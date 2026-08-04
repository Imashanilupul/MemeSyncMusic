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

export const processYouTube = (url) =>
  api.post("/youtube/process", {
    url,
  });

export const searchMeme = (lyrics) =>
  api.post("/meme/search", {
    lyrics,
  });

export const renderVideo = (payload) => api.post("/video/render", payload);

export default api;