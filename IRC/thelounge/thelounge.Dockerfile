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

COPY source/client/components/MessageTypes/join.vue /app/thelounge/client/components/MessageTypes/join.vue

COPY source/client/components/MessageTypes/part.vue /app/thelounge/client/components/MessageTypes/part.vue

COPY source/client/components/MessageTypes/quit.vue /app/thelounge/client/components/MessageTypes/quit.vue

COPY source/client/components/MessageTypes/whois.vue /app/thelounge/client/components/MessageTypes/whois.vue

COPY source/client/thelounge.webmanifest /app/thelounge/client/thelounge.webmanifest

COPY source/server/identification.ts /app/thelounge/server/identification.ts

COPY source/client/components/Settings/General.vue /app/thelounge/client/components/Settings/General.vue

COPY source/client/components/Windows/Help.vue /app/thelounge/client/components/Windows/Help.vue

COPY source/client/js/socket-events/connection.ts /app/thelounge/client/js/socket-events/connection.ts

#COPY source/server/server.ts /app/thelounge/server/server.ts

#OPY source/server/plugins/clientCertificate.ts /app/thelounge/server/plugins/clientCertificate.ts

#COPY source/server/config.ts /app/thelounge/server/config.ts

#COPY source/server/models/network.ts /app/thelounge/server/models/network.ts

COPY source/client/components/MessageSearchForm.vue /app/thelounge/client/components/MessageSearchForm.vue

COPY source/client/components/Chat.vue /app/thelounge/client/components/Chat.vue

#COPY ./server.ts /app/thelounge/server/server.ts

RUN sed -i 's/pingTimeout: 60000,/pingTimeout: 600000,/' /app/thelounge/server/server.ts
RUN sed -i 's/log\.info(`The Lounge \${colors\.green(Helper\.getVersion())}/log\.info(`Nightwatch version: \${colors\.green(Helper\.getVersion())}/' /app/thelounge/server/server.ts
RUN sed -i 's/title: "The Lounge",/title: "Nightwatch",/' /app/thelounge/server/server.ts
RUN sed -i 's/value: "The Lounge IRC Client",/value: "Nightwatch IRC Client",/' /app/thelounge/server/plugins/clientCertificate.ts
RUN sed -i 's/return "thelounge";/return "nightwatch";/' /app/thelounge/server/config.ts
RUN sed -i 's/this\.username = cleanString(this\.username) || "thelounge";/this\.username = cleanString(this\.username) || "nightwatch";/' /app/thelounge/server/models/network.ts
RUN sed -i 's/username: "thelounge",/username: "nightwatch",/' /app/thelounge/server/models/network.ts

WORKDIR /app/thelounge/

RUN yarn install

RUN yarn build
