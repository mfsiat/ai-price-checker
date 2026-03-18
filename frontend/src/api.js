import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export const getProviders = () => API.get("/providers");

export const calculatePrice = (data) =>
  API.post("/calculate", data);

export const getFilteredModels = (params) =>
  API.get("/models", { params });