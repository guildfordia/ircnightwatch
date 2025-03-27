FROM debian:bullseye

RUN apt-get update && apt-get install -y \
    iproute2 iw wireless-tools net-tools batctl \
 && apt-get clean

COPY mesh-start.sh /usr/local/bin/mesh-start.sh
RUN chmod +x /usr/local/bin/mesh-start.sh

CMD ["/usr/local/bin/mesh-start.sh"]
