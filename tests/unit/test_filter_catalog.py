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
