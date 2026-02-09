import axios from "axios";

// GANTI localhost DENGAN LINK KOYEB KAMU:
export const BASE_URL = "https://defeated-marya-farrel2008-b39f2824.koyeb.app"; 

export const api = axios.create({
  baseURL: BASE_URL,
});

// ... sisanya sama