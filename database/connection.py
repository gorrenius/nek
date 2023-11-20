from sqlalchemy import create_engine
from config import (
    PG_HOST, PG_PORT, USE_SSH, PG_DB, PG_USER, PG_PASS
)
from ssh import SSH


class ConnectionDB:

    def __init__(self):
        self.client = SSH()
        self.engine = None
        self.conn = None

    def set_connection(self):

        local_host, local_port = PG_HOST, PG_PORT
        if USE_SSH:
            # print(f'DEFAULT SSH host:{local_host}   SSH port:{local_port}')
            local_host, local_port = self.client.ssh_session()
            # print(f'SSH host:{local_host}   SSH port:{local_port}')
        pg_url = 'postgresql+psycopg2://{user}:{passw}@{host}:{port}/{db}?application_name=mms' \
            .format(user=PG_USER, passw=PG_PASS, host=local_host, port=local_port, db=PG_DB)

        self.engine = create_engine(
            pg_url, echo=False, isolation_level="AUTOCOMMIT", client_encoding='utf8'
        )
        self.conn = self.engine.connect()
        return self.conn

    def close_connection(self):
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        if self.client:
            self.client.ssh_close()
