from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class Me(BaseModel):
    """Pydantic model representing a me record."""

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "username": "John Doe",
                    "ip": "127.0.0.1",
                    "email": "john.doe@example.com",
                    "is_admin": False,
                }
            ]
        },
    )

    username: str
    ip: str
    email: EmailStr
    is_admin: bool = False
