from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3, re, logging

urllib3.disable_warnings()

def kubernetesGetVolumes(config=None):
    """
    description: get volumes data
    return: list
    """
    kubernetes = client.CoreV1Api()

    volumes = []

    for node in kubernetes.list_node().items:
        if node.spec.taints is not None:
            if "node.kubernetes.io/not-ready" in str(node.spec.taints):
                continue

        node_info = kubernetes.connect_get_node_proxy_with_path(name=node.metadata.name, path="stats/summary").replace("'", "\"")
        node_json = json.loads(node_info)

        for pod in node_json['pods']:
            if not "volume" in pod:
                continue

            for volume in pod['volume']:

                if not "pvcRef" in volume:
                    continue

                if volume['pvcRef']['name'].startswith(pod['podRef']['name']) and re.match(r"(.*)-[a-z0-9]{8,10}-[a-z0-9]{5}$", pod['podRef']['name']):
                    continue

                volume['namespace'] = volume['pvcRef']['namespace']
                volume['name'] = volume['pvcRef']['name']

                if volume.get("metadata"):
                    if volume.metadata.get("labels"):
                        if matchLabels(config['labels']['exclude'], volume.metadata.labels):
                            continue
                        if config['labels']['include'] != []:
                            if not matchLabels(config['labels']['include'], volume.metadata.labels):
                                continue

                for i in ["time", "pvcRef"]:
                    del volume[i]

                if any(v['name'] == volume['name'] and v['namespace'] == volume['namespace'] for v in volumes):
                    continue
                
                if "-token-" in volume['name']:
                    continue

                volumes.append(volume)

    return volumes

def zabbixDiscoveryVolumes(clustername, volumes=[]):
    """
    description: create a discovery for persistent volume claim, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for volume in volumes:
        output = {
            "{#KUBERNETES_PVC_NAMESPACE}": volume['namespace'],
            "{#KUBERNETES_PVC_NAME}": volume['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.pvc.discovery", json.dumps(discovery))]

    return sender

def zabbixItemVolumes(clustername, volumes=[]):
    """
    description: create a item for persistent volume claim, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for volume in volumes: 
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.availableBytes[{volume['namespace']},{volume['name']}]", volume['availableBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.capacityBytes[{volume['namespace']},{volume['name']}]", volume['capacityBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.usedBytes[{volume['namespace']},{volume['name']}]", volume['usedBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodesFree[{volume['namespace']},{volume['name']}]", volume['inodesFree']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodes[{volume['namespace']},{volume['name']}]", volume['inodes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodesUsed[{volume['namespace']},{volume['name']}]", volume['inodesUsed']),)

    return sender

def baseVolumes(mode=None, config=None):
    """
    description: monitoring volumes
    return: class ZabbixMetric
    """
    if mode == "discovery":
        return zabbixDiscoveryVolumes(config['kubernetes']['name'], kubernetesGetVolumes(config['monitoring']['volumes']))
    if mode == "item":
        return zabbixItemVolumes(config['kubernetes']['name'], kubernetesGetVolumes(config['monitoring']['volumes']))
    return []
