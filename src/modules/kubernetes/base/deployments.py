from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.deployments")

def kubernetesGetDeployments(config=None):
    """
    description: get deployments data
    return: list
    """
    kubernetes = client.AppsV1Api()

    deployments = []

    for deployment in kubernetes.list_deployment_for_all_namespaces().items:

        json = {
            "name": deployment.metadata.name,
            "namespace": deployment.metadata.namespace,
            "replicas": {
                "desired": deployment.status.replicas,
                "ready": deployment.status.ready_replicas,
                "available": deployment.status.available_replicas
            }
        }

        if matchLabels(config['labels']['exclude'], deployment.metadata.labels):
            continue

        if config['labels']['include'] != []:
            if not matchLabels(config['labels']['include'], deployment.metadata.labels):
                continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in deployments):
            continue

        deployments.append(json)

    return deployments

def zabbixDiscoveryDeployments(clustername, deployments=[]):
    """
    description: create a discovery for deployment, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for deployment in deployments:
        output = {
            "{#KUBERNETES_DEPLOYMENT_NAMESPACE}": deployment['namespace'],
            "{#KUBERNETES_DEPLOYMENT_NAME}": deployment['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.deployment.discovery", json.dumps(discovery))]

    return sender

def zabbixItemDeployments(clustername, deployments=[]):
    """
    description: create a item for deployment, per namespace
    return: class ZabbixResponse
    """
    sender = []

    for deployment in deployments:
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.availableReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.readyReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['ready']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.desiredReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['desired']),)

    return sender

def baseDeployments(mode=None, config=None):
    """
    description: monitoring deployments
    return: class ZabbixMetric
    """
    logging.info(f"Function baseDeployments() executed: {mode}")
    if mode == "discovery":
        return zabbixDiscoveryDeployments(config['kubernetes']['name'], kubernetesGetDeployments(config['monitoring']['deployments']))
    if mode == "item":
        return zabbixItemDeployments(config['kubernetes']['name'], kubernetesGetDeployments(config['monitoring']['deployments']))
    return []
