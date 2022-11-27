from pyzabbix import ZabbixMetric
import json

def zabbixDiscoveryNode(clustername, nodes=[]):
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


def zabbixDiscoveryDaemonset(clustername, daemonsets=[]):
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


def zabbixDiscoveryVolume(clustername, volumes=[]):
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


def zabbixDiscoveryDeployment(clustername, deployments=[]):
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


def zabbixDiscoveryStatefulset(clustername, statefulsets=[]):
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


def zabbixDiscoveryCronjob(clustername, cronjobs=[]):
    """
    description: create a discovery for cronjob, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for cronjob in cronjobs:
        output = {
            "{#KUBERNETES_CRONJOB_NAMESPACE}": cronjob['namespace'],
            "{#KUBERNETES_CRONJOB_NAME}": cronjob['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.cronjob.discovery", json.dumps(discovery))]

    return sender
