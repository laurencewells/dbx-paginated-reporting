from typing import List, Optional
from uuid import UUID

from common.connectors.lakebase import LakebaseConnector, get_lakebase_connector
from common.factories.cache import app_cache
from common.logger import log as L
from models.project import Project, ProjectCreate, ProjectUpdate, ProjectShare, ProjectShareCreate


_PROJECT_COLUMNS = "id, name, user_email, is_locked, is_global, created_at, updated_at"
_SHARE_COLUMNS = "id, project_id, shared_with_email, shared_by_email, created_at"


class ProjectsRepository:
    """Data-access layer for the projects and project_shares tables."""

    def __init__(self, connector: Optional[LakebaseConnector] = None):
        self.connector = connector or get_lakebase_connector()

    def _require_connector(self) -> LakebaseConnector:
        if self.connector is None:
            raise RuntimeError(
                "Lakebase is not available. Ensure LAKEBASE_INSTANCE_NAME is configured "
                "and the database instance exists."
            )
        return self.connector

    # -- projects --------------------------------------------------------------

    async def get_all_for_user(self, user_email: str) -> List[Project]:
        """Return projects owned by or shared with the given user."""
        result = await self._require_connector().execute_query(
            """
            SELECT DISTINCT p.id, p.name, p.user_email, p.is_locked, p.is_global, p.created_at, p.updated_at
            FROM projects p
            LEFT JOIN project_shares ps ON ps.project_id = p.id
            WHERE p.user_email = :email OR ps.shared_with_email = :email OR p.is_global = TRUE
            ORDER BY p.created_at
            """,
            {"email": user_email},
        )
        rows = result.fetchall()
        return [self._row_to_project(r) for r in rows]

    @app_cache.cached("project:{project_id}", ttl=60)
    async def get_by_id(self, project_id: UUID) -> Optional[Project]:
        result = await self._require_connector().execute_query(
            f"""
            SELECT {_PROJECT_COLUMNS}
            FROM projects
            WHERE id = :id
            """,
            {"id": str(project_id)},
        )
        row = result.fetchone()
        return self._row_to_project(row) if row else None

    async def create(self, data: ProjectCreate, user_email: str) -> Project:
        result = await self._require_connector().execute_query(
            f"""
            INSERT INTO projects (name, user_email)
            VALUES (:name, :email)
            RETURNING {_PROJECT_COLUMNS}
            """,
            {"name": data.name, "email": user_email},
        )
        row = result.fetchone()
        return self._row_to_project(row)

    async def update(self, project_id: UUID, data: ProjectUpdate) -> Optional[Project]:
        sets: list[str] = []
        params: dict = {"id": str(project_id)}

        if data.name is not None:
            sets.append("name = :name")
            params["name"] = data.name
        if data.is_locked is not None:
            sets.append("is_locked = :is_locked")
            params["is_locked"] = data.is_locked
        if data.is_global is not None:
            sets.append("is_global = :is_global")
            params["is_global"] = data.is_global

        if not sets:
            return await self.get_by_id(project_id)

        sets.append("updated_at = NOW()")
        set_clause = ", ".join(sets)

        result = await self._require_connector().execute_query(
            f"""
            UPDATE projects
            SET {set_clause}
            WHERE id = :id
            RETURNING {_PROJECT_COLUMNS}
            """,
            params,
        )
        row = result.fetchone()
        return self._row_to_project(row) if row else None

    async def delete(self, project_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            """
            DELETE FROM projects
            WHERE id = :id
            """,
            {"id": str(project_id)},
        )
        return result.rowcount > 0

    # -- shares ----------------------------------------------------------------

    async def get_shares(self, project_id: UUID) -> List[ProjectShare]:
        result = await self._require_connector().execute_query(
            f"""
            SELECT {_SHARE_COLUMNS}
            FROM project_shares
            WHERE project_id = :pid
            ORDER BY created_at
            """,
            {"pid": str(project_id)},
        )
        rows = result.fetchall()
        return [self._row_to_share(r) for r in rows]

    async def create_share(
        self, project_id: UUID, data: ProjectShareCreate, shared_by_email: str
    ) -> ProjectShare:
        result = await self._require_connector().execute_query(
            f"""
            INSERT INTO project_shares (project_id, shared_with_email, shared_by_email)
            VALUES (:pid, :shared_with, :shared_by)
            RETURNING {_SHARE_COLUMNS}
            """,
            {
                "pid": str(project_id),
                "shared_with": data.shared_with_email,
                "shared_by": shared_by_email,
            },
        )
        row = result.fetchone()
        return self._row_to_share(row)

    async def delete_share(self, share_id: UUID) -> bool:
        result = await self._require_connector().execute_query(
            """
            DELETE FROM project_shares
            WHERE id = :id
            """,
            {"id": str(share_id)},
        )
        return result.rowcount > 0

    async def user_has_access(self, project_id: UUID, user_email: str) -> bool:
        """Check if a user owns, has been shared, or can see a global project."""
        result = await self._require_connector().execute_query(
            """
            SELECT EXISTS(
                SELECT 1 FROM (
                    SELECT 1 FROM projects
                    WHERE id = :pid AND (user_email = :email OR is_global = TRUE)
                    UNION ALL
                    SELECT 1 FROM project_shares
                    WHERE project_id = :pid AND shared_with_email = :email
                ) sub
            ) AS has_access
            """,
            {"pid": str(project_id), "email": user_email},
        )
        row = result.fetchone()
        return bool(row and row[0])

    async def get_access_and_lock_status(
        self, project_id: UUID, user_email: str
    ) -> tuple[bool, bool]:
        """
        Single query returning (has_access, is_locked).

        Replaces the two separate calls to user_has_access + get_by_id that
        combined-access-and-lock callers previously made.
        """
        result = await self._require_connector().execute_query(
            """
            SELECT
                p.is_locked,
                EXISTS(
                    SELECT 1 FROM (
                        SELECT 1 FROM projects
                        WHERE id = :pid AND (user_email = :email OR is_global = TRUE)
                        UNION ALL
                        SELECT 1 FROM project_shares
                        WHERE project_id = :pid AND shared_with_email = :email
                    ) sub
                ) AS has_access
            FROM projects p
            WHERE p.id = :pid
            """,
            {"pid": str(project_id), "email": user_email},
        )
        row = result.fetchone()
        if not row:
            return False, False
        is_locked, has_access = row[0], row[1]
        return bool(has_access), bool(is_locked)

    # -- row mappers -----------------------------------------------------------

    @staticmethod
    def _row_to_project(row) -> Project:
        return Project(
            id=row[0],
            name=row[1],
            user_email=row[2],
            is_locked=row[3],
            is_global=row[4],
            created_at=row[5],
            updated_at=row[6],
        )

    @staticmethod
    def _row_to_share(row) -> ProjectShare:
        return ProjectShare(
            id=row[0],
            project_id=row[1],
            shared_with_email=row[2],
            shared_by_email=row[3],
            created_at=row[4],
        )
