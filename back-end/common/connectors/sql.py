from common.authentication.sql import SQLAuthentication
from pandas import DataFrame
import asyncio
from typing import Optional

class SQLConnector:
    """
    A connector for interacting with Databricks SQL.
    
    This class provides functionality to:
    - Execute SQL statements synchronously and asynchronously
    
    The class uses SQLAuthentication for secure access to Databricks SQL.
    
    Attributes:
        client: Authenticated Databricks SQL client instance
    """
    def __init__(self, bearer: Optional[str] = None) -> None:
        """Initialize SQLConnector class with an authenticated Databricks client."""
        self.client = SQLAuthentication(bearer=bearer).client

    async def run_sql_statement_async(self, statement: str) -> Optional[DataFrame]:
        """
        Execute a SQL statement asynchronously and return results as a DataFrame.
        
        This method:
        1. Executes the SQL statement asynchronously using Databricks cursor
        2. Converts the result to an Arrow table
        3. Returns the data as a pandas DataFrame
        
        Args:
            statement (str): The SQL statement to execute
            
        Returns:
            Optional[DataFrame]: Results as a pandas DataFrame, or None if no results
            
        Raises:
            Exception: If there's an error executing the SQL statement
            
        Note:
            This method is non-blocking and suitable for long-running queries
        """
        with self.client.cursor() as cursor:
            call = cursor.execute_async(statement)
            await asyncio.to_thread(lambda: call.get_async_execution_result())
            return await asyncio.to_thread(lambda: call.fetchall_arrow().to_pandas())
            
    def run_sql_statement(self, statement: str) -> Optional[DataFrame]:
        """
        Execute a SQL statement synchronously and return results as a DataFrame.
        
        This method:
        1. Executes the SQL statement using Databricks cursor
        2. Converts the result to an Arrow table
        3. Returns the data as a pandas DataFrame
        
        Args:
            statement (str): The SQL statement to execute
            
        Returns:
            Optional[DataFrame]: Results as a pandas DataFrame, or None if no results
            
        Raises:
            Exception: If there's an error executing the SQL statement
            
        Note:
            This method is blocking and will wait for the query to complete
            For long-running queries, prefer run_sql_statement_async
        """
        with self.client.cursor() as cursor:
            cursor.execute(statement)
            return cursor.fetchall_arrow().to_pandas()
