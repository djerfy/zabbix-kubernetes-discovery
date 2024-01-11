from kubernetes import client
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.nodes")

def kubernetesGetNodes(config):
    """
    description: get nodes data
    return: list
    """
    kubernetes = client.CoreV1Api()

    nodes = []

    for node in kubernetes.list_node().items:
        node_healthz = kubernetes.connect_get_node_proxy_with_path(name=node.metadata.name, path="healthz")
        node_status  = kubernetes.read_node_status(name=node.metadata.name)
        node_pods    = kubernetes.list_pod_for_all_namespaces(field_selector="spec.nodeName={}".format(node.metadata.name))

        json = {
            "name": node.metadata.name,
            "uid": node.metadata.uid,
            "status": node_healthz,
            "capacity": node_status.status.capacity,
            "allocatable": node_status.status.allocatable,
            "current": {
                "pods": str(len(node_pods.items)),
                "pods_used": str(round(len(node_pods.items) * 100 / int(node_status.status.allocatable['pods']), 1)),
                "pods_free": str(round(100 - (len(node_pods.items) * 100 / int(node_status.status.allocatable['pods'])), 1))
            }
        }

        if hasattr(node, 'metadata'):
            if hasattr(node.metadata, 'labels'):
                if matchLabels(config['monitoring']['nodes']['labels']['exclude'], node.metadata.labels):
                    continue
                if config['monitoring']['nodes']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['nodes']['labels']['include'], node.metadata.labels):
                        continue

        if any(n['name'] == json['name'] for n in nodes):
            continue

        nodes.append(json)

    return nodes

def zabbixDiscoveryNodes(config):
    """
    description: create a discovery for node
    return: dict
    """
    discovery = {"data":[]}

    for node in kubernetesGetNodes(config):
        output = {"{#KUBERNETES_NODE_NAME}": node['name']}
        discovery['data'].append(output)

    return [[config['kubernetes']['name'], "kubernetes.nodes.discovery", json.dumps(discovery)]]

def zabbixItemsNodes(config):
    """
    description: create a item for node
    return: list
    """
    items = []

    for node in kubernetesGetNodes(config):
        items.append([config['kubernetes']['name'], f"kubernetes.node.healthz[{node['name']}]", node['status']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.capacity.cpu[{node['name']}]", node['capacity']['cpu']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.capacity.memory[{node['name']}]", node['capacity']['memory']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.capacity.pods[{node['name']}]", node['capacity']['pods']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.allocatable.cpu[{node['name']}]", node['allocatable']['cpu']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.allocatable.memory[{node['name']}]", node['allocatable']['memory']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.allocatable.pods[{node['name']}]", node['allocatable']['pods']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.current.pods[{node['name']}]", node['current']['pods']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.current.podsUsed[{node['name']}]", node['current']['pods_used']])
        items.append([config['kubernetes']['name'], f"kubernetes.node.current.podsFree[{node['name']}]", node['current']['pods_free']])

    return items
