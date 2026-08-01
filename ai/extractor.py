import re
import os
from typing import Dict, Any, List, Tuple
import fitz  # PyMuPDF
import pdfplumber

class PDFExtractor:
    def __init__(self):
        # Regular expressions for common paper headers
        self.headers_regex = {
            "abstract": re.compile(r"^\s*(?:abstract)\s*$", re.IGNORECASE),
            "introduction": re.compile(r"^\s*(?:\d+\.?\s+)?(?:introduction)\s*$", re.IGNORECASE),
            "methodology": re.compile(r"^\s*(?:\d+\.?\s+)?(?:methodology|proposed\s+(?:method|system|framework|approach|model)|methods|system\s+design)\s*$", re.IGNORECASE),
            "results": re.compile(r"^\s*(?:\d+\.?\s+)?(?:results|evaluation|experiments|experimental\s+(?:setup|results|evaluation))\s*$", re.IGNORECASE),
            "limitations": re.compile(r"^\s*(?:limitations|discussion|threats\s+to\s+validity)\s*$", re.IGNORECASE),
            "future_work": re.compile(r"^\s*(?:future\s+work|future\s+directions|future\s+scope)\s*$", re.IGNORECASE),
            "conclusion": re.compile(r"^\s*(?:\d+\.?\s+)?(?:conclusion|conclusions|concluding\s+remarks)\s*$", re.IGNORECASE),
            "references": re.compile(r"^\s*(?:references|bibliography)\s*$", re.IGNORECASE)
        }

    def clean_text(self, text: str) -> str:
        """Cleans common PDF text anomalies such as ligatures and duplicate spacing."""
        if not text:
            return ""
        # Fix ligatures
        replacements = {
            "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
            "–": "-", "—": "-"
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        
        # Remove consecutive spacing and soft hyphens at line endings
        text = re.sub(r"-\n\s*", "", text)
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def extract_raw_text(self, pdf_path: str) -> Tuple[str, List[str]]:
        """Extracts raw text from PDF. Returns (full_text, list_of_pages)."""
        full_text = ""
        pages_text = []
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
            
        try:
            # Try PyMuPDF first (highly performant)
            doc = fitz.open(pdf_path)
            for page in doc:
                text = page.get_text("text")
                pages_text.append(text)
                full_text += text + "\n---PAGE_BREAK---\n"
            doc.close()
        except Exception as e:
            # Fallback to pdfplumber
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        pages_text.append(text)
                        full_text += text + "\n---PAGE_BREAK---\n"
            except Exception as ex:
                raise RuntimeError(f"Failed to parse PDF using both fitz and pdfplumber: {ex}")
                
        return full_text, pages_text

    def parse_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Parses the PDF and classifies text blocks into standard sections."""
        full_text, pages_text = self.extract_raw_text(pdf_path)
        
        # Try to extract Title and Authors from the first page
        title, authors = self.extract_first_page_metadata(pages_text[0] if pages_text else "")
        
        # Segment full text by sections
        sections = self.segment_sections(full_text)
        
        # Refine missing sections by searching matching keywords in paragraphs
        if not sections.get("limitations"):
            sections["limitations"] = self.find_paragraphs_with_keywords(full_text, ["limitation", "drawback", "shortcoming", "weakness"])
            
        if not sections.get("future_work"):
            sections["future_work"] = self.find_paragraphs_with_keywords(full_text, ["future work", "future scope", "future directions", "plan to extend"])

        # Construct final dict
        return {
            "title": title,
            "authors": authors,
            "abstract": self.clean_text(sections.get("abstract", "")),
            "methodology": self.clean_text(sections.get("methodology", "")),
            "results": self.clean_text(sections.get("results", "")),
            "limitations": self.clean_text(sections.get("limitations", "")),
            "future_work": self.clean_text(sections.get("future_work", "")),
            "conclusion": self.clean_text(sections.get("conclusion", "")),
            "references": self.clean_text(sections.get("references", "")),
            "raw_text": full_text
        }

    def extract_first_page_metadata(self, first_page_text: str) -> Tuple[str, str]:
        """Extracts title and authors from the first page using layout heuristics."""
        if not first_page_text:
            return "Untitled Paper", "Unknown Authors"
            
        lines = [line.strip() for line in first_page_text.split("\n") if line.strip()]
        
        # The title is usually in the first 5 lines (skipping headers like IEEE/ACM placeholders)
        title_candidates = []
        for line in lines[:8]:
            # Skip conference/journal metadata headers
            if any(h in line.lower() for h in ["proceeding", "vol.", "no.", "copyright", "isbn", "http", "journal", "ieee", "acm"]):
                continue
            title_candidates.append(line)
            if len(title_candidates) >= 3:
                break
                
        title = " ".join(title_candidates) if title_candidates else "Untitled Paper"
        title = re.sub(r"\s+", " ", title).strip()
        
        # Extract authors - lines following the title
        author_candidates = []
        title_index = -1
        for i, line in enumerate(lines):
            if title_candidates and title_candidates[0] in line:
                title_index = i
                break
                
        start_idx = title_index + len(title_candidates) if title_index != -1 else 3
        for line in lines[start_idx:start_idx+4]:
            if any(x in line.lower() for x in ["abstract", "introduction", "email", "university", "department", "school"]):
                break
            author_candidates.append(line)
            
        authors = ", ".join(author_candidates) if author_candidates else "Unknown Authors"
        authors = re.sub(r"\s+", " ", authors).strip()
        
        # Truncate if title or authors look too long
        if len(title) > 250:
            title = title[:247] + "..."
        if len(authors) > 300:
            authors = authors[:297] + "..."
            
        return title, authors

    def segment_sections(self, full_text: str) -> Dict[str, str]:
        """Segments text into sections based on recognized headers."""
        lines = full_text.split("\n")
        sections: Dict[str, List[str]] = {}
        current_section = None
        
        for line in lines:
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
                
            # Check if this line is a heading
            matched_header = None
            for sec_name, pattern in self.headers_regex.items():
                if pattern.match(cleaned_line):
                    matched_header = sec_name
                    break
                    
            if matched_header:
                current_section = matched_header
                if current_section not in sections:
                    sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)
                
        return {k: "\n".join(v) for k, v in sections.items()}

    def find_paragraphs_with_keywords(self, text: str, keywords: List[str]) -> str:
        """Finds and groups paragraphs containing specified keywords."""
        paragraphs = text.split("\n\n")
        matching_paragraphs = []
        
        for para in paragraphs:
            para_clean = para.replace("\n", " ").strip()
            if not para_clean:
                continue
            if any(keyword in para_clean.lower() for keyword in keywords):
                matching_paragraphs.append(para_clean)
                
        return "\n\n".join(matching_paragraphs[:5])  # Return top 5 matches
