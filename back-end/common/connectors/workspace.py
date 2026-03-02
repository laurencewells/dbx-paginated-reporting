from typing import Optional
from common.authentication.workspace import WorkspaceAuthentication
from common.logger import log as L

class WorkspaceConnector:
    """
    Connector class for interacting with Databricks workspace services.
    
    This class manages the authenticated connection to the Databricks Workspace API
    and provides operations such as health checks and warehouse lookups.
    
    Attributes:
        auth: WorkspaceAuthentication instance
        client: Databricks workspace client
    """
    
    def __init__(self, bearer: Optional[str] = None) -> None:
        """
        Initialize WorkspaceConnector with authentication.
        
        Args:
            bearer (str, optional): Bearer token for direct authentication.
                                  If not provided, other auth methods will be attempted.
            
        Raises:
            ValueError: If authentication fails
        """
        self.auth = WorkspaceAuthentication(bearer=bearer)
        self.client = self.auth.client
    
    
    def health_check(self) -> bool:
        """
        Perform a health check on the workspace connection.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            # Try to get current user as a simple health check
            self.client.current_user.me()
            L.info("Workspace connection health check passed")
            return True
        except Exception as e:
            L.error(f"Workspace health check failed: {e}")
            return False
        
    def get_warehouse_id_by_name(self, cluster_name: str) -> Optional[str]:
        """
        Returns the ID of a SQL warehouse (cluster) in Databricks.
        Args:
            cluster_name (str): The name of the SQL cluster (SQL warehouse) to find the ID for.
            Returns:
            str: The ID of the SQL cluster (SQL warehouse) if found, otherwise None.
            Raises ValueError if the cluster is not found.
        """
        try:
            warehouses = self.client.warehouses.list()
            for w in warehouses:
                if w.name == cluster_name:
                    return w.id
        except Exception as e:
            L.error(f"Error getting warehouse ID by name: {e}")
            raise
        return None
