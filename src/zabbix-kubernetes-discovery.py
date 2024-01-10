#!/usr/bin/env python3

import argparse, sys, os
import logging, schedule, yaml
from time import sleep
from kubernetes import config as kube_config
from pyzabbix import ZabbixSender
from modules.kubernetes.base import *

parser = argparse.ArgumentParser()
parser.add_argument("--config-file", "-c", dest="config_file", action="store", required=False, help="Configuration file (default: config.yaml)", default="config.yaml")
parser.add_argument("--debug", "-d", dest="debug", action="store_true", required=False, help="Enable debug output (default: false)", default=False)
args = parser.parse_args()

logging.basicConfig(
    format="[%(asctime)s] (%(levelname)s) %(name)s.%(funcName)s():%(lineno)d - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.INFO)

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

def mainSender(data):
    try:
        logging.debug(data)
        zabbix.send(data)
    except Exception as e:
        logging.debug(e)

if __name__ == "__main__":
    # discovery
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseCronjobs(mode="discovery", config=config)))         # cronjobs
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseDaemonsets(mode="discovery", config=config)))       # daemonsets
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseDeployments(mode="discovery", config=config)))      # deployments
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseNodes(mode="discovery", config=config)))            # nodes
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseStatefulsets(mode="discovery", config=config)))     # statefulsets
    schedule.every(config['zabbix']['schedule']['discovery']).seconds.do(lambda: mainSender(baseVolumes(mode="discovery", config=config)))          # volumes

    # items
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseCronjobs(mode="item", config=config)))                   # cronjobs
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseDaemonsets(mode="item", config=config)))                 # daemonsets
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseDeployments(mode="item", config=config)))                # deployments
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseNodes(mode="item", config=config)))                      # nodes
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseStatefulsets(mode="item", config=config)))               # statefulsets
    schedule.every(config['zabbix']['schedule']['items']).seconds.do(lambda: mainSender(baseVolumes(mode="item", config=config)))                    # volumes

    # tasks
    while True:
        schedule.run_pending()
        sleep(1)
