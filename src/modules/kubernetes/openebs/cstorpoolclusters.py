from kubernetes import client
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.openebs.cstorpoolclusters")

def openebsGetCstorpoolclusters(config):
    """
    description: get cstorpoolclusters data
    return: list
    """
    kubernetes = client.CustomObjectsApi()

    cstorpoolclusters = []

    if config['monitoring']['openebs']['engine'] != "cstor":
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
                if matchLabels(config['monitoring']['openebs']['labels']['exclude'], cstorpoolcluster['metadata']['labels']):
                    continue
                if config['monitoring']['openebs']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['openebs']['labels']['exclude'], cstorpoolcluster['metadata']['labels']):
                        continue

        if any(c['name'] == json['name'] and c['namespace'] == json['namespace'] for c in cstorpoolclusters):
            continue

        cstorpoolclusters.append(json)

    return cstorpoolclusters

def zabbixDiscoveryCstorpoolclusters(config):
    """
    description: create a discovery for cstorpoolclusters, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for cstorpoolcluster in openebsGetCstorpoolclusters(config):
        output = {
            "{#KUBERNETES_OPENEBS_CSTORPOOLCLUSTER_NAMESPACE}": cstorpoolcluster['namespace'],
            "{#KUBERNETES_OPENEBS_CSTORPOOLCLUSTER_NAME}": cstorpoolcluster['name']}
        discovery['data'].append(output)

    return [config['kubernetes']['name'], "kubernetes.openebs.cstorpoolclusters.discovery", json.dumps(discovery)]

def zabbixItemsCstorpoolclusters(config):
    """
    description: create a item for cstorpoolclusters, per namespace
    return: list
    """
    items = []

    for cstorpoolcluster in openebsGetCstorpoolclusters(config):
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolclusters.desiredInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['desired']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolclusters.healthyInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['healthy']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolclusters.provisionedInstances[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['instances']['provisioned']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolclusters.desiredVersion[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['version']['desired']])
        items.append([config['kubernetes']['name'], f"kubernetes.openebs.cstorpoolclusters.currentVersion[{cstorpoolcluster['namespace']},{cstorpoolcluster['name']}]", cstorpoolcluster['version']['current']])

    return items
