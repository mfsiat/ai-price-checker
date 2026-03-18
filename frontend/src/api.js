import axios from "axios";

const API = axios.create({
  baseURL: "http://backend:8000"
});

export const getProviders = () => API.get("/providers");

export const calculatePrice = (data) =>
  API.post("/calculate", data);

export const getFilteredModels = (params) =>
  API.get("/models", { params });
