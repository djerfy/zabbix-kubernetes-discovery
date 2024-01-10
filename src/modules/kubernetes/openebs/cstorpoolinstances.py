from kubernetes import client
from pyzabbix import ZabbixMetric
from modules.common.functions import *
import json, urllib3

urllib3.disable_warnings()

def openebsGetCstorpoolinstances(config=None):
    """
    description: get cstorpoolinstances data
    return: list
    """
    kubernetes = client.CustomObjectsApi()

    cstorpoolinstances = []

    if config['engine'] != "cstor":
        return cstorpoolinstances

    for cstorpoolinstance in rawObjects(kubernetes.list_cluster_custom_object(group="cstor.openebs.io", version="v1", plural="cstorpoolinstances")):
        json = {
            "name": cstorpoolinstance['metadata']['name'],
            "namespace": cstorpoolinstance['metadata']['namespace'],
            "status": cstorpoolinstance['status'],
            "version": {
                "desired": cstorpoolinstance['versionDetails']['desired'],
                "current": cstorpoolinstance['versionDetails']['status']['current']
            }
        }

        if cstorpoolinstance.get("metadata"):
            if cstorpoolinstance['metadata'].get("labels"):
                if matchLabels(config['labels']['exclude'], cstorpoolinstance['metadata']['labels']):
                    continue
                if config['labels']['include'] != []:
                    if not matchLabels(config['labels']['exclude'], cstorpoolinstance['metadata']['labels']):
                        continue

        if any(c['name'] == json['name'] and c['namespace'] == json['namespace'] for c in cstorpoolinstance):
            continue

        cstorpoolinstances.append(json)

    return cstorpoolinstances

def ZabbixDiscoveryCstorpoolinstances(clustername, cstorpoolinstances=[]):
    """
    description: create a discovery for cstorpoolinstances, per namespace
    return: class ZabbixMetric
    """
    discovery = {"data":[]}

    for cstorpoolinstance in cstorpoolinstances:
        output = {
            "{#KUBERNETES_OPENEBS_CSTORPOOLINSTANCE_NAMESPACE}": cstorpoolinstance['namespace'],
            "{#KUBERNETES_OPENEBS_CSTORPOOLINSTANCE_NAME}": cstorpoolinstance['name']}
        discovery['data'].append(output)

    sender = [ZabbixMetric(clustername, "kubernetes.openebs.cstorpoolinstances.discovery", json.dumps(discovery))]

    return sender

def ZabbixItemCstorpoolinstances(clustername, cstorpoolinstances=[]):
    """
    description: create a item for cstorpoolinstances, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for cstorpoolinstance in cstorpoolinstances:
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.readonly[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['readOnly']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.provisionedReplicas[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['provisionedReplicas']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.healthyReplicas[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['healthyReplicas']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.status[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['phase']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.capacity.total[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['total']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.capacity.free[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['free']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.openebs.cstorpoolinstances.capacity.used[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['used']),)
    return sender

def baseOpenebsCstorpoolinstances(mode=None, config=None):
    """
    description: monitoring openebs cstorpoolinstances
    return: class ZabbixMetric
    """
    if mode == "discovery":
        return ZabbixDiscoveryCstorpoolinstances(config['kubernetes']['name'], openebsGetCstorpoolinstances(config['monitoring']['openebs']))
    if mode == "item":
        return ZabbixItemCstorpoolinstances(config['kubernetes']['name'], openebsGetCstorpoolinstances(config['monitoring']['openebs']))
    return []
