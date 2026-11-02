import axios from "axios";

// The backend runs on Render's free tier and can cold-start (~50s) after idle,
// so allow a generous timeout before treating a request as failed.
const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://127.0.0.1:8000",
  timeout: 60000,
});

export const getProviders = () => API.get("/providers");

export const calculatePrice = (data) =>
  API.post("/calculate", data);

export const getFilteredModels = (params) =>
  API.get("/models", { params });