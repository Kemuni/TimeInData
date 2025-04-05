FROM node:18-alpine AS builder

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY package.json package-lock.json ./
RUN npm ci

# Копируем исходный код
COPY . .

# Собираем проект
RUN npm run build

# Финальный образ
FROM node:18-alpine AS runner

WORKDIR /app

# Копируем только необходимые файлы
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Опционально: если нужны другие файлы (например, серверный рендеринг)
# COPY --from=builder /app/server.js ./server.js

# Пользователь без root-прав (для безопасности)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
USER nextjs

# Переменные среды
ENV PORT=3000
ENV HOST=0.0.0.0
ENV NODE_ENV=production

# Запуск сервера Vite (или своего сервера, если есть server.js)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000", "--debug"]