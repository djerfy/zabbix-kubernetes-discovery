FROM ubuntu:24.04

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
    apt-get install -y --no-install-recommends \
        curl \
        iputils-ping \
        python3 \
        python3-pip \
        python3-venv && \
    rm -rf /var/lib/apt/lists && \
    mkdir -p /app /root/.kube && \
    touch /app/crontab && \
    groupadd -g 2000 ${CONTAINER_GROUP} && \
    useradd -u 2000 -d /app -s /bin/bash -M -g ${CONTAINER_GROUP} ${CONTAINER_USER} && \
    python3 -m venv venv

ARG SUPERCRONIC_VER="0.2.31"
ARG SUPERCRONIC_SHA="fb4242e9d28528a76b70d878dbf69fe8d94ba7d2"

RUN curl -fsSLO "https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VER}/supercronic-linux-amd64" && \
    echo "${SUPERCRONIC_SHA}  supercronic-linux-amd64" | sha1sum -c - && \
    chmod +x supercronic-linux-amd64 && \
    mv supercronic-linux-amd64 /usr/local/bin/supercronic

COPY ./src/ /app/

RUN chown ${CONTAINER_USER}:${CONTAINER_GROUP} -R /app && \
    chmod +x /app/*.py && \
    /app/venv/bin/pip3 install --no-cache-dir -r /app/requirements.txt

USER ${CONTAINER_USER}:${CONTAINER_GROUP}

CMD ["/usr/local/bin/supercronic", "-split-logs", "-json", "/app/crontab"]
