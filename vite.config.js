import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import * as path from 'path';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export default defineConfig({
    plugins: [react()],
    root: 'client',
    build: {
        outDir: 'dist'
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://localhost:8080',
                changeOrigin: true
            },
            '/socket.io': {
                target: 'http://localhost:8080',
                changeOrigin: true,
                ws: true
            }
        }
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './client/src')
        }
    }
});
