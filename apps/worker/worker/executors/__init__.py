"""
Action executors for remediation actions.
Each executor implements a specific action type.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import httpx
from datetime import datetime


class ActionExecutor(ABC):
    """Base class for action executors"""
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the action and return result"""
        pass


class CloseJiraTicketExecutor(ActionExecutor):
    """Closes Jira tickets"""
    
    def __init__(self, jira_base_url: str, jira_email: str, jira_api_token: str):
        self.jira_base_url = jira_base_url.rstrip("/")
        self.auth = (jira_email, jira_api_token)
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Close Jira tickets.
        
        params: {
            "issue_keys": ["PAI-123", "PAI-124"]
        }
        """
        issue_keys = params.get("issue_keys", [])
        results = []
        
        async with httpx.AsyncClient() as client:
            for issue_key in issue_keys:
                try:
                    # Get available transitions
                    trans_url = f"{self.jira_base_url}/rest/api/3/issue/{issue_key}/transitions"
                    trans_resp = await client.get(trans_url, auth=self.auth)
                    trans_resp.raise_for_status()
                    transitions = trans_resp.json()["transitions"]
                    
                    # Find "Done" or "Closed" transition
                    done_transition = next(
                        (t for t in transitions if t["name"].lower() in ["done", "closed", "close"]),
                        None
                    )
                    
                    if not done_transition:
                        results.append({
                            "issue_key": issue_key,
                            "success": False,
                            "error": "No 'Done' or 'Closed' transition available"
                        })
                        continue
                    
                    # Execute transition
                    url = f"{self.jira_base_url}/rest/api/3/issue/{issue_key}/transitions"
                    payload = {"transition": {"id": done_transition["id"]}}
                    resp = await client.post(url, json=payload, auth=self.auth)
                    resp.raise_for_status()
                    
                    results.append({
                        "issue_key": issue_key,
                        "success": True,
                        "transition": done_transition["name"]
                    })
                    
                except Exception as e:
                    results.append({
                        "issue_key": issue_key,
                        "success": False,
                        "error": str(e)
                    })
        
        return {
            "total": len(issue_keys),
            "succeeded": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "details": results
        }


class RestartPodExecutor(ActionExecutor):
    """Restarts Kubernetes pods"""
    
    def __init__(self, k8s_client):
        self.k8s_client = k8s_client
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restart pods by deleting them.
        
        params: {
            "pods": [
                {"name": "nginx-xyz", "namespace": "default"}
            ]
        }
        """
        from kubernetes import client
        
        pods = params.get("pods", [])
        results = []
        
        api = client.CoreV1Api(self.k8s_client)
        
        for pod_info in pods:
            try:
                pod_name = pod_info["name"]
                namespace = pod_info["namespace"]
                
                # Delete pod (will be recreated by controller)
                api.delete_namespaced_pod(
                    name=pod_name,
                    namespace=namespace,
                    body=client.V1DeleteOptions()
                )
                
                results.append({
                    "pod": pod_name,
                    "namespace": namespace,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "pod": pod_info.get("name", "unknown"),
                    "namespace": pod_info.get("namespace", "unknown"),
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "total": len(pods),
            "succeeded": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "details": results
        }


class ScaleDeploymentExecutor(ActionExecutor):
    """Scales Kubernetes deployments"""
    
    def __init__(self, k8s_client):
        self.k8s_client = k8s_client
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scale deployment.
        
        params: {
            "deployment": "nginx",
            "namespace": "default",
            "replicas": 3
        }
        """
        from kubernetes import client
        
        deployment = params["deployment"]
        namespace = params["namespace"]
        replicas = params["replicas"]
        
        try:
            api = client.AppsV1Api(self.k8s_client)
            
            # Get current deployment
            dep = api.read_namespaced_deployment(deployment, namespace)
            
            # Update replicas
            dep.spec.replicas = replicas
            api.patch_namespaced_deployment_scale(
                name=deployment,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            
            return {
                "success": True,
                "deployment": deployment,
                "namespace": namespace,
                "replicas": replicas
            }
            
        except Exception as e:
            return {
                "success": False,
                "deployment": deployment,
                "namespace": namespace,
                "error": str(e)
            }


# Registry of executors
EXECUTOR_REGISTRY = {
    "close_jira_tickets": CloseJiraTicketExecutor,
    "restart_pods": RestartPodExecutor,
    "scale_deployment": ScaleDeploymentExecutor,
}
