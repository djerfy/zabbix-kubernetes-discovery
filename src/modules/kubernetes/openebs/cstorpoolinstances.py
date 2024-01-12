from kubernetes import client
from modules.common.functions import *
import urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.openebs.cstorpoolinstances")

def openebsGetCstorpoolinstances(config):
    """
    description: get cstorpoolinstances data
    return: list
    """
    kubernetes = client.CustomObjectsApi()

    cstorpoolinstances = []

    if config['monitoring']['openebs']['engine'] != "cstor":
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
                if matchLabels(config['monitoring']['openebs']['labels']['exclude'], cstorpoolinstance['metadata']['labels']):
                    continue
                if config['monitoring']['openebs']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['openebs']['labels']['exclude'], cstorpoolinstance['metadata']['labels']):
                        continue

        if any(c['name'] == json['name'] and c['namespace'] == json['namespace'] for c in cstorpoolinstances):
            continue

        cstorpoolinstances.append(json)

    return cstorpoolinstances

def zabbixDiscoveryCstorpoolinstances(config):
    """
    description: create a discovery for cstorpoolinstances, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for cstorpoolinstance in openebsGetCstorpoolinstances(config):
        output = {
            "{#KUBERNETES_OPENEBS_CSTORPOOLINSTANCES_NAMESPACE}": cstorpoolinstance['namespace'],
            "{#KUBERNETES_OPENEBS_CSTORPOOLINSTANCES_NAME}": cstorpoolinstance['name']}
        discovery['data'].append(output)

    return [[config['kubernetes']['name'], "kubernetes.openebs.cstorpoolinstances.discovery", json.dumps(discovery)]]

def zabbixItemsCstorpoolinstances(config):
    """
    description: create a item for cstorpoolinstances, per namespace
    return: list
    """
    items = []

    for cstorpoolinstance in openebsGetCstorpoolinstances(config):
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.readonly[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['readOnly']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.provisionedReplicas[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['provisionedReplicas']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.healthyReplicas[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['healthyReplicas']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.status[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['phase']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.capacity.total[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['total']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.capacity.free[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['free']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolinstances.capacity.used[{cstorpoolinstance['namespace']},{cstorpoolinstance['name']}]", cstorpoolinstance['status']['capacity']['used']])

    return items
