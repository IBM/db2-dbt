import decimal
from unittest import TestCase

import agate
from dbt_common.clients import agate_helper

from dbt.adapters.db2 import Db2Adapter


class TestDb2FilterCatalog(TestCase):
    def test__catalog_filter_table(self):
        used_schemas = [["a", "B"], ["a", "1234"]]
        # Include all columns that the catalog returns
        column_names = [
            "table_database", "table_schema", "table_name", "table_type",
            "table_comment", "column_name", "column_index", "column_type",
            "column_comment", "table_owner"
        ]
        rows = [
            ["a", "b", "foo", "TABLE", None, "col1", 1, "VARCHAR", None, "owner"],  # include
            ["a", "1234", "foo", "TABLE", None, "col1", 1, "VARCHAR", None, "owner"],  # include, w/ table schema as str
            ["c", "B", "foo", "TABLE", None, "col1", 1, "VARCHAR", None, "owner"],  # skip
            ["A", "B", "1234", "TABLE", None, "col1", 1, "VARCHAR", None, "owner"],  # include, w/ table name as str
        ]
        table = agate.Table(rows, column_names, agate_helper.DEFAULT_TYPE_TESTER)

        result = Db2Adapter._catalog_filter_table(table, used_schemas)
        assert len(result) == 3
        for row in result.rows:
            assert isinstance(row["table_schema"], str)
            assert isinstance(row["table_database"], str)
            assert isinstance(row["table_name"], str)
            # column_index should be a number (int or Decimal depending on agate's type inference)
            assert isinstance(row["column_index"], (int, decimal.Decimal))
