from pyzabbix import ZabbixMetric

def zabbixItemNode(clustername, nodes=[]):
    """
    description: create a item for node
    return: class ZabbixMetric
    """
    sender = []

    for node in nodes:
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.healthz[{node['name']}]", node['status']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.cpu[{node['name']}]", node['capacity']['cpu']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.memory[{node['name']}]", node['capacity']['memory']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.capacity.pods[{node['name']}]", node['capacity']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.cpu[{node['name']}]", node['allocatable']['cpu']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.memory[{node['name']}]", node['allocatable']['memory']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.allocatable.pods[{node['name']}]", node['allocatable']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.pods[{node['name']}]", node['current']['pods']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.podsUsed[{node['name']}]", node['current']['pods_used']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.node.current.podsFree[{node['name']}]", node['current']['pods_free']),)

    return sender


def zabbixItemDaemonset(clustername, daemonsets=[]):
    """
    description: create a item for daemonset, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for daemonset in daemonsets:
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.desiredReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['desired']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.currentReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['current']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.availableReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.daemonset.readyReplicas[{daemonset['namespace']},{daemonset['name']}]", daemonset['replicas']['ready']),)

    return sender


def zabbixItemVolume(clustername, volumes=[]):
    """
    description: create a item for persistent volume claim, per namespace
    return: class ZabbixMetric
    """
    sender = []

    for volume in volumes: 
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.availableBytes[{volume['namespace']},{volume['name']}]", volume['availableBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.capacityBytes[{volume['namespace']},{volume['name']}]", volume['capacityBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.usedBytes[{volume['namespace']},{volume['name']}]", volume['usedBytes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodesFree[{volume['namespace']},{volume['name']}]", volume['inodesFree']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodes[{volume['namespace']},{volume['name']}]", volume['inodes']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.volumeclaim.inodesUsed[{volume['namespace']},{volume['name']}]", volume['inodesUsed']),)

    return sender


def zabbixItemDeployment(clustername, deployments=[]):
    """
    description: create a item for deployment, per namespace
    return: class ZabbixResponse
    """
    sender = []

    for deployment in deployments:
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.availableReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.readyReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['ready']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.deployment.desiredReplicas[{deployment['namespace']},{deployment['name']}]", deployment['replicas']['desired']),)

    return sender


def zabbixItemStatefulset(clustername, statefulsets=[]):
    """
    description: create a item for statefulset, per namespace
    return: class ZabbixResponse
    """
    sender = []

    for statefulset in statefulsets:
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.availableReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['available']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.readyReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['ready']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.statefulset.desiredReplicas[{statefulset['namespace']},{statefulset['name']}]", statefulset['replicas']['desired']),)

    return sender


def zabbixItemCronjob(clustername, cronjobs=[]):
    """
    description: create a item for cronjob, per namespace
    return: class ZabbixResponse
    """
    sender = []

    for cronjob in cronjobs:
        sender.append(ZabbixMetric(clustername, f"kubernetes.cronjob.status[{cronjob['namespace']},{cronjob['name']}]", cronjob['status']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.cronjob.reason[{cronjob['namespace']},{cronjob['name']}]", cronjob['last_job']['reason']),)
        sender.append(ZabbixMetric(clustername, f"kubernetes.cronjob.message[{cronjob['namespace']},{cronjob['name']}]", cronjob['last_job']['message']),)

    return sender
