![](https://raw.githubusercontent.com/djerfy/zabbix-kubernetes-discovery/main/.github/assets/zabbix-kubernetes-discovery.png)

<p align="center">
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/blob/main/LICENSE.md">
    <img alt="License" src="https://img.shields.io/github/license/djerfy/zabbix-kubernetes-discovery?logo=github&color=0&label=License&style=flat-square">
  </a>
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/djerfy/zabbix-kubernetes-discovery?logo=github&color=0&label=Issues&style=flat-square">
  </a>
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/actions/workflows/docker-release.yml">
    <img alt="Pipeline Docker" src="https://img.shields.io/github/actions/workflow/status/djerfy/zabbix-kubernetes-discovery/docker-release.yml?logo=github&color=0&label=Pipeline%20Docker&style=flat-square">
  </a>
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/actions/workflows/helm.yml">
    <img alt="Pipeline Helm" src="https://img.shields.io/github/actions/workflow/status/djerfy/zabbix-kubernetes-discovery/helm.yml?logo=github&color=0&label=Pipeline%20Helm&style=flat-square">
  </a>
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/actions/workflows/trivy-scan-code.yml">
    <img alt="Pipeline Helm" src="https://img.shields.io/github/actions/workflow/status/djerfy/zabbix-kubernetes-discovery/trivy-scan-code.yml?logo=github&color=0&label=Trivy%20Scan&style=flat-square">
  </a>
  <a style="text-decoration:none" href="https://github.com/djerfy/zabbix-kubernetes-discovery/releases/tag/v1.4.17">
    <img alt="Release" src="https://img.shields.io/github/v/release/djerfy/zabbix-kubernetes-discovery?logo=github&color=0&label=Release&style=flat-square">
  </a>
</p>

# Zabbix Kubernetes Discovery

[![Artifact Hub](https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/djerfy&style=flat-square)](https://artifacthub.io/packages/search?repo=djerfy)

## Introduction

Kubernetes monitoring for Zabbix with discovery objects:

* Nodes
* DaemonSets
* Deployments
* StatefulSets
* Cronjobs
* PersistentVolumeClaims

Works with 2 variables only by default:

* `ZABBIX_ENDPOINT`: Zabbix server/proxy where the datas will be sent
* `KUBERNETES_NAME`: Name of your Kubernetes cluster on Zabbix (host)

## Helm

Before installation, you need to create `zabbix-monitoring` namespace in your cluster:

```bash
$ kubectl create namespace zabbix-monitoring
```

All Helm options/parameters are available in the [Helm folder here](./helm/).

### Install from local

To install the chart with the release name `zabbix-kubernetes-discovery` from local Helm templates:

```bash
$ helm upgrade --install zabbix-kubernetes-discovery \
    ./helm/zabbix-kubernetes-discovery/ \
    --values ./helm/zabbix-kubernetes-discovery/values.yaml \
    --namespace zabbix-monitoring \
    --set namespace.name="zabbix-monitoring" \
    --set environment.ZABBIX_ENDPOINT="zabbix-proxy.example.com" \
    --set environment.KUBERNETES_NAME="kubernetes-cluster-example"
```

### Install from repo

To install the chart with the release name `zabbix-kubernetes-discovery` from my Helm repository:

```bash
$ helm repo add djerfy https://djerfy.github.io/helm-charts
$ helm upgrade --install zabbix-kubernetes-discovery \
    djerfy/zabbix-kubernetes-discovery \
    --namespace zabbix-monitoring
    --set namespace.name="zabbix-monitoring" \
    --set environment.ZABBIX_ENDPOINT="zabbix-proxy.example.com" \
    --set environment.KUBERNETES_NAME="kubernetes-cluster-name"
```

### Uninstall

To uninstall/delete the `zabbix-kubernetes-discovery` deployment:

```bash
$ helm list -n zabbix-monitoring
$ helm delete -n zabbix-monitoring zabbix-kubernetes-discovery
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Commands

```
usage: zabbix-kubernetes-discovery.py [-h]
    [--zabbix-timeout ZABBIX_TIMEOUT]
    --zabbix-endpoint ZABBIX_ENDPOINT
    --kubernetes-name KUBERNETES_NAME
    --monitoring-mode {volume,deployment,daemonset,node,statefulset,cronjob}
    --monitoring-type {discovery,item,json}
    [--object-name OBJECT_NAME]
    [--match-label KEY=VALUE]
    [--include-name INCLUDE_NAME]
    [--include-namespace INCLUDE_NAMESPACE]
    [--exclude-name EXCLUDE_NAME]
    [--exclude-namespace EXCLUDE_NAMESPACE]
    [--no-wait]
    [--verbose]
    [--debug]
```

## Zabbix

### Import template

Zabbix template is located in [`./zabbix/`](./zabbix/) folder on this repository.

After downloading, you need to import it as below:

1. Go to **Configuration** in menu
2. And **Templates**
3. Click **Import**
4. Select downloaded template file
5. Confirm import

![zabbix-template-import](https://raw.githubusercontent.com/djerfy/zabbix-kubernetes-discovery/main/.github/assets/zabbix-template-import.png)

### Discovery rules

* Daemonset
  * Items: 4
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Available replicas`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Current replicas`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Desired replicas`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Ready replicas`
  * Triggers: 5
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Available replicas nodata`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Current replicas nodata`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Desired replicas nodata`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Ready replicas nodata`
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Problem items nodata`
  * Graphs: 1
    * `Daemonset {#KUBERNETES_DAEMONSET_NAME}: Graph replicas`
* Deployment
  * Items: 3
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Available replicas`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Desired replicas`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Ready replicas`
  * Triggers: 5
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Available replicas nodata`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Desired replicas nodata`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Ready replicas nodata`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Problem items nodata`
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Problem number of replicas`
  * Graphs: 1
    * `Deployment {#KUBERNETES_DEPLOYMENT_NAME}: Graph replicas`
* Statefulset
  * Items: 3
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Available replicas`
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Desired replicas`
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Ready replicas`
  * Triggers: 5
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Available replicas nodata`
    * `Stetafulset {#KUBERNETES_STATEFULSET_NAME}: Desired replicas nodata`
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Ready replicas nodata`
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Problem items nodata`
    * `Statefulset {#KUBERNETES_STATEFULSET_NAME}: Problem number of replicas`
  * Graphs: 1
    * `Deployment {#KUBERNETES_STATEFULSET_NAME}: Graph replicas`
* Cronjob
  * Items: 3
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job exitcode`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job restart`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job reason`
  * Triggers: 5
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job exitcode nodata`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job restart nodata`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Job reason nodata`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Problem items nodata`
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Problem last job`
  * Graphs: 1
    * `Cronjob {#KUBERNETES_CRONJOB_NAME}: Graph jobs`
* Node
  * Items: 8
    * `Node {#KUBERNETES_NODE_NAME}: Allocatable cpu`
    * `Node {#KUBERNETES_NODE_NAME}: Allocatable memory`
    * `Node {#KUBERNETES_NODE_NAME}: Allocatable pods`
    * `Node {#KUBERNETES_NODE_NAME}: Capacity cpu`
    * `Node {#KUBERNETES_NODE_NAME}: Capacity memory`
    * `Node {#KUBERNETES_NODE_NAME}: Capacity pods`
    * `Node {#KUBERNETES_NODE_NAME}: Current pods`
    * `Node {#KUBERNETES_NODE_NAME}: Healthz`
  * Triggers: 8
    * `Node {#KUBERNETES_NODE_NAME}: Allocatable pods nodata`
    * `Node {#KUBERNETES_NODE_NAME}: Capacity pods nodata`
    * `Node {#KUBERNETES_NODE_NAME}: Current pods nodata`
    * `Node {#KUBERNETES_NODE_NAME}: Problem pods limits warning`
    * `Node {#KUBERNETES_NODE_NAME}: Problem pods limits critical`
    * `Node {#KUBERNETES_NODE_NAME}: Health nodata`
    * `Node {#KUBERNETES_NODE_NAME}: Health problem`
    * `Node {#KUBERNETES_NODE_NAME}: Problem items nodata`
  * Graphs: 1
    * `Node {#KUBERNETES_NODE_NAME}: Graph pods`
* VolumeClaim
  * Items: 6
    * `Volume {#KUBERNETES_PVC_NAME}: Available bytes`
    * `Volume {#KUBERNETES_PVC_NAME}: Capacity bytes`
    * `Volume {#KUBERNETES_PVC_NAME}: Capacity inodes`
    * `Volume {#KUBERNETES_PVC_NAME}: Free inodes`
    * `Volume {#KUBERNETES_PVC_NAME}: Used bytes`
    * `Volume {#KUBERNETES_PVC_NAME}: Used inodes`
  * Triggers: 11
    * `Volume {#KUBERNETES_PVC_NAME}: Available bytes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Capacity bytes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Capacity inodes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Consumption bytes critical`
    * `Volume {#KUBERNETES_PVC_NAME}: Consumption bytes warning`
    * `Volume {#KUBERNETES_PVC_NAME}: Consumption inodes critical`
    * `Volume {#KUBERNETES_PVC_NAME}: Consumption inodes warning`
    * `Volume {#KUBERNETES_PVC_NAME}: Free inodes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Used bytes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Used inodes nodata`
    * `Volume {#KUBERNETES_PVC_NAME}: Problem items nodata`
  * Graphs: 2
    * `Volume {#KUBERNETES_PVC_NAME}: Graph bytes`
    * `Volume {#KUBERNETES_PVC_NAME}: Graph inodes`

## Development

### Manual build

You can build Docker image manually like this:

```bash
$ docker build -t zabbix-kubernetes-discovery .
```

## Contributing

All contributions are welcome! Please fork the main branch, create a new branch and then create a pull request.
