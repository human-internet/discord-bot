FROM node:alpine3.11
RUN mkdir -p /app
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
EXPOSE $PORT
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=$PORT
ENV PROXY_API=$PROXY_API
ENV PROXY_LOGIN=$PROXY_LOGIN
CMD [ "npm", "start" ]
