import re
from typing import Dict, Any, List, Set

class NREngine:
    def __init__(self):
        # Regex patterns for datasets, algorithms, metrics
        self.dataset_patterns = [
            re.compile(r"\b([A-Z][A-Za-z0-9\-]+(?:\s+[A-Z][A-Za-z0-9\-]+)*\s+(?:dataset|corpus|benchmark|database|dataset\s+version\s+\d+))\b"),
            re.compile(r"\b(?:ImageNet|CIFAR-10|CIFAR-100|MNIST|COCO|SST-2|CoLA|SQuAD|Glue|SuperGLUE|IMDb|WikiText|PASCAL\s+VOC|Kaggle\s+[A-Za-z0-9\-]+)\b", re.IGNORECASE),
            re.compile(r"\b(?:using|on|evaluating|with)\s+the\s+([A-Z][a-zA-Z0-9_\-]+)\s+data\b")
        ]
        
        self.algorithm_patterns = [
            re.compile(r"\b(?:BERT|GPT-3|GPT-4|Gemma|Llama|Qwen|Mistral|ResNet\-\d+|VGG\-\d+|LSTM|GRU|SVM|XGBoost|Random\s+Forest|Q?CNNs?|RNNs?|GNNs?|Transformers?|Autoencoder|DQN|PPO|A2C|K-Means|DBScan)\b"),
            re.compile(r"\b([A-Z][a-zA-Z0-9\-]+(?:\s+[A-Z][a-zA-Z0-9\-]+)*\s+(?:architecture|network|model|algorithm|classifier|regressor|framework))\b"),
            re.compile(r"\b(?:proposed|used|implemented)\s+the\s+([A-Z][a-zA-Z0-9_\-]+)\s+(?:approach|method|technique)\b")
        ]
        
        self.metric_patterns = [
            re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|percent|accuracy|F1|F1-score|recall|precision|AUC|ROC|mAP|BLEU|ROUGE|perplexity|MSE|RMSE|MAE)\b", re.IGNORECASE),
            re.compile(r"\b(?:accuracy|F1-score|recall|precision|mAP|BLEU)\s*(?:of|is|reached|was)\s*(\d+(?:\.\d+)?%?)\b", re.IGNORECASE)
        ]
        
        # Stopwords/junk words to filter from keywords
        self.stopwords = {
            "a", "an", "the", "and", "or", "but", "about", "above", "after", "along",
            "amid", "among", "as", "at", "by", "for", "from", "in", "into", "like",
            "minus", "near", "of", "off", "on", "onto", "out", "over", "past", "since",
            "through", "throughout", "to", "under", "until", "up", "upon", "with", "within",
            "without", "we", "our", "this", "paper", "study", "results", "method", "proposed"
        }

    def extract_entities(self, section_text: str) -> Dict[str, List[str]]:
        """Extracts datasets, algorithms, and metrics from text using patterns."""
        if not section_text:
            return {"datasets": [], "algorithms": [], "metrics": []}
            
        datasets: Set[str] = set()
        algorithms: Set[str] = set()
        metrics: Set[str] = set()
        
        # 1. Extract Datasets
        for pattern in self.dataset_patterns:
            matches = pattern.findall(section_text)
            for match in matches:
                # Handle group matches vs full matches
                val = match[0] if isinstance(match, tuple) else match
                val_clean = val.strip().strip(",.-() ")
                if len(val_clean) > 2 and val_clean.lower() not in ["the dataset", "a dataset", "our dataset", "this dataset"]:
                    datasets.add(val_clean)
                    
        # 2. Extract Algorithms / Models
        for pattern in self.algorithm_patterns:
            matches = pattern.findall(section_text)
            for match in matches:
                val = match[0] if isinstance(match, tuple) else match
                val_clean = val.strip().strip(",.-() ")
                if len(val_clean) > 2 and val_clean.lower() not in ["the model", "the algorithm", "our method", "this approach"]:
                    algorithms.add(val_clean)
                    
        # 3. Extract Metrics
        for pattern in self.metric_patterns:
            matches = pattern.findall(section_text)
            for match in matches:
                val = match[0] if isinstance(match, tuple) else match
                val_clean = val.strip().strip(",.-() ")
                if len(val_clean) > 1:
                    metrics.add(val_clean)
                    
        return {
            "datasets": sorted(list(datasets))[:8],
            "algorithms": sorted(list(algorithms))[:8],
            "metrics": sorted(list(metrics))[:8]
        }

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extracts top keywords using simple term-frequency/noun phrase heuristic."""
        if not text:
            return []
            
        # Standard cleaning
        words = re.findall(r"\b[a-zA-Z\-]{4,25}\b", text.lower())
        
        freq: Dict[str, int] = {}
        for word in words:
            if word in self.stopwords:
                continue
            freq[word] = freq.get(word, 0) + 1
            
        # Sort and return top candidates
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:max_keywords]]

    def analyze_paper_metadata(self, parsed_paper: Dict[str, str]) -> Dict[str, Any]:
        """Combines section structures and extracts all core entities and keywords."""
        # Focus dataset/algorithm extraction on Abstract, Methodology, and Results
        focus_text = f"{parsed_paper.get('abstract', '')} \n {parsed_paper.get('methodology', '')} \n {parsed_paper.get('results', '')}"
        
        entities = self.extract_entities(focus_text)
        keywords = self.extract_keywords(parsed_paper.get("abstract", "") + " " + parsed_paper.get("title", ""), max_keywords=8)
        
        return {
            "keywords": keywords,
            "datasets": entities["datasets"],
            "algorithms": entities["algorithms"],
            "metrics": entities["metrics"]
        }
