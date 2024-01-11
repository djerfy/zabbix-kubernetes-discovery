from kubernetes import client
from datetime import datetime
from modules.common.functions import *
import json, urllib3, logging

urllib3.disable_warnings()
logging = logging.getLogger("kubernetes.base.cronjobs")

def kubernetesGetCronjobs(config):
    """
    description: get cronjobs data
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

        if cronjob.metadata:
            if cronjob.metadata.labels:
                if matchLabels(config['monitoring']['cronjobs']['labels']['exclude'], cronjob.metadata.labels):
                    continue
                if config['monitoring']['cronjobs']['labels']['include'] != []:
                    if not matchLabels(config['monitoring']['cronjobs']['labels']['include'], cronjob.metadata.labels):
                        continue

        cronjobs.append(json)

    return cronjobs

def zabbixDiscoveryCronjobs(config):
    """
    description: create a discovery for cronjob, per namespace
    return: dict
    """
    discovery = {"data":[]}

    for cronjob in kubernetesGetCronjobs(config):
        output = {
            "{#KUBERNETES_CRONJOB_NAMESPACE}": cronjob['namespace'],
            "{#KUBERNETES_CRONJOB_NAME}": cronjob['name']}
        discovery['data'].append(output)

    return [config['kubernetes']['name'], "kubernetes.cronjobs.discovery", json.dumps(discovery)]

def zabbixItemsCronjobs(config):
    """
    description: create a item for cronjob, per namespace
    return: list
    """
    items = []

    for cronjob in kubernetesGetCronjobs(config):
        items.append([config['kubernetes']['name'], f"kubernetes.cronjob.status[{cronjob['namespace']},{cronjob['name']}]", cronjob['status']])
        items.append([config['kubernetes']['name'], f"kubernetes.cronjob.reason[{cronjob['namespace']},{cronjob['name']}]", cronjob['last_job']['reason']])
        items.append([config['kubernetes']['name'], f"kubernetes.cronjob.message[{cronjob['namespace']},{cronjob['name']}]", cronjob['last_job']['message']])

    return items
