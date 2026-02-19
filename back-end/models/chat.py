
from typing import Optional
from pydantic import BaseModel, ConfigDict

class QueryResult(BaseModel):
    """Represents a query extracted from a Genie response."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "query": "SELECT * FROM customers",
                    "description": "This query returns all customers from the customers table",
                }
            ]
        },
    )
    query: str
    description: Optional[str] = None

class QueryData(BaseModel):
    """Represents the data returned from executing a query."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "columns": ["customerID", "first_name", "last_name", "email_address", "phone_number", "address", "city", "state", "country", "continent", "postal_zip_code", "gender"],
                    "data": [[1, "Ada", "Lovelace", "ada@example.com", "+1-555-0100", "123 Main St", "London", "", "UK", "Europe", 90210, "F"]],
                    "row_count": 1,
                }
            ]
        },
    )
    columns: list[str]
    data: list
    row_count: int

class GenieResponse(BaseModel):
    """Represents the full response from a Genie interaction."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "status": "completed",
                    "response": "The customer with ID 1 is Ada Lovelace",
                    "conversation_id": "1234567890",
                    "message_id": "1234567890",
                    "query_result": {
                        "query": "SELECT * FROM customers",
                        "description": "This query returns all customers from the customers table",
                    },
                    "query_data": {
                        "columns": ["customerID", "first_name", "last_name", "email_address", "phone_number", "address", "city", "state", "country", "continent", "postal_zip_code", "gender"],
                        "data": [[1, "Ada", "Lovelace", "ada@example.com", "+1-555-0100", "123 Main St", "London", "", "UK", "Europe", 90210, "F"]],
                        "row_count": 1,
                    }
                }
            ]
        },
    )
    success: bool
    status: str
    response: Optional[str] = None
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    query_result: Optional[QueryResult] = None
    query_data: Optional[QueryData] = None
