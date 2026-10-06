// vite.config.js
import { defineConfig } from "file:///D:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/frontend/node_modules/vite/dist/node/index.js";
import react from "file:///D:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/frontend/node_modules/@vitejs/plugin-react/dist/index.js";
import tailwindcss from "file:///D:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/frontend/node_modules/@tailwindcss/vite/dist/index.mjs";
import { reticle } from "file:///D:/CipherTECH/Projects/AI-Classroom-Intelligent-System/vista/frontend/node_modules/@reticlehq/vite-plugin/dist/index.js";
var vite_config_default = defineConfig({
  plugins: [reticle({ port: 4460 }), react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8002",
        changeOrigin: true
      },
      "/ws": {
        target: "http://127.0.0.1:8002",
        ws: true
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxDaXBoZXJURUNIXFxcXFByb2plY3RzXFxcXEFJLUNsYXNzcm9vbS1JbnRlbGxpZ2VudC1TeXN0ZW1cXFxcdmlzdGFcXFxcZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXENpcGhlclRFQ0hcXFxcUHJvamVjdHNcXFxcQUktQ2xhc3Nyb29tLUludGVsbGlnZW50LVN5c3RlbVxcXFx2aXN0YVxcXFxmcm9udGVuZFxcXFx2aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovQ2lwaGVyVEVDSC9Qcm9qZWN0cy9BSS1DbGFzc3Jvb20tSW50ZWxsaWdlbnQtU3lzdGVtL3Zpc3RhL2Zyb250ZW5kL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSc7XHJcbmltcG9ydCByZWFjdCBmcm9tICdAdml0ZWpzL3BsdWdpbi1yZWFjdCc7XHJcbmltcG9ydCB0YWlsd2luZGNzcyBmcm9tICdAdGFpbHdpbmRjc3Mvdml0ZSc7XHJcblxyXG5pbXBvcnQgeyByZXRpY2xlIH0gZnJvbSAnQHJldGljbGVocS92aXRlLXBsdWdpbic7XG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xyXG4gIHBsdWdpbnM6IFtyZXRpY2xlKHsgcG9ydDogNDQ2MCB9KSwgcmVhY3QoKSwgdGFpbHdpbmRjc3MoKV0sXHJcbiAgc2VydmVyOiB7XHJcbiAgICBwb3J0OiA1MTczLFxyXG4gICAgcHJveHk6IHtcclxuICAgICAgJy9hcGknOiB7XHJcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovLzEyNy4wLjAuMTo4MDAyJyxcclxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXHJcbiAgICAgIH0sXHJcbiAgICAgICcvd3MnOiB7XHJcbiAgICAgICAgdGFyZ2V0OiAnaHR0cDovLzEyNy4wLjAuMTo4MDAyJyxcclxuICAgICAgICB3czogdHJ1ZSxcclxuICAgICAgfSxcclxuICAgIH0sXHJcbiAgfSxcclxufSk7XHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBNlksU0FBUyxvQkFBb0I7QUFDMWEsT0FBTyxXQUFXO0FBQ2xCLE9BQU8saUJBQWlCO0FBRXhCLFNBQVMsZUFBZTtBQUN4QixJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsUUFBUSxFQUFFLE1BQU0sS0FBSyxDQUFDLEdBQUcsTUFBTSxHQUFHLFlBQVksQ0FBQztBQUFBLEVBQ3pELFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLE1BQ0EsT0FBTztBQUFBLFFBQ0wsUUFBUTtBQUFBLFFBQ1IsSUFBSTtBQUFBLE1BQ047QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
