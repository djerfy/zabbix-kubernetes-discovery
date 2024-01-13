FROM ubuntu:22.04

LABEL description="Zabbix Kubernetes Discovery" \
      maintainer="DJΞRFY <djerfy@gmail.com>" \
      repository="https://github.com/djerfy/zabbix-kubernetes-discovery"

WORKDIR /app

ARG CONTAINER_USER="zabbix"
ARG CONTAINER_GROUP="zabbix"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends curl iputils-ping python3 python3-pip && \
    rm -rf /var/lib/apt/lists && \
    mkdir -p /app /root/.kube && \
    groupadd -g 2000 ${CONTAINER_GROUP} && \
    useradd -u 2000 -d /app -s /bin/bash -M -g ${CONTAINER_GROUP} ${CONTAINER_USER}

COPY ./src/ /app/

RUN chown ${CONTAINER_USER}:${CONTAINER_GROUP} -R /app && \
    chmod +x /app/*.py && \
    pip3 install --no-cache-dir -r /app/requirements.txt

USER ${CONTAINER_USER}:${CONTAINER_GROUP}

CMD ["/usr/bin/python3", "/app/zabbix-kubernetes-discovery.py"]
