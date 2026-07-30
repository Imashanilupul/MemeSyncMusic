import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

export const uploadMusic = (formData, onUploadProgress) =>
  api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });

export const getAnalysis = (jobId) => api.get(`/analyze/${jobId}`);

export default api;