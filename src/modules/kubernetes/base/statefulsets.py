from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3

urllib3.disable_warnings()

def kubernetesGetStatefulsets(config=None):
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

        if matchLabels(config['labels']['exclude'], statefulset.metadata.labels):
            continue

        if config['labels']['include'] != []:
            if not matchLabels(config['labels']['include'], statefulset.metadata.labels):
                continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if any(s['name'] == json['name'] and s['namespace'] == json['namespace'] for s in statefulsets):
            continue

        statefulsets.append(json)

    return statefulsets

def zabbixDiscoveryStatefulsets(clustername, statefulsets=[]):
    """
    description: create a discovery for statefulset, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for statefulset in statefulsets:
        output = {
            "{#KUBERNETES_STATEFULSET_NAMESPACE}": statefulset['namespace'],
            "{#KUBERNETES_STATEFULSET_NAME}": statefulset['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.statefulset.discovery", json.dumps(discovery))]

    return sender

def zabbixItemStatefulsets(clustername, statefulsets=[]):
    """
    description: create a item for statefulset, per namespace
    return: class ZabbixResponse
    """
    sender = []

    for statefulset in statefulsets:
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.availableReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.readyReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['ready']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.desiredReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['desired']),)

    return sender

def baseStatefulsets(mode=None, config=None):
    """
    description: monitoring statefulsets
    return: class ZabbixMetric
    """
    if mode == "discovery":
        return zabbixDiscoveryStatefulsets(config['kubernetes']['name'], kubernetesGetStatefulsets(config['monitoring']['statefulsets']))
    if mode == "item":
        return zabbixItemStatefulsets(config['kubernetes']['name'], kubernetesGetStatefulsets(config['monitoring']['statefulsets']))
    return []
