from kubernetes import client
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.daemonsets")

def kubernetesGetDaemonsets(config):
    """
    description: get daemonsets data
    return: list
    """
    kubernetes = client.AppsV1Api()

    daemonsets = []

    for daemonset in kubernetes.list_daemon_set_for_all_namespaces().items:

        json = {
            "name": daemonset.metadata.name,
            "namespace": daemonset.metadata.namespace,
            "replicas": {
                "desired": daemonset.status.desired_number_scheduled,
                "current": daemonset.status.current_number_scheduled,
                "available": daemonset.status.number_available,
                "ready": daemonset.status.number_ready
            }
        }

        for i in ["desired", "current", "available", "ready"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if hasattr(daemonset, 'metadata'):
            if hasattr(daemonset.metadata, 'labels'):
                if matchLabels(config['monitoring']['daemonsets']['labels']['exclude'], daemonset.metadata.labels):
                    continue
                if config['monitoring']['daemonsets']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['daemonsets']['labels']['include'], daemonset.metadata.labels):
                        continue

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in daemonsets):
            continue

        daemonsets.append(json)

    return daemonsets

def zabbixDiscoveryDaemonsets(config):
    """
    description: create a discovery for daemonset, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for daemonset in kubernetesGetDaemonsets(config):
        output = {
            "{#KUBERNETES_BASE_DAEMONSETS_NAMESPACE}": daemonset['namespace'],
            "{#KUBERNETES_BASE_DAEMONSETS_NAME}": daemonset['name']}
        discovery['data'].append(output)

    return [[config['kubernetes']['name'], "kubernetes.base.daemonsets.discovery", json.dumps(discovery)]]

def zabbixItemsDaemonsets(config):
    """
    description: create a item for daemonset, per namespace
    return: list
    """
    items = []

    for daemonset in kubernetesGetDaemonsets(config):
        items.append([config['kubernetes']['name'], f"kubernetes.base.daemonsets.desiredReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['desired']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.daemonsets.currentReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['current']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.daemonsets.availableReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['available']])
        items.append([config['kubernetes']['name'], f"kubernetes.base.daemonsets.readyReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['ready']])

    return items
