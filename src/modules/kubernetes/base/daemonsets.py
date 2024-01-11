from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.daemonsets")

def kubernetesGetDaemonsets(config=None):
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

        if matchLabels(config['labels']['exclude'], daemonset.metadata.labels):
            continue

        if config['labels']['include'] != []:
            if not matchLabels(config['labels']['include'], daemonset.metadata.labels):
                continue

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in daemonsets):
            continue

        daemonsets.append(json)

    return daemonsets

def zabbixDiscoveryDaemonsets(clustername, daemonsets=[]):
    """
    description: create a discovery for daemonset, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for daemonset in daemonsets:
        output = {
            "{#KUBERNETES_DAEMONSET_NAMESPACE}": daemonset['namespace'],
            "{#KUBERNETES_DAEMONSET_NAME}": daemonset['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.daemonset.discovery", json.dumps(discovery))]

    return sender

def zabbixItemDaemonsets(clustername, daemonsets=[]):
    """
    description: create a item for daemonset, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for daemonset in daemonsets:
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.desiredReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['desired']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.currentReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['current']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.availableReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.readyReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['ready']),)

    return sender

def baseDaemonsets(mode=None, config=None):
    """
    description: monitoring daemonsets
    return: class ZabbixMetric
    """
    logging.info(f"Function baseDaemonsets() executed: {mode}")
    if mode == "discovery":
        return zabbixDiscoveryDaemonsets(config['kubernetes']['name'], kubernetesGetDaemonsets(config['monitoring']['daemonsets']))
    if mode == "item":
        return zabbixItemDaemonsets(config['kubernetes']['name'], kubernetesGetDaemonsets(config['monitoring']['daemonsets']))
    return []