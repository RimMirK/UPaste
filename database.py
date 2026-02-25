import secrets
import time as time_module
import aiosqlite


class DB:
    path: str
    con: aiosqlite.Connection

    def __init__(self, path) -> None:
        self.path = path
        self.con = None

    async def bootstrap(self, create_tables=True) -> None:
        if not self.con:
            self.con = await aiosqlite.connect(self.path)

        if create_tables:
            await self.create_tables()

    async def force_bootstrap(self, create_tables=True) -> None:
        if self.con:
            await self.con.close()

        self.con = await aiosqlite.connect(self.path)

        if create_tables:
            await self.create_tables()

    async def teardown(self) -> None:
        await self.con.close()

    async def sql(
        self,
        sql: str,
        asdict: bool = False,
        return_cursor: bool = False,
        **params
    ):
        cursor = await self.con.execute(sql, params)
        rows = await cursor.fetchall()

        if asdict and return_cursor:
            raise ValueError("Cannot return cursor and asdict at the same time.")

        if asdict:
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

        await self.con.commit()

        if return_cursor:
            return cursor

        return rows

    # =====================================================

    async def create_tables(self):

        await self.sql("""
            CREATE TABLE IF NOT EXISTS pastes (
                id              INTEGER PRIMARY KEY NOT NULL,
                paste_id        TEXT    NOT NULL UNIQUE,
                content         TEXT    NOT NULL,
                ext             TEXT,
                ip              TEXT    NOT NULL,
                time            NUMERIC NOT NULL,
                delete_token    TEXT    NOT NULL
            );
        """)

    # =====================================================

    async def add_paste(self, content, ip, ext=None) -> tuple[str, str]:
        while True:
            paste_id = secrets.token_urlsafe(6)
            r = await self.sql(
                "SELECT 1 FROM pastes WHERE paste_id = :id",
                id=paste_id
            )
            if not r:
                break

        delete_token = secrets.token_urlsafe(16)
        time = time_module.time()

        await self.sql(
            """
            INSERT INTO pastes
                (paste_id, content, ip, time, ext, delete_token)
            VALUES
                (:id, :content, :ip, :time, :ext, :token)
            """,
            id=paste_id,
            content=content,
            ip=ip,
            time=time,
            ext=ext,
            token=delete_token
        )

        return paste_id, delete_token

    # =====================================================

    async def get_paste(self, id):
        r = await self.sql(
            "SELECT content, ext FROM pastes WHERE paste_id=:id",
            id=id
        )
        return (*r[0],) if r else None

    async def get_paste_full(self, id):
        r = await self.sql(
            "SELECT * FROM pastes WHERE paste_id=:id",
            id=id
        )
        return r[0] if r else None

    async def check_delete_token(self, id, token):
        r = await self.sql(
            "SELECT delete_token FROM pastes WHERE paste_id=:id",
            id=id
        )
        return r and r[0][0] == token

    async def delete_paste(self, id):
        await self.sql(
            "DELETE FROM pastes WHERE paste_id=:id",
            id=id
        )
        
    async def update_paste(self, paste_id, content, ext):
        await self.sql(
            """
            UPDATE pastes
            SET content=:content, ext=:ext
            WHERE paste_id=:id
            """,
            id=paste_id,
            content=content,
            ext=ext
        )