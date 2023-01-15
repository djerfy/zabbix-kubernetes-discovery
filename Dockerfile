FROM ubuntu:22.04

LABEL description="Zabbix Kubernetes Discovery" \
      maintainer="DJΞRFY <djerfy@gmail.com>" \
      repository="https://github.com/djerfy/zabbix-kubernetes-discovery"

WORKDIR /app

ENV ZABBIX_ENDPOINT=""
ENV KUBERNETES_NAME=""

ARG CONTAINER_USER="zabbix"
ARG CONTAINER_GROUP="zabbix"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl iputils-ping python3 python3-pip && \
    rm -rf /var/lib/apt/lists && \
    mkdir -p /app /root/.kube && \
    touch /app/crontab && \
    groupadd -g 2000 ${CONTAINER_GROUP} && \
    useradd -u 2000 -d /app -s /bin/bash -M -g ${CONTAINER_GROUP} ${CONTAINER_USER}

ARG SUPERCRONIC_VER="0.2.1"
ARG SUPERCRONIC_SHA="d7f4c0886eb85249ad05ed592902fa6865bb9d70"

RUN curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VER}/supercronic-linux-amd64" && \
    echo "${SUPERCRONIC_SHA}  supercronic-linux-amd64" | sha1sum -c - && \
    chmod +x supercronic-linux-amd64 && \
    mv supercronic-linux-amd64 /usr/local/bin/supercronic

COPY ./src/ /app/

RUN chown ${CONTAINER_USER}:${CONTAINER_GROUP} -R /app && \
    chmod +x /app/*.py && \
    pip3 install --no-cache-dir -r /app/requirements.txt

USER ${CONTAINER_USER}:${CONTAINER_GROUP}

CMD ["/usr/local/bin/supercronic", "-split-logs", "-json", "/app/crontab"]
