from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes import api_router
from common.factories import AppFactory
from common.config import (
    is_development, 
    get_cors_origins, 
    get_static_files_directory,
)


class SPAStaticFiles(StaticFiles):
    """
    Serves a Vue/React SPA by falling back to index.html for any path that
    does not match a real file, allowing client-side routing to take over.
    """
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (StarletteHTTPException, Exception) as e:
            if getattr(e, "status_code", None) == 404 or isinstance(e, FileNotFoundError):
                return await super().get_response("index.html", scope)
            raise


app = AppFactory().create_app()
app.include_router(api_router)


if is_development():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
else:
    try:
        static_dir = get_static_files_directory()
        app.mount("/", SPAStaticFiles(directory=static_dir, html=True), name="static")
    except Exception:
        pass