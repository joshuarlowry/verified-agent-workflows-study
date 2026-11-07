import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev UI server. The Hono API runs separately on :4310 ("npm run dev:api")
// and /api requests are proxied so the browser sees a single origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:4310",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
