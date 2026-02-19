from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from common.logger import log as L
from models.image import Image, ImageCreate, ImageUpdate


_COLUMNS = "id, project_id, filename, mime_type, size_bytes, created_at, updated_at"


class ImagesRepository:
    """Data-access layer for the images table in Lakebase."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    async def get_all(self, project_id: UUID) -> List[Image]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM images WHERE project_id = :pid ORDER BY created_at",
            {"pid": str(project_id)},
        )
        rows = result.fetchall()
        return [self._row_to_model(r) for r in rows]

    async def count(self, project_id: UUID) -> int:
        result = await self._require_connector().execute_query(
            "SELECT COUNT(*) FROM images WHERE project_id = :pid",
            {"pid": str(project_id)},
        )
        return result.scalar() or 0

    async def get_by_id(self, image_id: UUID) -> Optional[Image]:
        result = await self._require_connector().execute_query(
            f"SELECT {_COLUMNS} FROM images WHERE id = :id",
            {"id": str(image_id)},
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def get_data(self, image_id: UUID) -> Optional[tuple]:
        """Return (mime_type, data_base64) for serving the raw image."""
        result = await self._require_connector().execute_query(
            "SELECT mime_type, data_base64 FROM images WHERE id = :id",
            {"id": str(image_id)},
        )
        row = result.fetchone()
        return (row[0], row[1]) if row else None

    async def create(self, data: ImageCreate) -> Image:
        result = await self._require_connector().execute_query(
            "INSERT INTO images (project_id, filename, mime_type, size_bytes, data_base64) "
            "VALUES (:project_id, :filename, :mime_type, :size_bytes, :data_base64) "
            f"RETURNING {_COLUMNS}",
            {
                "project_id": str(data.project_id),
                "filename": data.filename,
                "mime_type": data.mime_type,
                "size_bytes": data.size_bytes,
                "data_base64": data.data_base64,
            },
        )
        row = result.fetchone()
        return self._row_to_model(row)

    async def update(self, image_id: UUID, data: ImageUpdate) -> Optional[Image]:
        sets: list[str] = []
        params: dict = {"id": str(image_id)}

        if data.filename is not None:
            sets.append("filename = :filename")
            params["filename"] = data.filename

        if not sets:
            return await self.get_by_id(image_id)

        sets.append("updated_at = NOW()")
        set_clause = ", ".join(sets)

        result = await self._require_connector().execute_query(
            f"UPDATE images SET {set_clause} WHERE id = :id "
            f"RETURNING {_COLUMNS}",
            params,
        )
        row = result.fetchone()
        return self._row_to_model(row) if row else None

    async def delete(self, image_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            "DELETE FROM images WHERE id = :id",
            {"id": str(image_id)},
        )
        return result.rowcount > 0

    @staticmethod
    def _row_to_model(row) -> Image:
        return Image(
            id=row[0],
            project_id=row[1],
            filename=row[2],
            mime_type=row[3],
            size_bytes=row[4],
            created_at=row[5],
            updated_at=row[6],
        )
