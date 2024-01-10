from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3

urllib3.disable_warnings()

def openebsGetCstorpoolclusters(config=None):
    """
    description: get cstorpoolclusters data
    return: list
    """
    kubernetes = client.CustomObjectsApi()

    cstorpoolclusters = []

    if config['engine'] != "cstor":
        return cstorpoolclusters

    for cstorpoolcluster in rawObjects(kubernetes.list_cluster_custom_object(group="cstor.openebs.io", version="v1", plural="cstorpoolclusters")):
        json = {
            "name": cstorpoolcluster['metadata']['name'],
            "namespace": cstorpoolcluster['metadata']['namespace'],
            "instances": {
                "desired": cstorpoolcluster['status']['desiredInstances'],
                "healthy": cstorpoolcluster['status']['healthyInstances'],
                "provisioned": cstorpoolcluster['status']['provisionedInstances']
            },
            "version": {
                "desired": cstorpoolcluster['versionDetails']['desired'],
                "current": cstorpoolcluster['versionDetails']['status']['current']
            }
        }

        if cstorpoolcluster.get("metadata"):
            if cstorpoolcluster['metadata'].get("labels"):
                if matchLabels(config['labels']['exclude'], cstorpoolcluster['metadata']['labels']):
                    continue
                if config['labels']['include'] != []:
                    if not matchLabels(config['labels']['exclude'], cstorpoolcluster['metadata']['labels']):
                        continue

        if any(c['name'] == json['name'] and c['namespace'] == json['namespace'] for c in cstorpoolclusters):
            continue

        cstorpoolclusters.append(json)

    return cstorpoolclusters

def ZabbixDiscoveryCstorpoolclusters(clustername, cstorpoolclusters=[]):
    """
    description: create a discovery for cstorpoolclusters, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for cstorpoolcluster in cstorpoolclusters:
        output = {
            "{#KUBERNETES_OPENEBS_CSTORPOOLCLUSTER_NAMESPACE}": cstorpoolcluster['namespace'],
            "{#KUBERNETES_OPENEBS_CSTORPOOLCLUSTER_NAME}": cstorpoolcluster['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.openebs.cstorpoolclusters.discovery", json.dumps(discovery))]

    return sender

def ZabbixItemCstorpoolclusters(clustername, cstorpoolclusters=[]):
    """
    description: create a item for cstorpoolclusters, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for cstorpoolcluster in cstorpoolclusters:
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolclusters.desiredInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['desired']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolclusters.healthyInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['healthy']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolclusters.provisionedInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['provisioned']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolclusters.desiredVersion[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['version']['desired']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolclusters.currentVersion[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['version']['current']),)

    return sender

def baseOpenebsCstorpoolclusters(mode=None, config=None):
    """
    description: monitoring openebs cstorpoolclusters
    return: class ZabbixMetric
    """
    if mode == "discovery":
        return ZabbixDiscoveryCstorpoolclusters(config['kubernetes']['name'], openebsGetCstorpoolclusters(config['monitoring']['openebs']))
    if mode == "item":
        return ZabbixItemCstorpoolclusters(config['kubernetes']['name'], openebsGetCstorpoolclusters(config['monitoring']['openebs']))
    return []
