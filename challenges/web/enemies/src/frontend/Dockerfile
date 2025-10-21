FROM node:22 AS builder
WORKDIR /opt/app
COPY package.json pnpm-lock.yaml ./
RUN npm install
COPY . ./
RUN npm run build
FROM nginx:1.29.1
RUN rm -rf /etc/nginx/conf.d/*
COPY nginx.conf /etc/nginx/conf.d/frontend.conf
RUN rm -rf /usr/share/nginx/html
COPY --from=builder /opt/app/dist /usr/share/nginx/html 
