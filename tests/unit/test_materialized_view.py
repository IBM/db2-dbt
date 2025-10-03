from copy import deepcopy

import pytest
from dbt.adapters.contracts.relation import RelationType
from dbt.adapters.relation_configs.config_change import RelationConfigChangeAction

from dbt.adapters.db2.relation import NetezzaRelation


@pytest.mark.skip(
    """Skipping. NPS doesn't support multiple types of Indexes as Postgres."""
)
def test_index_config_changes():
    index_0_old = {
        "name": "my_index_0",
        "column_names": {"column_0"},
        "unique": True,
        "method": "btree",
    }
    index_1_old = {
        "name": "my_index_1",
        "column_names": {"column_1"},
        "unique": True,
        "method": "btree",
    }
    index_2_old = {
        "name": "my_index_2",
        "column_names": {"column_2"},
        "unique": True,
        "method": "btree",
    }
    existing_indexes = frozenset(
        PostgresIndexConfig.from_dict(index) for index in [index_0_old, index_1_old, index_2_old]
    )

    index_0_new = deepcopy(index_0_old)
    index_2_new = deepcopy(index_2_old)
    index_2_new.update(method="hash")
    index_3_new = {
        "name": "my_index_3",
        "column_names": {"column_3"},
        "unique": True,
        "method": "hash",
    }
    new_indexes = frozenset(
        PostgresIndexConfig.from_dict(index) for index in [index_0_new, index_2_new, index_3_new]
    )

    relation = NetezzaRelation.create(
        database="my_database",
        schema="my_schema",
        identifier="my_materialized_view",
        type=RelationType.MaterializedView,
    )

    index_changes = relation._get_index_config_changes(existing_indexes, new_indexes)

    assert isinstance(index_changes, list)
    assert len(index_changes) == len(["drop 1", "drop 2", "create 2", "create 3"])
    assert index_changes[0].action == RelationConfigChangeAction.drop
    assert index_changes[1].action == RelationConfigChangeAction.drop
    assert index_changes[2].action == RelationConfigChangeAction.create
    assert index_changes[3].action == RelationConfigChangeAction.create
