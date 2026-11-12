FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# L'image officielle remplace les ${VARIABLES} des fichiers *.template au démarrage.
ENV PORT=8080 BACKEND_URL=http://backend:8000 NGINX_ENVSUBST_FILTER="^(PORT|BACKEND_URL)$"
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
