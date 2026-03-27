"""Secret store helper — separated so providers remain free of workspace SDK imports."""
import base64 as _base64


def get_secret(scope: str, key: str) -> str:
    from common.authentication.workspace import WorkspaceAuthentication
    client = WorkspaceAuthentication().client
    encoded = client.secrets.get_secret(scope=scope, key=key).value
    return _base64.b64decode(encoded).decode("utf-8")
