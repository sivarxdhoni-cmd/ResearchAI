const isLocal = 
  window.location.hostname === "localhost" || 
  window.location.hostname === "127.0.0.1" || 
  window.location.port !== "" ||
  window.location.protocol === "file:";

const BASE_URL = import.meta.env.VITE_API_URL || (isLocal 
  ? `http://${window.location.hostname || "localhost"}:8000/api/v1` 
  : "/api/v1");

// Helper to inject JWT token in Authorization Header
const getHeaders = (isMultipart = false) => {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {};
  if (!isMultipart) {
    headers["Content-Type"] = "application/json";
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async (res: Response) => {
  if (!res.ok) {
    let errorMsg = "API request failed";
    try {
      const data = await res.json();
      errorMsg = data.detail || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  if (res.status === 204) return null;
  return res.json();
};

export const api = {
  // Authentication
  login: async (email: string, pass: string) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", pass);
    
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData.toString()
    });
    const data = await handleResponse(res);
    localStorage.setItem("token", data.access_token);
    return data;
  },

  register: async (email: string, pass: string, fullName: string, role: string) => {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ email, password: pass, full_name: fullName, role })
    });
    return handleResponse(res);
  },

  getMe: async () => {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  logout: () => {
    localStorage.removeItem("token");
  },

  // Papers CRUD
  getPapers: async (statusFilter?: string) => {
    const url = statusFilter ? `${BASE_URL}/papers/?status=${statusFilter}` : `${BASE_URL}/papers/`;
    const res = await fetch(url, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  getPaper: async (id: number) => {
    const res = await fetch(`${BASE_URL}/papers/${id}`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  deletePaper: async (id: number) => {
    const res = await fetch(`${BASE_URL}/papers/${id}`, {
      method: "DELETE",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  uploadPaper: async (file: File, metadata?: { publication_year?: number; conference_journal?: string; doi?: string; arxiv_url?: string }) => {
    const formData = new FormData();
    formData.append("file", file);
    if (metadata) {
      if (metadata.publication_year) formData.append("publication_year", String(metadata.publication_year));
      if (metadata.conference_journal) formData.append("conference_journal", metadata.conference_journal);
      if (metadata.doi) formData.append("doi", metadata.doi);
      if (metadata.arxiv_url) formData.append("arxiv_url", metadata.arxiv_url);
    }

    const res = await fetch(`${BASE_URL}/papers/upload`, {
      method: "POST",
      headers: getHeaders(true),
      body: formData
    });
    return handleResponse(res);
  },

  comparePapers: async (paperIds: number[]) => {
    const res = await fetch(`${BASE_URL}/papers/compare`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ paper_ids: paperIds })
    });
    return handleResponse(res);
  },

  // RAG Chat Assistant
  askAssistant: async (message: string) => {
    const res = await fetch(`${BASE_URL}/chat/`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ message })
    });
    return handleResponse(res);
  },

  getChatHistory: async () => {
    const res = await fetch(`${BASE_URL}/chat/history`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  // Research Gap & Review Engine
  getGaps: async () => {
    const res = await fetch(`${BASE_URL}/gaps/`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  getIdeas: async () => {
    const res = await fetch(`${BASE_URL}/gaps/ideas`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  scanGaps: async (topicId: number) => {
    const res = await fetch(`${BASE_URL}/gaps/scan/${topicId}`, {
      method: "POST",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  generateLiteratureReview: async (topicName: string) => {
    const res = await fetch(`${BASE_URL}/gaps/literature-review`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ topic_name: topicName })
    });
    return handleResponse(res);
  },

  // Dashboard Stats & Visualizer
  getDashboardStats: async () => {
    const res = await fetch(`${BASE_URL}/dashboard/stats`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  },

  getGraphData: async () => {
    const res = await fetch(`${BASE_URL}/dashboard/graph`, {
      method: "GET",
      headers: getHeaders()
    });
    return handleResponse(res);
  }
};
