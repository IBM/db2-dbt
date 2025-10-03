from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Tuple, Any
import time

import agate
from dbt_common.clients import agate_helper
from dbt_common.exceptions import DbtRuntimeError, DbtDatabaseError
from dbt.adapters.contracts.connection import Connection, Credentials
from dbt.adapters.sql.connections import SQLConnectionManager as connection_cls
from dbt.adapters.events.logging import AdapterLogger
from dbt_common.events.functions import fire_event, warn_or_error
from dbt.adapters.events.types import ConnectionUsed, SQLQuery, SQLQueryStatus, TypeCodeNotFound
from dbt.adapters.contracts.connection import Connection, AdapterResponse
from dbt_common.helper_types import Port
import ibm_db, ibm_db_dbi

logger = AdapterLogger("db2")


@dataclass
class DB2Credentials(Credentials):
    """
    Defines database specific credentials that get added to
    profiles.yml to connect to new adapter
    """

    dsn: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    schema: Optional[str] = None
    host: Optional[str] = None
    port: Port = Port(5480)
    retries: int = 1

    _ALIASES = {"dbname": "database", "user": "username", "pass": "password"}

    @property
    def type(self):
        """Return name of adapter."""
        return "db2"

    @property
    def unique_field(self):
        """
        Hashed and included in anonymous telemetry to track adapter adoption.
        Pick a field that can uniquely identify one team/organization building with this adapter
        """
        return self.host

    def _connection_keys(self):
        """
        List of keys to display in the `dbt debug` output.
        """
        return (
            ("dsn", "username")
            if self.dsn
            else ("host", "port", "database", "schema", "username")
        )


class DB2ConnectionManager(connection_cls):
    TYPE = "db2"

    def test_connection(self) -> None:
        """
        This method is called by `dbt debug` to verify that the connection works.
        """
        logger.debug("Running DB2 test_connection with SYSIBM.SYSDUMMY1")
        # Use proper DB2 syntax for a simple test query
        sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"
        try:
            self.add_query(sql, auto_begin=False)
            logger.debug("DB2 test_connection succeeded.")
        except Exception as e:
            logger.error(f"DB2 test_connection failed: {str(e)}")
            raise

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except ibm_db_dbi.ProgrammingError as e:
            logger.error("Db2 backend responded with: {}", str(e))
            raise DbtRuntimeError(str(e)) from e

        except ibm_db_dbi.DatabaseError as e:
            logger.debug("Db2 error: {}", str(e))
            try:
                self.rollback_if_open()
            except ibm_db_dbi.DatabaseError:
                logger.error("Failed to release connection!")

            # Fixed: unpacking error message safely
            error_message = str(e)
            raise DbtDatabaseError(error_message) from e

        except Exception as e:
            logger.debug("Error running SQL: {}", sql)
            logger.debug("Rolling back transaction.")
            self.rollback_if_open()
            if isinstance(e, DbtRuntimeError):
                raise
            raise DbtRuntimeError(str(e)) from e

    @classmethod
    def open(cls, connection):
        logger.debug("db2 adapter: Connection is about to open.")

        # ✅ Skip if already open and handle is valid
        if connection.state == "open" and connection.handle is not None:
            try:
                connection.handle.cursor()  # Test if it's still usable
                logger.debug("Connection is already open and valid, skipping open.")
                return connection
            except Exception as e:
                logger.warning(f"Existing connection is open but unusable: {e}")
                # Fall through to reconnect

        credentials = cls.get_credentials(connection.credentials)

        def connect():
            try:
                if credentials.dsn:
                    logger.debug("Using DSN for connection.")
                    conn = ibm_db_dbi.connect(credentials.dsn, "", "")
                else:
                    conn_str = (
                        f"DATABASE={credentials.database};"
                        f"HOSTNAME={credentials.host};"
                        f"PORT={credentials.port};"
                        f"PROTOCOL=TCPIP;"
                        f"UID={credentials.username};"
                        f"PWD={credentials.password};"
                    )
                    logger.debug(f"Connecting with connection string: {conn_str}")
                    conn = ibm_db_dbi.connect(conn_str, "", "")
                
                if not hasattr(conn, 'cursor'):
                    raise DbtRuntimeError("Connection object lacks 'cursor()' method")
                return conn
            except Exception as e:
                logger.error(f"Failed to connect: {e}")
                raise

        retryable_exceptions = [ibm_db_dbi.DatabaseError]

        # 🛠 Retry only if we actually need to connect
        dbt_conn = cls.retry_connection(
            connection,
            connect=connect,
            logger=logger,
            retry_limit=credentials.retries,
            retryable_exceptions=retryable_exceptions,
        )

        connection.handle = dbt_conn.handle
        connection.state = "open"
        return connection

    def cancel(self, connection):
        """Attempt to cancel ongoing query"""
        connection.handle.close()

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    @classmethod
    def get_response(cls, cursor) -> AdapterResponse:
        return AdapterResponse("OK", rows_affected=cursor.rowcount)

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        connection = self.get_thread_connection()
        if auto_begin and not connection.transaction_open:
            self.begin()

        fire_event(ConnectionUsed(conn_type=self.TYPE, conn_name=connection.name))

        with self.exception_handler(sql):
            log_sql = f"{sql[:512]}..." if abridge_sql_log else sql
            fire_event(SQLQuery(conn_name=connection.name, sql=log_sql))
            pre = time.time()
            logger.debug(f"Calling .cursor() on connection.handle of type: {type(connection.handle)}")

            # Check if handle has cursor method
            if connection.handle and hasattr(connection.handle, 'cursor'):
                # Use Any type to bypass type checking for the cursor method
                from typing import cast, Any
                db_conn = cast(Any, connection.handle)
                cursor = db_conn.cursor()
                
                # If this is the debug query, modify it for DB2 syntax
                if sql.strip().lower() == 'select 1 as id':
                    logger.debug("Detected debug query, modifying for DB2 syntax")
                    sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"
            else:
                error_msg = f"Connection handle is invalid or missing cursor method. Handle type: {type(connection.handle)}"
                logger.error(error_msg)
                raise DbtRuntimeError(error_msg)

            if bindings:
                cursor.execute(sql, bindings)
            else:
                cursor.execute(sql)

            while cursor.description is None:
                break

            fire_event(
                SQLQueryStatus(
                    status=str(self.get_response(cursor)),
                    elapsed=round((time.time() - pre), 2),
                )
            )

            return connection, cursor

    @classmethod
    def data_type_code_to_name(cls, type_code) -> str:
        name_map = {
            int: "INTEGER",
            str: "VARCHAR",
            float: "FLOAT",
            bool: "BOOLEAN",
            bytes: "BLOB",
        }
        if type(type_code) in name_map:
            return name_map[type(type_code)]
        else:
            warn_or_error(TypeCodeNotFound(type_code=type_code))
            return f"unknown type_code {type_code}"

    def execute(
        self, sql: str, auto_begin: bool = False, fetch: bool = False, limit: Optional[int] = None
    ) -> Tuple[AdapterResponse, agate.Table]:
        sql = self._add_query_comment(sql)
        
        # If this is the debug query, modify it for DB2 syntax
        if sql.strip().lower() == 'select 1 as id':
            logger.debug("Detected debug query in execute, modifying for DB2 syntax")
            sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"
        
        try:
            connection, cursor = self.add_query(sql, auto_begin)
            response = self.get_response(cursor)

            if fetch:
                if cursor.description is not None:
                    table = self.get_result_from_cursor(cursor, limit)
                else:
                    table = agate_helper.empty_table()
            else:
                table = agate_helper.empty_table()

            return response, table
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            logger.debug(f"Problematic SQL: {sql}")
            raise
