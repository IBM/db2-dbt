import dataclasses
from multiprocessing import get_context
from unittest import TestCase, mock

import agate
from dbt.adapters.base import BaseRelation
from dbt.adapters.contracts.relation import Path
from dbt_common.context import set_invocation_context
from dbt_common.exceptions import DbtValidationError
import pytest
import ibm_db, ibm_db_dbi

from dbt.adapters.db2 import Plugin, DB2Adapter
from tests.unit.utils import (
    config_from_parts_or_dicts,
    inject_adapter,
    mock_connection,
)


class TestDB2Adapter(TestCase):
    def setUp(self):
        project_cfg = {
            "name": "X",
            "version": "0.1",
            "profile": "test",
            "project-root": "/tmp/dbt/does-not-exist",
            "config-version": 2,
        }
        profile_cfg = {
            "outputs": {
                "test": {
                    "type": "db2",
                    "dbname": "testdbt",
                    "user": "root",
                    "host": "thishostshouldnotexist",
                    "pass": "password",
                    "port": 50000,
                    "schema": "admin",
                }
            },
            "target": "test",
        }

        self.config = config_from_parts_or_dicts(project_cfg, profile_cfg)
        self.mp_context = get_context("spawn")
        self._adapter = None

    @property
    def adapter(self):
        if self._adapter is None:
            self._adapter = DB2Adapter(self.config, self.mp_context)
            inject_adapter(self._adapter, Plugin)
        return self._adapter

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_acquire_connection_validations(self, mock_connect):
        try:
            connection = self.adapter.acquire_connection("dummy")
        except DbtValidationError as e:
            self.fail("got DbtValidationError: {}".format(str(e)))
        except BaseException as e:
            self.fail("acquiring connection failed with unknown exception: {}".format(str(e)))
        self.assertEqual(connection.type, "db2")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_acquire_connection(self, mock_connect):
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        self.assertEqual(connection.state, "open")
        self.assertNotEqual(connection.handle, None)
        mock_connect.assert_called_once()

    def test_cancel_open_connections_empty(self):
        self.assertEqual(len(list(self.adapter.cancel_open_connections())), 0)

    def test_cancel_open_connections_master(self):
        key = self.adapter.connections.get_thread_identifier()
        self.adapter.connections.thread_connections[key] = mock_connection("master")
        self.assertEqual(len(list(self.adapter.cancel_open_connections())), 0)

    @pytest.mark.skip(
        """Skipping. Cancelling query is not supported."""
    )
    def test_cancel_open_connections_single(self):
        master = mock_connection("master")
        model = mock_connection("model")
        key = self.adapter.connections.get_thread_identifier()
        model.handle.get_backend_pid.return_value = 42
        self.adapter.connections.thread_connections.update(
            {
                key: master,
                1: model,
            }
        )
        with mock.patch.object(self.adapter.connections, "add_query") as add_query:
            query_result = mock.MagicMock()
            add_query.return_value = (None, query_result)
            self.assertEqual(len(list(self.adapter.cancel_open_connections())), 1)
            add_query.assert_called_once_with("select pg_terminate_backend(42)")

        master.handle.get_backend_pid.assert_not_called()

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_default_connect_timeout(self, mock_connect):
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support connection timeout yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_changed_connect_timeout(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(connect_timeout=30)
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_default_keepalive(self, mock_connect):
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support keepalives_idle yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_changed_keepalive(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(keepalives_idle=256)
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_default_application_name(self, mock_connect):
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support application rename yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_changed_application_name(self, mock_connect):
        print(f"creds: {self.config.credentials}")
        self.config.credentials = self.config.credentials.replace(application_name="myapp")
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support role in connections yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_role(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(role="somerole")
        connection = self.adapter.acquire_connection("dummy")

        # Mock the cursor
        mock_cursor = mock.MagicMock()
        connection.handle.cursor.return_value = mock_cursor

        # Access the cursor to trigger the mock
        cursor = connection.handle.cursor()

        cursor.execute.assert_called_once_with("set role somerole")

    @pytest.mark.skip(
        """Skipping. search-path is a postgres feature."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_search_path(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(search_path="test")
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_security_ssl(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(security="SSL")
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()
        
        # Verify SSL parameter is in connection string
        call_args = mock_connect.call_args[0][0]
        assert "Security=SSL" in call_args

    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_ssl_parameters(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(security="SSL")
        self.config.credentials = self.config.credentials.replace(ssl_server_certificate="/etc/db2/ca.crt")
        self.config.credentials = self.config.credentials.replace(ssl_client_keystore="/etc/db2/client.kdb")
        self.config.credentials = self.config.credentials.replace(ssl_client_keystash="/etc/db2/client.sth")
        self.config.credentials = self.config.credentials.replace(ssl_client_hostname_validation=True)
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()
        
        # Verify all SSL parameters are in connection string
        call_args = mock_connect.call_args[0][0]
        assert "Security=SSL" in call_args
        assert "SSLServerCertificate=/etc/db2/ca.crt" in call_args
        assert "SSLClientKeystoredb=/etc/db2/client.kdb" in call_args
        assert "SSLClientKeystash=/etc/db2/client.sth" in call_args
        assert "SSLClientHostnameValidation=true" in call_args

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support search_path yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_schema_with_space(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(search_path="test test")
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @pytest.mark.skip(
        """Skipping. since dbt-db2 doesn't support keepalives_idle yet."""
    )
    @mock.patch("dbt.adapters.db2.connections.ibm_db_dbi.connect")
    def test_set_zero_keepalive(self, mock_connect):
        self.config.credentials = self.config.credentials.replace(keepalives_idle=0)
        connection = self.adapter.acquire_connection("dummy")

        mock_connect.assert_not_called()
        connection.handle
        mock_connect.assert_called_once()

    @mock.patch.object(DB2Adapter, "execute_macro")
    @mock.patch.object(DB2Adapter, "_get_catalog_relations")
    def test_get_catalog_various_schemas(self, mock_get_relations, mock_execute):
        self.catalog_test(mock_get_relations, mock_execute, False)

    @mock.patch.object(DB2Adapter, "execute_macro")
    @mock.patch.object(DB2Adapter, "_get_catalog_relations")
    def test_get_filtered_catalog(self, mock_get_relations, mock_execute):
        self.catalog_test(mock_get_relations, mock_execute, True)

    def catalog_test(self, mock_get_relations, mock_execute, filtered=False):
        column_names = ["table_database", "table_schema", "table_name"]
        relations = [
            BaseRelation(path=Path(database="dbt", schema="foo", identifier="bar")),
            BaseRelation(path=Path(database="dbt", schema="FOO", identifier="baz")),
            BaseRelation(path=Path(database="dbt", schema=None, identifier="bar")),
            BaseRelation(path=Path(database="dbt", schema="quux", identifier="bar")),
            BaseRelation(path=Path(database="dbt", schema="skip", identifier="bar")),
        ]
        rows = list(map(lambda x: dataclasses.astuple(x.path), relations))
        mock_execute.return_value = agate.Table(rows=rows, column_names=column_names)

        mock_get_relations.return_value = relations

        relation_configs = []
        used_schemas = {("dbt", "foo"), ("dbt", "quux")}

        set_invocation_context({})
        if filtered:
            catalog, exceptions = self.adapter.get_filtered_catalog(
                relation_configs, used_schemas, set([relations[0], relations[3]])
            )
        else:
            catalog, exceptions = self.adapter.get_catalog(relation_configs, used_schemas)

        tupled_catalog = set(map(tuple, catalog))
        if filtered:
            self.assertEqual(tupled_catalog, {rows[0], rows[3]})
        else:
            self.assertEqual(tupled_catalog, {rows[0], rows[1], rows[3]})

        self.assertEqual(exceptions, [])
