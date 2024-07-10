#!/usr/bin/env python3

import argparse, sys, os, logging
from random import randint
from time import sleep
from kubernetes import config
from pyzabbix import ZabbixSender
from modules.kubernetes.get import *
from modules.zabbix.item import *
from modules.zabbix.discovery import *

parser = argparse.ArgumentParser()
parser.add_argument("--zabbix-timeout", dest="zabbix_timeout", action="store", required=False, help="Set Zabbix timeout", default=5)
parser.add_argument("--zabbix-endpoint", dest="zabbix_endpoint", action="store", required=True, help="Set Zabbix endpoint (server)")
parser.add_argument("--kubernetes-name", dest="kubernetes_name", action="store", required=True, help="Set Kubernetes cluster name in Zabbix")
parser.add_argument("--monitoring-mode", dest="monitoring_mode", action="store", required=True, help="Mode of monitoring", choices=["volume","deployment","daemonset","node","statefulset","cronjob"])
parser.add_argument("--monitoring-type", dest="monitoring_type", action="store", required=True, help="Type of monitoring", choices=["discovery", "item", "json"])
parser.add_argument("--object-name", dest="object_name", action="store", required=False, help="Name of object in Kubernetes", default=None)
parser.add_argument("--match-label", dest="match_label", action="store", required=False, help="Match label of object in Kubernetes", default=None)
parser.add_argument("--include-name", dest="include_name", action="store", required=False, help="Include object name in Kubernetes", default=None)
parser.add_argument("--include-namespace", dest="include_namespace", action="store", required=False, help="Include namespace in Kubernetes", default=None)
parser.add_argument("--exclude-name", dest="exclude_name", action="store", required=False, help="Exclude object name in Kubernetes", default=None)
parser.add_argument("--exclude-namespace", dest="exclude_namespace", action="store", required=False, help="Exclude namespace in Kubernetes", default=None)
parser.add_argument("--no-wait", dest="no_wait", action="store_true", required=False, help="Disable startup wait time", default=False)
parser.add_argument("--verbose", dest="verbose", action="store_true", required=False, help="Verbose output", default=False)
parser.add_argument("--debug", dest="debug", action="store_true", required=False, help="Debug output for Zabbix", default=False)
args = parser.parse_args()

if args.debug:
    logger = logging.getLogger("pyzabbix")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token") and not os.getenv('KUBECONFIG'):
    config.load_incluster_config()
    if args.verbose: print("Kubernetes credentials from ServiceAccount")
else:
    try:
        config.load_kube_config()
        if args.verbose: print("Kubernetes credentials from KUBECONFIG")
    except:
        print("Unable to find kubernetes cluster configuration")
        sys.exit(1)

zabbix = ZabbixSender(args.zabbix_endpoint)
if args.zabbix_timeout: zabbix.timeout = int(args.zabbix_timeout)
if args.verbose:
    print(f"Zabbix endpoint: {args.zabbix_endpoint}")
    print(f"Zabbix timeout: {args.zabbix_timeout}")
    print(f"Kubernetes name: {args.kubernetes_name}")

if __name__ == "__main__":

    # Random sleep between 0 and 15 seconds
    if args.no_wait == False:
        timewait = randint(0,15)
        if args.verbose: print(f"Starting in {timewait} second(s)...")
        sleep(timewait)

    # Node
    if args.monitoring_mode == "node":
        if args.monitoring_type == "json":
            print("JSON output (node): {}".format(
                getNode(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.exclude_name
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (node): {}".format(
                zabbix.send(
                    zabbixDiscoveryNode(
                        args.kubernetes_name,
                        getNode(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.exclude_name
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (node): {}".format(
                zabbix.send(zabbixItemNode(
                    args.kubernetes_name,
                    getNode(
                        args.object_name,
                        args.match_label,
                        args.include_name,
                        args.exclude_name
                    )
                ))
            ))

    # Daemonset
    if args.monitoring_mode == "daemonset":
        if args.monitoring_type == "json":
            print("JSON output (daemonset): {}".format(
                getDaemonset(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.include_namespace,
                    args.exclude_name,
                    args.exclude_namespace
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (daemonset): {}".format(
                zabbix.send(
                    zabbixDiscoveryDaemonset(
                        args.kubernetes_name,
                        getDaemonset(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (daemonset): {}".format(
                zabbix.send(
                    zabbixItemDaemonset(
                        args.kubernetes_name,
                        getDaemonset(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))

    # Volumes
    if args.monitoring_mode == "volume":
        if args.monitoring_type == "json":
            print("JSON output (volume): {}".format(
                getVolume(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.include_namespace,
                    args.exclude_name,
                    args.exclude_namespace
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (volume): {}".format(
                zabbix.send(
                    zabbixDiscoveryVolume(
                        args.kubernetes_name,
                        getVolume(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (volume): {}".format(
                zabbix.send(
                    zabbixItemVolume(
                        args.kubernetes_name,
                        getVolume(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
    
    # Deployment
    if args.monitoring_mode == "deployment":
        if args.monitoring_type == "json":
            print("JSON output (deployment): {}".format(
                getDeployment(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.include_namespace,
                    args.exclude_name,
                    args.exclude_namespace
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (deployment): {}".format(
                zabbix.send(
                    zabbixDiscoveryDeployment(
                        args.kubernetes_name,
                        getDeployment(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (deployment): {}".format(
                zabbix.send(
                    zabbixItemDeployment(
                        args.kubernetes_name,
                        getDeployment(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))

    # Statefulset
    if args.monitoring_mode == "statefulset":
        if args.monitoring_type == "json":
            print("JSON output (statefulset): {}".format(
                getStatefulset(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.include_namespace,
                    args.exclude_name,
                    args.exclude_namespace
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (statefulset): {}".format(
                zabbix.send(
                    zabbixDiscoveryStatefulset(
                        args.kubernetes_name,
                        getStatefulset(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (statefulset): {}".format(
                zabbix.send(
                    zabbixItemStatefulset(
                        args.kubernetes_name,
                        getStatefulset(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))

    # Cronjob
    if args.monitoring_mode == "cronjob":
        if args.monitoring_type == "json":
            print("JSON output (cronjob): {}".format(
                getCronjob(
                    args.object_name,
                    args.match_label,
                    args.include_name,
                    args.include_namespace,
                    args.exclude_name,
                    args.exclude_namespace
                )
            ))
        if args.monitoring_type == "discovery":
            print("Zabbix discovery (cronjob): {}".format(
                zabbix.send(
                    zabbixDiscoveryCronjob(
                        args.kubernetes_name,
                        getCronjob(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
        if args.monitoring_type == "item":
            print("Zabbix item (cronjob): {}".format(
                zabbix.send(
                    zabbixItemCronjob(
                        args.kubernetes_name,
                        getCronjob(
                            args.object_name,
                            args.match_label,
                            args.include_name,
                            args.include_namespace,
                            args.exclude_name,
                            args.exclude_namespace
                        )
                    )
                )
            ))
