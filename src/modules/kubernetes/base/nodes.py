from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.nodes")

def kubernetesGetNodes(config=None):
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

        if matchLabels(config['labels']['exclude'], node.metadata.labels):
            continue

        if config['labels']['include'] != []:
            if not matchLabels(config['labels']['include'], node.metadata.labels):
                continue

        if any(n['name'] == json['name'] for n in nodes):
            continue

        nodes.append(json)

    return nodes

def zabbixDiscoveryNodes(clustername, nodes=[]):
    """
    description: create a discovery for node
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for node in nodes:
        output = {"{#KUBERNETES_NODE_NAME}": node['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.node.discovery", json.dumps(discovery))]

    return sender

def zabbixItemNodes(clustername, nodes=[]):
    """
    description: create a item for node
    return: class ZabbixMetric
    """
    sender = []

    for node in nodes:
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.healthz[{node['name']}]", node['status']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.cpu[{node['name']}]", node['capacity']['cpu']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.memory[{node['name']}]", node['capacity']['memory']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.pods[{node['name']}]", node['capacity']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.cpu[{node['name']}]", node['allocatable']['cpu']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.memory[{node['name']}]", node['allocatable']['memory']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.pods[{node['name']}]", node['allocatable']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.pods[{node['name']}]", node['current']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.podsUsed[{node['name']}]", node['current']['pods_used']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.podsFree[{node['name']}]", node['current']['pods_free']),)

    return sender

def baseNodes(mode=None, config=None):
    """
    description: monitoring nodes
    return: class ZabbixMetric
    """
    logging.info(f"Function baseNodes() executed: {mode}")
    if mode == "discovery":
        return zabbixDiscoveryNodes(config['kubernetes']['name'], kubernetesGetNodes(config['monitoring']['nodes']))
    if mode == "item":
        return zabbixItemNodes(config['kubernetes']['name'], kubernetesGetNodes(config['monitoring']['nodes']))
    return []
