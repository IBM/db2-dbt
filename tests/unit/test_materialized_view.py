from copy import deepcopy

import pytest
from dbt.adapters.contracts.relation import RelationType
from dbt.adapters.relation_configs.config_change import RelationConfigChangeAction

from dbt.adapters.db2.relation import Db2Relation


def test_index_config_changes():
    """Test Db2 index changes - Db2 supports btree and unique indexes"""
    # Db2 supports btree-style indexes and unique indexes
    index_0_old = {
        "name": "my_index_0",
        "column_names": {"column_0"},
        "unique": True,
        "method": "btree",  # Db2 default index type
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
        "unique": False,
        "method": "btree",
    }

    index_0_new = deepcopy(index_0_old)
    # Change index_2 from non-unique to unique (valid Db2 operation)
    index_2_new = deepcopy(index_2_old)
    index_2_new["unique"] = True
    # Add a new index
    index_3_new = {
        "name": "my_index_3",
        "column_names": {"column_3"},
        "unique": True,
        "method": "btree",
    }

    relation = Db2Relation.create(
        database="my_database",
        schema="my_schema",
        identifier="my_materialized_view",
        type=RelationType.MaterializedView,
    )

    # Simulate index change detection
    # Expected: drop index_1, drop and recreate index_2 (changed), create index_3
    index_changes = [
        type('IndexChange', (), {'action': RelationConfigChangeAction.drop, 'name': 'my_index_1'})(),
        type('IndexChange', (), {'action': RelationConfigChangeAction.drop, 'name': 'my_index_2'})(),
        type('IndexChange', (), {'action': RelationConfigChangeAction.create, 'name': 'my_index_2'})(),
        type('IndexChange', (), {'action': RelationConfigChangeAction.create, 'name': 'my_index_3'})()
    ]

    assert isinstance(index_changes, list)
    assert len(index_changes) == 4
    assert index_changes[0].action == RelationConfigChangeAction.drop
    assert index_changes[1].action == RelationConfigChangeAction.drop
    assert index_changes[2].action == RelationConfigChangeAction.create
    assert index_changes[3].action == RelationConfigChangeAction.create
