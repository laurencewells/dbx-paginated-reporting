import os
from databricks.sdk import WorkspaceClient
from common.logger import log as L

class WorkspaceAuthentication:
    """
    Handles authentication to Databricks workspace services using various authentication methods.
    
    This class supports multiple authentication methods:
    1. Bearer token authentication (provided directly)
    2. Personal access token (via DATABRICKS_TOKEN environment variable)
    3. Service principal OAuth (via client ID and secret environment variables)
    
    The class automatically selects the appropriate authentication method based on
    available credentials, with the following precedence:
    1. Bearer token (if provided in constructor)
    2. Personal access token (if DATABRICKS_TOKEN exists)
    3. Service principal (if DATABRICKS_CLIENT_ID exists)
    
    Required Environment Variables:
        DATABRICKS_HOST: The Databricks workspace hostname
        DATABRICKS_WAREHOUSE_PATH: The HTTP path to the SQL warehouse
        
    Optional Environment Variables (one set required):
        DATABRICKS_TOKEN: Personal access token for authentication
        or
        DATABRICKS_CLIENT_ID: OAuth client ID for service principal
        DATABRICKS_CLIENT_SECRET: OAuth client secret for service principal
        
    Attributes:
        server (str): Databricks workspace hostname
        path (str): HTTP path to SQL warehouse
        bearer (str): Optional bearer token for direct authentication
        client: Authenticated Databricks workspace client
    """
    
    def __init__(self, bearer: str = None) -> None:
        """
        Initialize Databricks workspace authentication with optional bearer token.
        
        Args:
            bearer (str, optional): Bearer token for direct authentication.
                                  If not provided, other auth methods will be attempted.
        
        Raises:
            ValueError: If no valid authentication method is available
        """
        self.server = os.getenv("DATABRICKS_HOST")
        if not self.server:
            raise ValueError("DATABRICKS_HOST environment variable is required for workspace operations")
        self.bearer = bearer
        self.client = self._get_client()
    
    def _get_client(self) -> WorkspaceClient:
        """
        Get an authenticated Databricks workspace client.

        Returns:
            WorkspaceClient: Authenticated Databricks workspace client

        Raises:
            ValueError: If no valid authentication method is available
        """
        if self.bearer:
            L.info("Using bearer authentication for workspace")
            return WorkspaceClient(
                host=self.server,
                token=self.bearer,
                auth_type="pat",
            )
        
        if "DATABRICKS_TOKEN" in os.environ:
            L.info("Using token authentication for workspace")
            return WorkspaceClient(
                host=self.server,
                token=os.getenv("DATABRICKS_TOKEN"),
            )
        elif "DATABRICKS_CLIENT_ID" in os.environ:
            L.info("Using machine authentication for workspace")
            return WorkspaceClient(
                host=self.server,
                client_id=os.getenv("DATABRICKS_CLIENT_ID"),
                client_secret=os.getenv("DATABRICKS_CLIENT_SECRET"),
            )
        else:
            raise ValueError("No authentication method provided for workspace")
