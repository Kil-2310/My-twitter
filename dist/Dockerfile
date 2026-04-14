FROM nginx:alpine

COPY ./css /usr/share/nginx/html/css
COPY ./js /usr/share/nginx/html/js
COPY ./favicon.ico /usr/share/nginx/html/favicon.ico

COPY ./index.html /usr/share/nginx/html/index.html

COPY ./nginx_from_image.conf /etc/nginx/nginx.conf
