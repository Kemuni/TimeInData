import {baseURL} from "@/services/api-urls.ts";
import axios, {AxiosInstance} from "axios";

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});