#!/usr/bin/env python3

import argparse, sys, os, yaml, queue
import logging, schedule, threading, psutil
from time import sleep
from kubernetes import config as kube_config
from pyzabbix import ZabbixSender
from modules.kubernetes.base import *
from modules.kubernetes.openebs import *

parser = argparse.ArgumentParser()
parser.add_argument("--config-file", dest="config_file", action="store", required=False, help="Configuration file (default: config.yaml)", default="config.yaml")
parser.add_argument("--log-level", dest="log_level", action="store", required=False, help="Logging output log-level (default: INFO)", default="INFO", choices=["INFO", "WARNING", "ERROR", "DEBUG"])
args = parser.parse_args()

logging.basicConfig(
    datefmt="%d/%m/%Y %H:%M:%S",
    format="[%(asctime)s] (%(levelname)s) %(name)s.%(funcName)s():%(lineno)d - %(message)s",
    level=getattr(logging, args.log_level))
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

with open(args.config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.debug(f"Configuration file {args.config_file} loaded successfully")

zabbix = ZabbixSender(config['zabbix']['endpoint'])
zabbix.timeout = int(config['zabbix']['timeout'])
logging.debug(f"-> Zabbix endpoint: {config['zabbix']['endpoint']}")
logging.debug(f"-> Zabbix timeout: {config['zabbix']['timeout']}")
logging.debug(f"-> Cluster name: {config['kubernetes']['name']}")

def executeSender(data):
    try:
        logging.debug(data)
        zabbix.send(data)
    except Exception as e:
        logging.debug(e)

def executeJobs():
    p = psutil.Process(os.getpid())
    logging.debug(f"Program memory used (rss): {p.memory_info().rss / 1024 / 1024} MiB")

    while True:
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

    # cronjobs
    if config['monitoring']['cronjobs']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseCronjobs(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseCronjobs(mode="item", config=config)))

    # daemonsets
    if config['monitoring']['daemonsets']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseDaemonsets(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseDaemonsets(mode="item", config=config)))

    # deployments
    if config['monitoring']['deployments']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseDeployments(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseDeployments(mode="item", config=config)))

    # nodes
    if config['monitoring']['nodes']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseNodes(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseNodes(mode="item", config=config)))

    # statefulsets
    if config['monitoring']['statefulsets']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseStatefulsets(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseStatefulsets(mode="item", config=config)))

    # volumes
    if config['monitoring']['volumes']['enabled']:
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseVolumes(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseVolumes(mode="item", config=config)))

    # openebs
    if config['monitoring']['openebs']['enabled']:
        # cstorpoolclusters
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseOpenebsCstorpoolclusters(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseOpenebsCstorpoolclusters(mode="item", config=config)))
        # cstorpoolinstances
        schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(jobs_queue.put, lambda: executeSender(baseOpenebsCstorpoolinstances(mode="discovery", config=config)))
        schedule.every(config['zabbix']['schedule']['items']).seconds.do(jobs_queue.put, lambda: executeSender(baseOpenebsCstorpoolinstances(mode="item", config=config)))

    # thread
    thread = threading.Thread(target=executeJobs)
    thread.start()

    # tasks
    while True:
        schedule.run_pending()
        logging
        sleep(1)
    