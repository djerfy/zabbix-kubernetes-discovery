from kubernetes import client
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.statefulsets")

def kubernetesGetStatefulsets(config):
    """
    description: get statefulsets data
    return: list
    """
    kubernetes = client.AppsV1Api()

    statefulsets = []

    for statefulset in kubernetes.list_stateful_set_for_all_namespaces().items:

        json = {
            "name": statefulset.metadata.name,
            "namespace": statefulset.metadata.namespace,
            "replicas": {
                "available": statefulset.status.current_replicas,
                "ready": statefulset.status.ready_replicas,
                "desired": statefulset.status.replicas
            }
        }

        if statefulset.metadata:
            if statefulset.metadata.labels:
                if matchLabels(config['monitoring']['statefulsets']['labels']['exclude'], statefulset.metadata.labels):
                    continue
                if config['monitoring']['statefulsets']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['statefulsets']['labels']['include'], statefulset.metadata.labels):
                        continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if any(s['name'] == json['name'] and s['namespace'] == json['namespace'] for s in statefulsets):
            continue

        statefulsets.append(json)

    return statefulsets

def zabbixDiscoveryStatefulsets(config):
    """
    description: create a discovery for statefulset, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for statefulset in kubernetesGetStatefulsets(config):
        output = {
            "{#KUBERNETES_STATEFULSET_NAMESPACE}": statefulset['namespace'],
            "{#KUBERNETES_STATEFULSET_NAME}": statefulset['name']}
        discovery['data'].append(output)

    return [config['kubernetes']['name'], "kubernetes.statefulsets.discovery", json.dumps(discovery)]

def zabbixItemsStatefulsets(config):
    """
    description: create a item for statefulset, per namespace
    return: list
    """
    items = []

    for statefulset in kubernetesGetStatefulsets(config):
        items.append([config['kubernetes']['name'], f"kubernetes.statefulset.availableReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['available']])
        items.append([config['kubernetes']['name'], f"kubernetes.statefulset.readyReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['ready']])
        items.append([config['kubernetes']['name'], f"kubernetes.statefulset.desiredReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['desired']])

    return items
