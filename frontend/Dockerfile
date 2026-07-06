FROM nginx:1.27-alpine

RUN apk update && apk upgrade --no-cache

COPY static/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80