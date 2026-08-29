import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
  server: {
    // Lets the dev server answer through an ngrok tunnel (free-tier
    // subdomains are random each run, hence the wildcard) — Vite blocks
    // unrecognized Host headers by default to guard against DNS
    // rebinding. Dev-server only; has no effect on the production build.
    allowedHosts: [".ngrok-free.dev", ".ngrok-free.app"],
  },
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg"],
      manifest: {
        name: "Isobar — market weather",
        short_name: "Isobar",
        description: "A monthly weather report for global markets, built from ETFs and country indices.",
        theme_color: "#161826",
        background_color: "#161826",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
          { src: "/icons/icon-512-maskable.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
        ],
      },
      workbox: {
        // App-shell + the generated data JSON precache so the last-fetched
        // month still renders offline; the shell itself is what makes this
        // installable, not just "has some caching".
        globPatterns: ["**/*.{js,css,html,svg,png,ico}"],
      },
    }),
  ],
});
