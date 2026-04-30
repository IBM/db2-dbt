import os

import pytz
import agate
from dateutil import parser
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Any, Union

from dbt import deprecations
from dbt.adapters.base.connections import AdapterResponse
from dbt.adapters.base.meta import available
from dbt.adapters.base.impl import ConstraintSupport, _utc
from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.exceptions.database import UnexpectedDbReferenceError
from dbt.adapters.db2 import Db2ConnectionManager
from dbt.adapters.db2.column import Db2Column
from dbt.adapters.db2.et_options_parser import get_et_options_as_string
from dbt.adapters.db2.relation import Db2Relation
from dbt.adapters.protocol import AdapterConfig
from dbt.adapters.sql.impl import SQLAdapter, LIST_RELATIONS_MACRO_NAME
from dbt.contracts.graph.manifest import Manifest
from dbt_common.exceptions import CompilationError, DbtDatabaseError, MacroResultError
from dbt_common.utils import filter_null_values, AttrDict
from dbt.contracts.graph.nodes import ConstraintType
from dbt.adapters.contracts.macros import MacroResolverProtocol

@dataclass
class Db2Config(AdapterConfig):
    dist: Optional[str] = None


FRESHNESS_MACRO_NAME = "collect_freshness"  # Macro used to analyze the freshness of the data imports in tables
class Db2Adapter(SQLAdapter):
    INT_MIN32 = -2147483648
    INT_MAX32 = 2147483648

    AdapterSpecificConfigs = Db2Config
    ConnectionManager = Db2ConnectionManager
    Relation = Db2Relation
    Column = Db2Column

    CONSTRAINT_SUPPORT = {
        ConstraintType.check: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.not_null: ConstraintSupport.ENFORCED,
        ConstraintType.unique: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.primary_key: ConstraintSupport.NOT_ENFORCED,
        ConstraintType.foreign_key: ConstraintSupport.NOT_ENFORCED,
    }

    @classmethod
    def date_function(cls):
        return "now()"

    # Overriding methods because Db2 uppercases by default
    # and we want to avoid quoting of columns
    # Source: https://github.com/dbt-labs/dbt-snowflake/blob/fda11c2e822519996101d2c456a51570f4ed1c04/dbt/adapters/snowflake/impl.py#L45-L54
    @classmethod
    def _catalog_filter_table(
        cls, table: agate.Table, manifest: Manifest
    ) -> agate.Table:
        lowered = table.rename(column_names=[c.lower() for c in table.column_names])
        return super()._catalog_filter_table(lowered, manifest)

    # Source: https://github.com/dbt-labs/dbt-snowflake/blob/fda11c2e822519996101d2c456a51570f4ed1c04/dbt/adapters/snowflake/impl.py#L56-L69
    def _make_match_kwargs(self, database: str, schema: str, identifier: str):
        quoting = self.config.quoting
        if identifier is not None and quoting["identifier"] is False:
            identifier = identifier.upper()

        if schema is not None and quoting["schema"] is False:
            schema = schema.upper()

        if database is not None and quoting["database"] is False:
            database = database.upper()

        return filter_null_values(
            {"identifier": identifier, "schema": schema, "database": database}
        )

    # Source: https://github.com/dbt-labs/dbt-snowflake/blob/fda11c2e822519996101d2c456a51570f4ed1c04/dbt/adapters/snowflake/impl.py#L128-L166
    def list_relations_without_caching(
        self, schema_relation: BaseRelation
    ) -> List[BaseRelation]:
        kwargs = {"schema_relation": schema_relation}
        try:
            results = self.execute_macro(LIST_RELATIONS_MACRO_NAME, kwargs=kwargs)
        except DbtDatabaseError as exc:
            # if the schema doesn't exist, we just want to return.
            # Alternatively, we could query the list of schemas before we start
            # and skip listing the missing ones, which sounds expensive.
            if "Object does not exist" in str(exc):
                return []
            raise

        relations: List[BaseRelation] = []
        quote_policy = {"database": True, "schema": True, "identifier": True}

        # Handle case where results is None or doesn't have select method
        if results is None or not hasattr(results, 'select'):
            return relations

        # Get actual column names from results (case-insensitive match)
        columns = []
        for expected_col in ["DATABASE", "SCHEMA", "NAME", "TYPE"]:
            # Find matching column (case-insensitive)
            matching_col = next((col for col in results.column_names
                                if col.upper() == expected_col), None)
            if matching_col:
                columns.append(matching_col)
            else:
                # Fallback to expected column name
                columns.append(expected_col)

        for _database, _schema, _identifier, _type in results.select(columns):
            try:
                _type = self.Relation.get_relation_type(_type.lower())
            except ValueError:
                _type = self.Relation.External
            relations.append(
                self.Relation.create(
                    database=_database,
                    schema=_schema,
                    identifier=_identifier,
                    quote_policy=quote_policy,
                    type=_type,
                )
            )

        return relations

    # Override with Redshift implementation because Db2 does not support `text`
    # Source: https://github.com/dbt-labs/dbt-redshift/blob/64f6f7ba4f8fbe11d9c547f7c07faeb9b14deb83/dbt/adapters/redshift/impl.py#L54-L61
    @classmethod
    def convert_text_type(cls, agate_table, col_idx):
        column = agate_table.columns[col_idx]
        # `lens` must be a list, so this can't be a generator expression,
        # because max() raises an exception if its argument has no members.
        # source: https://github.com/fishtown-analytics/dbt/pull/2255/files#diff-39545f1198b754f67de59957630a527b6d1df026aff22cc90de923f5653d5ad8
        lens = [len(d.encode("utf-8")) for d in column.values_without_nulls()]
        max_len = max(lens) if lens else 64
        return f"varchar({max_len})"

    # Override to remove `without time zone` because Db2 does not support this
    @classmethod
    def convert_datetime_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return "timestamp"

    # Override to check if view exists before dropping because Db2 does not support
    # `drop view if exists`
    def drop_relation(self, relation):
        # If relation type is None, the relation doesn't exist in the database
        if relation.type is None:
            return

        if relation.type == "view":
            identifier = relation.identifier
            relations = self.list_relations_without_caching(relation)
            no_relation_exists = (
                next(
                    rel
                    for rel in relations
                    if rel.type == "view" and rel.identifier == identifier
                )
                is None
            )
            if no_relation_exists:
                return

        super().drop_relation(relation)

    # Override to skip the cursor.commit() which causes a ODBC HY010
    # "function sequence error"
    # Source: https://github.com/dbt-labs/dbt-core/blob/c270a77552ae9fc66fdfab359d65a8db1307c3f3/core/dbt/adapters/sql/impl.py#L223-L243
    def run_sql_for_tests(self, sql, fetch, conn):
        cursor = conn.handle.cursor()
        try:
            cursor.execute(sql)
            if hasattr(conn.handle, "commit"):
                # Skip cursor.commit()
                pass
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return
        except BaseException as e:
            if conn.handle and not getattr(conn.handle, "closed", True):
                conn.handle.rollback()
            print(sql)
            print(e)
            raise
        finally:
            conn.transaction_open = False

    @available
    def get_seed_file_path(self, model) -> str:
        return os.path.join(model["root_path"], model["original_file_path"])

    @available
    def verify_database(self, database):
        if database.startswith('"'):
            database = database.strip('"')
        expected = self.config.credentials.database
        if database.lower() != expected.lower():
            raise UnexpectedDbReferenceError(self.type(), database, expected)
        # return an empty string on success so macros can call this
        return ""

    @available
    def rename_relation(self, from_relation, to_relation):
        self.cache_renamed(from_relation, to_relation)

        kwargs = {"from_relation": from_relation, "to_relation": to_relation}
        self.execute_macro('rename_relation', kwargs=kwargs)

    @available
    def get_et_options(self, model) -> str:
        return get_et_options_as_string(os.path.join(model["root_path"], "et_options.yml"))

    # Override to change the default value of quote_columns to False
    # Source: https://github.com/dbt-labs/dbt-core/blob/7f8d9a7af976f640e376900773a0d793acf3a3ce/core/dbt/adapters/base/impl.py#L812-L828
    @available
    def quote_seed_column(self, column: str, quote_config: Optional[bool]) -> str:
        # Change default value to False
        quote_columns: bool = False
        if isinstance(quote_config, bool):
            quote_columns = quote_config
        elif quote_config is None:
            pass
        else:
            raise CompilationError(
                f'The seed configuration value of "quote_columns" has an '
                f"invalid type {type(quote_config)}"
            )

        if quote_columns:
            return self.quote(column)
        else:
            return column

    @available
    def quote_seed_value(self, value, quote_config: Optional[bool] = True) -> str:
        """Quote a seed value for insertion into a SQL statement."""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            value = str(value).replace("'", "''")
            return f"'{value}'"

    # Override to search for uppercase keys in grants_table because Db2 always returns
    # uppercase keys and agate.Table.__get_item__ is case-sensitive
    def standardize_grants_dict(self, grants_table: agate.Table) -> dict:
        grants_dict: Dict[str, List[str]] = {}
        for row in grants_table:
            grantee = row["GRANTEE"]
            privilege = row["PRIVILEGE_TYPE"]
            if privilege in grants_dict.keys():
                grants_dict[privilege].append(grantee)
            else:
                grants_dict.update({privilege: [grantee]})
        return grants_dict

    def valid_incremental_strategies(self):
        """The set of standard builtin strategies which this adapter supports out-of-the-box.
        Not used to validate custom strategies defined by end users.
        """
        return ["merge", "delete+insert"]

    # For checking the freshness , converting the str type object returned from Db2 relation to datetime
    def calculate_freshness(
        self,
        source: BaseRelation,
        loaded_at_field: str,
        filter: Optional[str],
        macro_resolver: Optional[MacroResolverProtocol] = None,
    ) -> Tuple[Optional[AdapterResponse], Dict[str, Any]]:
        """Calculate the freshness of sources in dbt, and return it"""
        kwargs: Dict[str, Any] = {
            "source": source,
            "loaded_at_field": loaded_at_field,
            "filter": filter,
        }
        # run the macro
        # in older versions of dbt-core, the 'collect_freshness' macro returned the table of results directly
        # starting in v1.5, by default, we return both the table and the adapter response (metadata about the query)
        result: Union[
            AttrDict,  # current: contains AdapterResponse + agate.Table
            agate.Table,  # previous: just table
        ]
        result = self.execute_macro(FRESHNESS_MACRO_NAME, kwargs=kwargs, macro_resolver=macro_resolver)
        if isinstance(result, agate.Table):
            deprecations.warn("collect-freshness-return-signature")
            adapter_response = None
            table = result
        else:
            adapter_response, table = result.response, result.table  # type: ignore[attr-defined]
        # now we have a 1-row table of the maximum `loaded_at_field` value and
        # the current time according to the db.
        if len(table) != 1 or len(table[0]) != 2:
            raise MacroResultError(FRESHNESS_MACRO_NAME, table)
        if table[0][0] is None:
            # no records in the table, so really the max_loaded_at was
            # infinitely long ago. Just call it 0:00 January 1 year UTC
            max_loaded_at = datetime(1, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        else:
            max_loaded_at = _utc(parser.parse(table[0][0]), source, loaded_at_field)
        snapshotted_at = _utc(parser.parse(table[0][1]), source, loaded_at_field)
        age = (snapshotted_at - max_loaded_at).total_seconds()
        freshness = {
            "max_loaded_at": max_loaded_at,
            "snapshotted_at": snapshotted_at,
            "age": age,
        }
        return adapter_response, freshness

    @classmethod
    def convert_number_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        # TODO CT-211
        decimals = agate_table.aggregate(agate.MaxPrecision(col_idx))  # type: ignore[attr-defined]
        if decimals:
            return "float8"
        else:
            clm = max([row[col_idx] for row in agate_table.rows])
            if clm >= cls.INT_MIN32 and clm <= cls.INT_MAX32:
                return "integer"
            else:
                return "bigint"
