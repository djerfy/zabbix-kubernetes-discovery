from kubernetes import client
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.deployments")

def kubernetesGetDeployments(config):
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

        if hasattr(deployment, 'metadata'):
            if hasattr(deployment.metadata, 'labels'):
                if matchLabels(config['monitoring']['deployments']['labels']['exclude'], deployment.metadata.labels):
                    continue
                if config['monitoring']['deployments']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['deployments']['labels']['include'], deployment.metadata.labels):
                        continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in deployments):
            continue

        deployments.append(json)

    return deployments

def zabbixDiscoveryDeployments(config):
    """
    description: create a discovery for deployment, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for deployment in kubernetesGetDeployments(config):
        output = {
            "{#KUBERNETES_DEPLOYMENT_NAMESPACE}": deployment['namespace'],
            "{#KUBERNETES_DEPLOYMENT_NAME}": deployment['name']}
        discovery['data'].append(output)

    return [[config['kubernetes']['name'], "kubernetes.deployments.discovery", json.dumps(discovery)]]

def zabbixItemsDeployments(config):
    """
    description: create a item for deployment, per namespace
    return: list
    """
    items = []

    for deployment in kubernetesGetDeployments(config):
        items.append([config['kubernetes']['name'], f"kubernetes.deployment.availableReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['available']])
        items.append([config['kubernetes']['name'], f"kubernetes.deployment.readyReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['ready']])
        items.append([config['kubernetes']['name'], f"kubernetes.deployment.desiredReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['desired']])

    return items
