import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://localhost:8000",
      "/people": "http://localhost:8000",
      "/relationships": "http://localhost:8000",
      "/tree": "http://localhost:8000",
      "/gedcom": "http://localhost:8000",
      "/admin": "http://localhost:8000",
      "/media": "http://localhost:8000",
      "/sources": "http://localhost:8000",
      "/uploads": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
