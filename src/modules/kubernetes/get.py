from kubernetes import client
from datetime import datetime
from modules.common.functions import *
import json, urllib3

urllib3.disable_warnings()

def getNode(name=None, exclude_name=None):
    """
    description: get all or specific node
    return: list
    """
    kubernetes = client.CoreV1Api()

    nodes = []

    for node in kubernetes.list_node().items:
        node_healthz = kubernetes.connect_get_node_proxy_with_path(name=node.metadata.name, path="healthz")
        node_status  = kubernetes.read_node_status(name=node.metadata.name)
        node_pods    = kubernetes.list_pod_for_all_namespaces(field_selector="spec.nodeName={}".format(node.metadata.name))

        json = {
            "name": node.metadata.name,
            "uid": node.metadata.uid,
            "status": node_healthz,
            "capacity": node_status.status.capacity,
            "allocatable": node_status.status.allocatable,
            "current": {
                "pods": str(len(node_pods.items)),
                "pods_used": str(round(len(node_pods.items) * 100 / int(node_status.status.allocatable['pods']), 1)),
                "pods_free": str(round(100 - (len(node_pods.items) * 100 / int(node_status.status.allocatable['pods'])), 1))
            }
        }

        if ifObjectMatch(exclude_name, json['name']):
            continue

        if name == json['name']:
            return [json]

        if any(n['name'] == json['name'] for n in nodes):
            continue

        nodes.append(json)

    return nodes


def getDaemonset(name=None, exclude_name=None, exclude_namespace=None):
    """
    description: get all or specific daemonset
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

        if ifObjectMatch(exclude_name, json['name']):
            continue

        if ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        if name == json['name']:
            return [json]

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in daemonsets):
            continue

        daemonsets.append(json)

    return daemonsets


def getVolume(name=None, exclude_name=None, exclude_namespace=None):
    """
    description: get all or specific persistent volume claim
    return: list
    """
    kubernetes = client.CoreV1Api()

    volumes = []

    for node in kubernetes.list_node().items:
        node_info = kubernetes.connect_get_node_proxy_with_path(name=node.metadata.name, path="stats/summary").replace("'", "\"")
        node_json = json.loads(node_info)

        for pod in node_json['pods']:

            if not "volume" in pod:
                continue

            for volume in pod['volume']:

                if not "pvcRef" in volume:
                    continue
                else:
                    volume['namespace'] = volume['pvcRef']['namespace']
                    volume['name'] = volume['pvcRef']['name']

                if ifObjectMatch(exclude_name, volume['name']):
                    continue

                if ifObjectMatch(exclude_namespace, volume['namespace']):
                    continue

                for i in ["time", "pvcRef"]:
                    del volume[i]

                if name == volume['name']:
                    return [volume]

                if any(v['name'] == volume['name'] and v['namespace'] == volume['namespace'] for v in volumes):
                    continue
                
                if "-token-" in volume['name']:
                    continue

                volumes.append(volume)

    return volumes


def getDeployment(name=None, exclude_name=None, exclude_namespace=None):
    """
    description: get all or specific deployment
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

        if ifObjectMatch(exclude_name, json['name']):
            continue

        if ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if name == json['name']:
            return [json]

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in deployments):
            continue

        deployments.append(json)

    return deployments


def getStatefulset(name=None, exclude_name=None, exclude_namespace=None):
    """
    description: get all or specific statefulset
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

        if ifObjectMatch(exclude_name, json['name']):
            continue

        if ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        for i in ["desired", "ready", "available"]:
            if json['replicas'][i] is None:
                json['replicas'][i] = 0

        if name == json['name']:
            return [json]

        if any(s['name'] == json['name'] and s['namespace'] == json['namespace'] for s in statefulsets):
            continue

        statefulsets.append(json)

    return statefulsets


def getPodjob(name=None):
    """
    description: get all or specific pod from cronjob
    return: list
    """
    kubernetes = client.CoreV1Api()

    pods = []

    for pod in kubernetes.list_pod_for_all_namespaces().items:

        if not pod.metadata.owner_references:
            continue

        if not "Job" in pod.metadata.owner_references[0].kind:
            continue

        if name != pod.status.container_statuses[0].name:
            continue

        json = {
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "status": {
                "restart": pod.status.container_statuses[0].restart_count,
                "exitcode": pod.status.container_statuses[0].state.terminated.exit_code,
                "started": datetime.timestamp(pod.status.container_statuses[0].state.terminated.started_at),
                "finished": datetime.timestamp(pod.status.container_statuses[0].state.terminated.finished_at),
                "reason": pod.status.container_statuses[0].state.terminated.reason
            }
        }

        pods.append(json)

    return pods


def getCronjob(name=None, exclude_name=None, exclude_namespace=None):
    """
    description: get all or specific cronjob
    return: list
    """
    kubernetes = client.BatchV1Api()

    cronjobs = []

    for cronjob in kubernetes.list_cron_job_for_all_namespaces().items:

        pods_created = getPodjob(name=cronjob.metadata.name)
        pods_finished, pod_latest = [], {}

        for pod in pods_created:
            pods_finished.append(pod['status']['finished'])

        for pod in pods_created:
            if pod['status']['finished'] == sorted(pods_finished)[-1]:
                pod_latest = pod

        json = {
            "name": cronjob.metadata.name,
            "namespace": cronjob.metadata.namespace,
            "status": pod_latest
        }

        if ifObjectMatch(exclude_name, json['name']):
            continue

        if ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        if name == json['name']:
            return [json]

        cronjobs.append(json)

    return cronjobs
