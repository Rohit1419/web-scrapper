import axios from "axios";
import { API_BASE_URL } from "./constant";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const apiService = {
  getCourts: async () => {
    const response = await api.get("/api/courts");
    return response.data;
  },

  startScraping: async (scrapeData) => {
    const response = await api.post("/api/scrape/start", scrapeData);
    return response.data;
  },

  getStatus: async (sessionId) => {
    const response = await api.get(`/api/scrape/status/${sessionId}`);
    return response.data;
  },

  confirmCaptcha: async (sessionId) => {
    const response = await api.post(`/api/scrape/captcha-solved/${sessionId}`);
    return response.data;
  },

  cancelSession: async (sessionId) => {
    const response = await api.delete(`/api/scrape/${sessionId}`);
    return response.data;
  },

  getDownloadUrl: (pdfUrl) => {
    return `${API_BASE_URL}${pdfUrl}`;
  },
};
