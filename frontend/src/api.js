import axios from "axios";

const API = axios.create({
  baseURL: "/api",   // ✅ must use this (nginx proxy)
});

export const getProviders = () => API.get("/providers");

export const calculatePrice = (data) =>
  API.post("/calculate", data);