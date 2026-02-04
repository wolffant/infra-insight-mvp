from kubernetes import client, config
from worker.core.config import settings

def load_client():
    mode = (settings.K8S_MODE or "incluster").lower()
    try:
        if mode == "kubeconfig":
            config.load_kube_config(config_file=settings.KUBECONFIG_PATH)
        elif mode == "incluster":
            config.load_incluster_config()
        else:
            print(f"Warning: Unknown K8S_MODE '{mode}'. K8s ingestion will be skipped.")
            return None
        return client.CoreV1Api()
    except Exception as e:
        print(f"Warning: Could not load Kubernetes config ({e}). K8s ingestion will be skipped.")
        return None

def namespace_filter():
    if not settings.K8S_NAMESPACE_FILTER:
        return None
    return {x.strip() for x in settings.K8S_NAMESPACE_FILTER.split(",") if x.strip()}
