FROM nginx:1.21

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx
COPY site.conf /etc/nginx/conf.d
