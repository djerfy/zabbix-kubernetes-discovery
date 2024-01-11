#!/usr/bin/env python3

import argparse, sys, os, yaml, queue
import logging, schedule, threading, psutil
from time import sleep
from kubernetes import config as kube_config
from zappix.sender import Sender as zabbix_sender
from modules.kubernetes.base import *
from modules.kubernetes.openebs import *

parser = argparse.ArgumentParser()
parser.add_argument("--config-file", dest="config_file", action="store", required=False, help="Configuration file (default: config.yaml)", default="config.yaml")
args = parser.parse_args()

with open(args.config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

logging.basicConfig(
    datefmt="%d/%m/%Y %H:%M:%S",
    format="[%(asctime)s] (%(levelname)s) %(name)s.%(funcName)s():%(lineno)d - %(message)s",
    level=getattr(logging, config['output']['level']))
logging = logging.getLogger("main")

if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token") and not os.getenv('KUBECONFIG'):
    kube_config.load_incluster_config()
    logging.debug("Loading Kubernetes credentials from ServiceAccount")
else:
    try:
        kube_config.load_kube_config()
        logging.debug("Loading Kubernetes credentials from KUBECONFIG variable")
    except:
        logging.error("Unable to load Kubernetes credentials")
        sys.exit(1)

zabbix = zabbix_sender(config['zabbix']['endpoint'])
zabbix.timeout = int(config['zabbix']['timeout'])
logging.debug(f"-> Zabbix endpoint: {config['zabbix']['endpoint']}")
logging.debug(f"-> Zabbix timeout: {config['zabbix']['timeout']}")
logging.debug(f"-> Cluster name: {config['kubernetes']['name']}")

def executeSender(data):
    try:
        logging.debug(data)
        zabbix.send_value(data)
    except Exception as e:
        logging.error(e)

def executeJobs():
    while True:
        logging.debug(f"Program memory used (rss): {round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024)} MiB")
        logging.debug(f"{jobs_queue.qsize()} job(s) in queue")
        jobs = jobs_queue.get()
        if jobs is not None:
            jobs()
            jobs_queue.task_done()
        else:
            logging.debug("0 job in queue")

if __name__ == "__main__":
    logging.info("Application zabbix-kubernetes-discovery started")

    jobs_queue = queue.Queue()
    sch_disco  = config['zabbix']['schedule']['discovery']
    sch_items  = config['zabbix']['schedule']['items']

    # cronjobs
    if config['monitoring']['cronjobs']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryCronjobs(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsCronjobs(config)))

    # daemonsets
    if config['monitoring']['daemonsets']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryDaemonsets(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsDaemonsets(config)))

    # deployments
    if config['monitoring']['deployments']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryDeployments(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsDeployments(config)))

    # nodes
    if config['monitoring']['nodes']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryNodes(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsNodes(config)))

    # statefulsets
    if config['monitoring']['statefulsets']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryStatefulsets(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsStatefulsets(config)))

    # volumes
    if config['monitoring']['volumes']['enabled']:
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryVolumes(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsVolumes(config)))

    # openebs
    if config['monitoring']['openebs']['enabled']:
        # cstorpoolclusters
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryCstorpoolclusters(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsCstorpoolclusters(config)))
        # cstorpoolinstances
        schedule.every(sch_disco).seconds.do(jobs_queue.put, lambda: executeSender(zabbixDiscoveryCstorpoolinstances(config)))
        schedule.every(sch_items).seconds.do(jobs_queue.put, lambda: executeSender(zabbixItemsCstorpoolinstances(config)))

    # thread
    thread = threading.Thread(target=executeJobs)
    thread.start()

    # tasks
    while True:
        schedule.run_pending()
        logging
        sleep(1)
    