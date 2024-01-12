from kubernetes import client
from modules.common.functions import *
import json, urllib3, re, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.volumes")

def kubernetesGetVolumes(config):
    """
    description: get volumes data
    return: list
    """
    kubernetes = client.CoreV1Api()

    volumes = []

    for node in kubernetes.list_node().items:
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

                if hasattr(volume, 'metadata'):
                    if hasattr(volume.metadata, 'labels'):
                        if matchLabels(config['monitoring']['volumes']['labels']['exclude'], volume.metadata.labels):
                            continue
                        if config['monitoring']['volumes']['labels']['include'] != []:
                            if not matchLabels(config['monitoring']['volumes']['labels']['include'], volume.metadata.labels):
                                continue

                for i in ["time", "pvcRef"]:
                    del volume[i]

                if any(v['name'] == volume['name'] and v['namespace'] == volume['namespace'] for v in volumes):
                    continue
                
                if "-token-" in volume['name']:
                    continue

                volumes.append(volume)

    return volumes

def zabbixDiscoveryVolumes(config):
    """
    description: create a discovery for persistent volume claim, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for volume in kubernetesGetVolumes(config):
        output = {
            "{#KUBERNETES_BASE_VOLUMES_NAMESPACE}": volume['namespace'],
            "{#KUBERNETES_BASE_VOLUMES_NAME}": volume['name']}
        discovery['data'].append(output)

    return [[config['kubernetes']['name'], "kubernetes.base.volumes.discovery", json.dumps(discovery)]]

def zabbixItemsVolumes(config):
    """
    description: create a item for persistent volume claim, per namespace
    return: list
    """
    items = []

    for volume in kubernetesGetVolumes(config): 
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.availableBytes[{volume['namespace']},{volume['name']}]", volume['availableBytes']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.capacityBytes[{volume['namespace']},{volume['name']}]", volume['capacityBytes']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.usedBytes[{volume['namespace']},{volume['name']}]", volume['usedBytes']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.inodesFree[{volume['namespace']},{volume['name']}]", volume['inodesFree']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.inodes[{volume['namespace']},{volume['name']}]", volume['inodes']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.volumes.inodesUsed[{volume['namespace']},{volume['name']}]", volume['inodesUsed']])

    return items
