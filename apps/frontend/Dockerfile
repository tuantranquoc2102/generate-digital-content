# apps/web/Dockerfile
# Stage deps
FROM node:20-alpine AS deps

WORKDIR /app

# Chỉ copy những file lock mà bạn thực sự có. 
# KHÔNG dùng '2>/dev/null || true' trong COPY.
# Nếu bạn dùng npm: giữ package.json + package-lock.json
COPY package.json ./

# Dùng npm mặc định (hoặc pnpm/yarn nếu bạn dùng)
RUN npm ci || npm install

# Stage build
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# build production (có thể chuyển sang dev nếu muốn hot reload trong container)
RUN npm run build

# 3 Stage runner
FROM node:20-alpine AS runner
WORKDIR /app

# đảm bảo luôn có thư mục public (kể cả rỗng)
RUN mkdir -p public

ENV NODE_ENV=production
# Next.js cần .next + node_modules (cho next start)
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs

# BỎ dòng COPY public gây lỗi
# COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm","run","start"]