FROM node:24-alpine AS build

WORKDIR /app

ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_DEFAULT_OLLAMA_ENDPOINT=http://127.0.0.1:11434
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_DEFAULT_OLLAMA_ENDPOINT=${VITE_DEFAULT_OLLAMA_ENDPOINT}

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html tsconfig.json vite.config.ts eslint.config.js ./
COPY src ./src

RUN npm run build

FROM nginx:1.29-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
