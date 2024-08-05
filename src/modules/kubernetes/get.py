from kubernetes import client
from datetime import datetime
from modules.common.functions import *
import json, urllib3, re

urllib3.disable_warnings()

def getNode(
    name=None,
    match_label=None,
    include_name=None,
    exclude_name=None
):
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

        if match_label and not ifLabelMatch(match_label, node.metadata.labels):
            continue

        if include_name and not ifObjectMatch(include_name, json['name']):
            continue

        if exclude_name and ifObjectMatch(exclude_name, json['name']):
            continue

        if name == json['name']:
            return [json]

        if any(n['name'] == json['name'] for n in nodes):
            continue

        nodes.append(json)

    return nodes


def getDaemonset(
    name=None,
    match_label=None,
    include_name=None,
    include_namespace=None,
    exclude_name=None,
    exclude_namespace=None
):
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

        if match_label and not ifLabelMatch(match_label, daemonset.metadata.labels):
            continue

        if include_name and not ifObjectMatch(include_name, json['name']):
            continue

        if include_namespace and not ifObjectMatch(include_namespace, json['namespace']):
            continue

        if exclude_name and ifObjectMatch(exclude_name, json['name']):
            continue

        if exclude_namespace and ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        if name == json['name']:
            return [json]

        if any(d['name'] == json['name'] and d['namespace'] == json['namespace'] for d in daemonsets):
            continue

        daemonsets.append(json)

    return daemonsets


def getVolume(
    name=None,
    match_label=None,
    include_name=None,
    include_namespace=None,
    exclude_name=None,
    exclude_namespace=None
):
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

                if volume['pvcRef']['name'].startswith(pod['podRef']['name']) and re.match(r"(.*)-[a-z0-9]{8,10}-[a-z0-9]{5}$", pod['podRef']['name']):
                    continue

                volume['namespace'] = volume['pvcRef']['namespace']
                volume['name'] = volume['pvcRef']['name']

                if match_label:
                    volume_object = kubernetes.read_namespaced_persistent_volume_claim(name=volume['name'], namespace=volume['namespace']).to_dict()
                    volume['metadata'], volume['metadata']['labels'] = {}, json.dumps(volume_object.get('metadata', {}).get('labels', {}))
                    if not ifLabelMatch(match_label, volume['metadata']['labels']):
                        continue

                if include_name and not ifObjectMatch(include_name, volume['name']):
                    continue

                if include_namespace and not ifObjectMatch(include_namespace, volume['namespace']):
                    continue

                if exclude_name and ifObjectMatch(exclude_name, volume['name']):
                    continue

                if exclude_namespace and ifObjectMatch(exclude_namespace, volume['namespace']):
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


def getDeployment(
    name=None,
    match_label=None,
    include_name=None,
    include_namespace=None,
    exclude_name=None,
    exclude_namespace=None
):
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

        if match_label and not ifLabelMatch(match_label, deployment.metadata.labels):
            continue

        if include_name and not ifObjectMatch(include_name, json['name']):
            continue

        if include_namespace and not ifObjectMatch(include_namespace, json['namespace']):
            continue

        if exclude_name and ifObjectMatch(exclude_name, json['name']):
            continue

        if exclude_namespace and ifObjectMatch(exclude_namespace, json['namespace']):
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


def getStatefulset(
    name=None,
    match_label=None,
    include_name=None,
    include_namespace=None,
    exclude_name=None,
    exclude_namespace=None
):
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

        if match_label and not ifLabelMatch(match_label, statefulset.metadata.labels):
            continue

        if include_name and not ifObjectMatch(include_name, json['name']):
            continue

        if include_namespace and not ifObjectMatch(include_namespace, json['namespace']):
            continue

        if exclude_name and ifObjectMatch(exclude_name, json['name']):
            continue

        if exclude_namespace and ifObjectMatch(exclude_namespace, json['namespace']):
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


def getCronjob(
    name=None,
    match_label=None,
    include_name=None,
    include_namespace=None,
    exclude_name=None,
    exclude_namespace=None
):
    """
    description: get all or specific cronjob
    return: list
    """
    kubernetes = client.BatchV1Api()

    cronjobs = []

    for cronjob in kubernetes.list_cron_job_for_all_namespaces().items:

        related_jobs, job_latest = [], {}

        for job in kubernetes.list_job_for_all_namespaces().items:

            if not job:
                continue

            if not job.metadata.owner_references:
                continue

            if not "CronJob" in job.metadata.owner_references[0].kind:
                continue

            if job.metadata.owner_references[0].name != cronjob.metadata.name:
                continue

            if job.status.active is not None:
                continue

            related_jobs.append(job)

        for related_job in related_jobs:

            if not bool(job_latest):
                job_latest = related_job
                continue

            related_job_dt = datetime.timestamp(related_job.status.conditions[0].last_probe_time)
            job_latest_dt = datetime.timestamp(job_latest.status.conditions[0].last_probe_time)

            if related_job_dt > job_latest_dt:
                job_latest = related_job

        if type(job_latest) is dict:
            continue

        if job_latest.status.conditions[0].type == "Complete":
            cronjob_status = "0"
        else:
            cronjob_status = "1"

        json = {
            "name": cronjob.metadata.name,
            "namespace": cronjob.metadata.namespace,
            "status": cronjob_status,
            "last_job": {
                "name": job_latest.metadata.name,
                "reason": job_latest.status.conditions[0].reason,
                "message": job_latest.status.conditions[0].message,
                "status": job_latest.status.conditions[0].type
            }
        }

        if match_label and not ifLabelMatch(match_label, cronjob.metadata.labels):
            continue

        if include_name and not ifObjectMatch(include_name, json['name']):
            continue

        if include_namespace and not ifObjectMatch(include_namespace, json['namespace']):
            continue

        if exclude_name and ifObjectMatch(exclude_name, json['name']):
            continue

        if exclude_namespace and ifObjectMatch(exclude_namespace, json['namespace']):
            continue

        if name == json['name']:
            return [json]

        cronjobs.append(json)

    return cronjobs
