FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for layer caching
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copy source and build
COPY . .
RUN npm run build

# Production: serve with nginx on port 80
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
