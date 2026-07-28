# Stage 1: Build React/Vite application
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY web/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source code
COPY web/frontend/ ./

# Build production bundle
RUN npm run build

# Stage 2: Production Nginx Server
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy static built assets from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY web/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
