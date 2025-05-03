import { defineConfig } from 'vite';

// 简化vite配置以避免与tailwindcss处理冲突
export default defineConfig({
  root: './',
  build: {
    outDir: 'dist',
    minify: true,
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
}); 