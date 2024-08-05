# Zabbix Kubernetes Discovery Helm Chart

This directory contains a chart for Kubernetes monitoring for Zabbix.
See [the README.md there](./zabbix-kubernetes-discovery/README.md) for
instructions on how to use it.

## Publishing

We use Github pages to publish the Helm chart as a versioned package. The
tarballs and index.yaml file are updated automatically (Github Actions).

## Prerequisites

* Kubernetes v1.19+
* Helm 3.2.0+

## Install

```bash
$ helm repo add djerfy https://djerfy.github.io/helm-charts
$ helm upgrade --install zabbix-kubernetes-discovery \
    djerfy/zabbix-kubernetes-discovery \
    --namespace zabbix-monitoring
    --set namespace.name="zabbix-monitoring" \
    --set environment.ZABBIX_ENDPOINT="zabbix-proxy.example.com" \
    --set environment.KUBERNETES_NAME="kubernetes-cluster-name"
```

## Uninstall

```bash
$ helm delete zabbix-kubernetes-discovery \
    --namespace zabbix-monitoring
```

## Parameters

| Name                                              | Type    | Value                                                       |
|---------------------------------------------------|---------|-------------------------------------------------------------|
| `namespace.name`                                  | string  | `zabbix-monitoring`                                         |
| `rbac.create`                                     | boolean | `true`                                                      |
| `rbac.name`                                       | string  | `zabbix-kubernetes-discovery`                               |
| `rbac.rolebinding`                                | string  | `zabbix-kubernetes-discovery`                               |
| `serviceAccount.create`                           | boolean | `true`                                                      |
| `serviceAccount.name`                             | string  | `zabbix-kubernetes-discovery`                               |
| `deployment.name`                                 | string  | `zabbix-kubernetes-discovery`                               |
| `deployment.image.name`                           | string  | `ghcr.io/djerfy/zabbix-kubernetes-discovery:v1.4.17`        |
| `deployment.image.pullPolicy`                     | string  | `IfNotPresent`                                              |
| `deployment.replicas`                             | integer | `1`                                                         |
| `deployment.strategy`                             | string  | `Recreate`                                                  |
| `environment.ZABBIX_ENDPOINT`                     | string  | `""`                                                        |
| `environment.KUBERNETES_NAME`                     | string  | `""`                                                        |
| `zabbix.timeout`                                  | integer | `5`                                                         |
| `zabbix.verbose`                                  | string  | `no`                                                        |
| `zabbix.debug`                                    | string  | `no`                                                        |
| `crontab.name`                                    | string  | `zabbix-kubernetes-discovery`                               |
| `crontab.node.discovery`                          | string  | `*/30 * * * *`                                                 |
| `crontab.node.item`                               | string  | `*/2 * * * *`                                               |
| `crontab.daemonset.discovery`                     | string  | `*/30 * * * *`                                                 |
| `crontab.daemonset.item`                          | string  | `*/2 * * * *`                                               |
| `crontab.volume.discovery`                        | string  | `*/30 * * * *`                                                 |
| `crontab.volume.item`                             | string  | `*/2 * * * *`                                               |
| `crontab.deployment.discovery`                    | string  | `*/30 * * * *`                                                 |
| `crontab.deployment.item`                         | string  | `*/2 * * * *`                                               |
| `crontab.statefulset.discovery`                   | string  | `*/30 * * * *`                                                 |
| `crontab.statefulset.item`                        | string  | `*/2 * * * *`                                               |
| `crontab.cronjob.discovery`                       | string  | `*/30 * * * *`                                                 |
| `crontab.cronjob.item`                            | string  | `*/2 * * * *`                                               |
| `monitoring.node.match_label`                     | string  | `""`                                                        |
| `monitoring.node.include_name`                    | string  | `""`                                                        |
| `monitoring.node.exclude_name`                    | string  | `""`                                                        |
| `monitoring.daemonset.match_label`                | string  | `""`                                                        |
| `monitoring.daemonset.include_name`               | string  | `""`                                                        |
| `monitoring.daemonset.include_namespace`          | string  | `""`                                                        |
| `monitoring.daemonset.exclude_name`               | string  | `""`                                                        |
| `monitoring.daemonset.exclude_namespace`          | string  | `""`                                                        |
| `monitoring.volume.match_label`                   | string  | `""`                                                        |
| `monitoring.volume.include_name`                  | string  | `""`                                                        |
| `monitoring.volume.include_namespace`             | string  | `""`                                                        |
| `monitoring.volume.exclude_name`                  | string  | `""`                                                        |
| `monitoring.volume.exclude_namespace`             | string  | `""`                                                        |
| `monitoring.deployment.match_label`               | string  | `""`                                                        |
| `monitoring.deployment.include_name`              | string  | `""`                                                        |
| `monitoring.deployment.include_namespace`         | string  | `""`                                                        |
| `monitoring.deployment.exclude_name`              | string  | `""`                                                        |
| `monitoring.deployment.exclude_namespace`         | string  | `""`                                                        |
| `monitoring.statefulset.match_label`              | string  | `""`                                                        |
| `monitoring.statefulset.include_name`             | string  | `""`                                                        |
| `monitoring.statefulset.include_namespace`        | string  | `""`                                                        |
| `monitoring.statefulset.exclude_name`             | string  | `""`                                                        |
| `monitoring.statefulset.exclude_namespace`        | string  | `""`                                                        |
| `monitoring.cronjob.match_label`                  | string  | `""`                                                        |
| `monitoring.cronjob.include_name`                 | string  | `""`                                                        |
| `monitoring.cronjob.include_namespace`            | string  | `""`                                                        |
| `monitoring.cronjob.exclude_name`                 | string  | `""`                                                        |
| `monitoring.cronjob.exclude_namespace`            | string  | `""`                                                        |
| `resources.requests.cpu`                          | string  | `50m`                                                       |
| `resources.requests.memory`                       | string  | `128Mi`                                                     |
| `resources.limits.cpu`                            | string  | `1000m`                                                     |
| `resources.limits.memory`                         | string  | `1Gi`                                                       |
| `nodeSelector`                                    | dict    | `{}`                                                        |
| `tolerations`                                     | list    | `[]`                                                        |
| `affinity`                                        | dict    | `{}`                                                        |
