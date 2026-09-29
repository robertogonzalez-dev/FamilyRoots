import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const API = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Same contract as nginx.conf and vercel.json: /api/* is forwarded with the prefix stripped.
      "/api": { target: API, changeOrigin: true, rewrite: (path) => path.replace(/^\/api/, "") },
      // Uploaded photos are served by the backend at /uploads/*.
      "/uploads": API,
    },
  },
});
