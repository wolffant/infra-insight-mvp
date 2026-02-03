from kubernetes import client, config
from worker.core.config import settings

def load_client():
    mode = (settings.K8S_MODE or "incluster").lower()
    if mode == "kubeconfig":
        config.load_kube_config(config_file=settings.KUBECONFIG_PATH)
    else:
        config.load_incluster_config()
    return client.CoreV1Api()

def namespace_filter():
    if not settings.K8S_NAMESPACE_FILTER:
        return None
    return {x.strip() for x in settings.K8S_NAMESPACE_FILTER.split(",") if x.strip()}
