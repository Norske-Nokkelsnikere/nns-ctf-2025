import { defineConfig } from "vite";
export default defineConfig({
    mode: "mpa",
    build: {
        rollupOptions: {
            input: {
                "index": "index.html",
                "message": "message.html"
            }
        }
    }
});