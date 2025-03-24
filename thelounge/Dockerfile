FROM lscr.io/linuxserver/thelounge:latest

COPY source/client/components/NetworkForm.vue /app/thelounge/client/components/NetworkForm.vue

COPY source/client/components/App.vue /app/thelounge/client/components/App.vue

COPY source/client/components/Sidebar.vue /app/thelounge/client/components/Sidebar.vue

COPY source/index.html.tpl /app/thelounge/client/index.html.tpl

COPY source/client/js/socket-events/msg.ts /app/thelounge/client/js/socket-events/msg.ts

COPY source/shared/types /app/thelounge/shared/types

COPY assets/theodore.jpg /app/thelounge/public/img/theodore.jpg

COPY source/client/css/style.css /app/thelounge/client/css/style.css

COPY source/client/css/style.css /app/thelounge/public/css/style.css

COPY source/client/css/style.css /app/thelounge/client/css/style.css

COPY source/client/components/MessageTypes/join.vue /app/thelouge/client/components/MessageTypes/join.vue

#COPY source/client/components/MessageSearchForm.vue /app/thelounge/client/components/MessageSearchForm.vue

#COPY source/client/components/Chat.vue /app/thelounge/client/components/Chat.vue

#COPY ./server.ts /app/thelounge/server/server.ts

RUN sed -i 's/pingTimeout: 60000,/pingTimeout: 600000,/' /app/thelounge/server/server.ts

WORKDIR /app/thelounge/

RUN yarn install

RUN yarn build