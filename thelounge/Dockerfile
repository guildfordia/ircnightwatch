FROM lscr.io/linuxserver/thelounge:latest

COPY ./components/NetworkForm.vue /app/thelounge/client/components/NetworkForm.vue

COPY ./components/App.vue /app/thelounge/client/components/App.vue

COPY ./components/Sidebar.vue /app/thelounge/client/components/Sidebar.vue

COPY ./index.html.tpl /app/thelounge/client/index.html.tpl

#COPY ./server.ts /app/thelounge/server/server.ts
RUN sed -i 's/pingTimeout: 60000,/pingTimeout: 600000,/' /app/thelounge/server/server.ts

WORKDIR /app/thelounge/

RUN yarn install

RUN yarn build