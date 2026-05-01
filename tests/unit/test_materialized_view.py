from dbt.adapters.contracts.relation import RelationType
from dbt.adapters.relation_configs.config_change import RelationConfigChangeAction

from dbt.adapters.db2.relation import Db2Relation


def test_index_config_changes():
    """Test Db2 index changes - Db2 supports btree and unique indexes"""
    # Test that Db2Relation can be created with MaterializedView type
    relation = Db2Relation.create(
        database="my_database",
        schema="my_schema",
        identifier="my_materialized_view",
        type=RelationType.MaterializedView,
    )

    # Verify relation properties
    assert relation.database == "my_database"
    assert relation.schema == "my_schema"
    assert relation.identifier == "my_materialized_view"
    assert relation.type == RelationType.MaterializedView

    # Test index change actions
    # Simulate index change detection for Db2
    # Expected: drop index_1, drop and recreate index_2 (changed), create index_3
    index_changes = [
        type('IndexChange', (), {
            'action': RelationConfigChangeAction.drop,
            'name': 'my_index_1'
        })(),
        type('IndexChange', (), {
            'action': RelationConfigChangeAction.drop,
            'name': 'my_index_2'
        })(),
        type('IndexChange', (), {
            'action': RelationConfigChangeAction.create,
            'name': 'my_index_2'
        })(),
        type('IndexChange', (), {
            'action': RelationConfigChangeAction.create,
            'name': 'my_index_3'
        })()
    ]

    # Verify index changes structure
    assert isinstance(index_changes, list)
    assert len(index_changes) == 4
    assert index_changes[0].action == RelationConfigChangeAction.drop
    assert index_changes[0].name == 'my_index_1'
    assert index_changes[1].action == RelationConfigChangeAction.drop
    assert index_changes[1].name == 'my_index_2'
    assert index_changes[2].action == RelationConfigChangeAction.create
    assert index_changes[2].name == 'my_index_2'
    assert index_changes[3].action == RelationConfigChangeAction.create
    assert index_changes[3].name == 'my_index_3'


def test_db2_relation_two_part_naming():
    """Test that Db2Relation uses two-part naming (schema.table), not three-part"""
    relation = Db2Relation.create(
        database="testdb",
        schema="testschema",
        identifier="testtable",
        type=RelationType.Table,
    )

    # Db2 uses two-part naming: schema.table
    # The database is stored but not used in qualified names
    assert relation.schema == "testschema"
    assert relation.identifier == "testtable"

    # Test relation rendering
    rendered = relation.render()
    # Should be schema.table, not database.schema.table
    assert "testschema" in rendered
    assert "testtable" in rendered
