#-------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
#-------------------------------------------------------------------------------------------------#

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Tuple, Any
import time

import agate
from dbt_common.clients import agate_helper
from dbt_common.exceptions import DbtRuntimeError, DbtDatabaseError
from dbt.adapters.contracts.connection import Connection, Credentials, AdapterResponse
from dbt.adapters.sql.connections import SQLConnectionManager as connection_cls
from dbt.adapters.events.logging import AdapterLogger
from dbt_common.events.functions import fire_event, warn_or_error
from dbt.adapters.events.types import ConnectionUsed, SQLQuery, SQLQueryStatus, TypeCodeNotFound
from dbt_common.helper_types import Port
import ibm_db_dbi

logger = AdapterLogger("db2")


@dataclass
class Db2Credentials(Credentials):
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
    port: Port = Port(50000)
    retries: int = 1

    # Db2 SSL/TLS parameters
    security: Optional[str] = None  # 'SSL' to enable SSL/TLS
    ssl_server_certificate: Optional[str] = None  # Path to server CA certificate
    ssl_client_keystore: Optional[str] = None  # Path to client keystore database
    ssl_client_keystash: Optional[str] = None  # Path to client keystash file
    ssl_client_hostname_validation: Optional[bool] = None  # Enable hostname verification

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


class Db2ConnectionManager(connection_cls):
    TYPE = "db2"

    def test_connection(self) -> None:
        """
        This method is called by `dbt debug` to verify that the connection works.
        """
        logger.debug("Running Db2 test_connection with SYSIBM.SYSDUMMY1")
        # Use proper Db2 syntax for a simple test query
        sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"
        try:
            self.add_query(sql, auto_begin=False)
            logger.debug("Db2 test_connection succeeded.")
        except Exception as e:
            logger.error(f"Db2 test_connection failed: {str(e)}")
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
    def open(cls, connection):  # noqa: C901
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

                    # Add Db2 SSL/TLS parameters if provided
                    if credentials.security:
                        # Enable SSL/TLS security
                        if credentials.security.upper() == 'SSL':
                            conn_str += "Security=SSL;"
                            logger.debug("SSL/TLS security enabled")
                        else:
                            conn_str += f"Security={credentials.security};"
                            logger.debug(f"Security mode: {credentials.security}")

                    # Add SSL server certificate (CA certificate for verification)
                    if credentials.ssl_server_certificate:
                        conn_str += f"SSLServerCertificate={credentials.ssl_server_certificate};"
                        logger.debug(f"SSL server certificate: {credentials.ssl_server_certificate}")

                    # Add SSL client keystore database
                    if credentials.ssl_client_keystore:
                        conn_str += f"SSLClientKeystoredb={credentials.ssl_client_keystore};"
                        logger.debug(f"SSL client keystore: {credentials.ssl_client_keystore}")

                    # Add SSL client keystash file
                    if credentials.ssl_client_keystash:
                        conn_str += f"SSLClientKeystash={credentials.ssl_client_keystash};"
                        logger.debug(f"SSL client keystash: {credentials.ssl_client_keystash}")

                    # Add hostname verification if specified
                    if credentials.ssl_client_hostname_validation is not None:
                        # Db2 uses SSLClientHostnameValidation parameter
                        validation_value = "true" if credentials.ssl_client_hostname_validation else "false"
                        conn_str += f"SSLClientHostnameValidation={validation_value};"
                        logger.debug(f"SSL hostname validation: {validation_value}")

                    logger.debug("Connecting with connection string (SSL params hidden)")
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
        """
        Gets a connection object and attempts to cancel any ongoing queries.
        """
        connection_name = connection.name
        db2_connection = connection.handle

        logger.info("Cancelling query '{}' ".format(connection_name))

        try:
            db2_connection.close()
        except Exception as e:
            logger.error('Error closing connection for cancel request')
            raise Exception(str(e))

        logger.info("Canceled query '{}'".format(connection_name))

    def begin(self):
        """Override to handle Db2-specific transaction behavior"""
        connection = self.get_thread_connection()
        if connection.transaction_open is True:
            logger.debug('Connection is already in a transaction')
            return

        logger.debug('Beginning a new transaction')
        connection.transaction_open = True
        # Db2 doesn't need an explicit BEGIN statement

    def commit(self):
        """Override to handle Db2-specific transaction behavior"""
        connection = self.get_thread_connection()
        if connection.transaction_open is False:
            logger.debug('No transaction was open, nothing to commit')
            return

        logger.debug('Committing transaction')
        connection.handle.commit()
        connection.transaction_open = False

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

                # If this is the debug query, modify it for Db2 syntax
                if sql.strip().lower() == 'select 1 as id':
                    logger.debug("Detected debug query, modifying for Db2 syntax")
                    sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"

                # Check if the SQL starts with BEGIN
                if sql.strip().upper().startswith('BEGIN'):
                    logger.debug("Detected BEGIN statement, removing it")
                    sql = sql.strip()[5:].strip()
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
    def _map_dbapi_type_to_name(cls, values: set) -> str:
        """Map DBAPITypeObject values to Db2 type name."""
        # STRING types
        if values & {"CHAR", "CHARACTER", "VARCHAR", "STRING", "CHARACTER VARYING", "CHAR VARYING"}:
            return "STRING"

        # INTEGER types
        if values & {"INT", "INTEGER", "SMALLINT", "BIGINT"}:
            return "INTEGER"

        # DECIMAL types
        if values & {"DECIMAL", "NUMERIC", "DEC", "NUM"}:
            return "DECIMAL"

        # TIMESTAMP types
        if "TIMESTAMP" in values:
            return "TIMESTAMP"

        # BOOLEAN
        if "BOOLEAN" in values:
            return "BOOLEAN"

        # BLOB
        if values & {"BLOB", "BINARY", "VARBINARY"}:
            return "BLOB"

        return sorted(values)[0]

    @classmethod
    def data_type_code_to_name(cls, type_code) -> str:
        # DBAPITypeObject handling
        if hasattr(type_code, "values"):
            try:
                values = {v.upper() for v in type_code.values}
                return cls._map_dbapi_type_to_name(values)
            except Exception:
                pass

        # Fallbacks (keep minimal and safe)
        if isinstance(type_code, bool):
            return "BOOLEAN"

        if isinstance(type_code, bytes):
            return "BLOB"

        type_code_str = str(type_code)
        warn_or_error(TypeCodeNotFound(type_code=type_code_str))
        return "STRING"

    def execute(
        self, sql: str, auto_begin: bool = False, fetch: bool = False, limit: Optional[int] = None
    ) -> Tuple[AdapterResponse, agate.Table]:
        sql = self._add_query_comment(sql)

        # If this is the debug query, modify it for Db2 syntax
        if sql.strip().lower() == 'select 1 as id':
            logger.debug("Detected debug query in execute, modifying for Db2 syntax")
            sql = "SELECT 1 FROM SYSIBM.SYSDUMMY1"

        # Check if the SQL starts with BEGIN
        if sql.strip().upper().startswith('BEGIN'):
            logger.debug("Detected BEGIN statement in execute, removing it")
            sql = sql.strip()[5:].strip()

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
