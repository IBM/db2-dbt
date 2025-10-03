from dbt.adapters.db2.relation import NetezzaRelation
from dbt.adapters.contracts.relation import RelationType


def test_renameable_relation():
    relation = NetezzaRelation.create(
        database="testdbt",
        schema="my_schema",
        identifier="my_table",
        type=RelationType.Table,
    )
    assert relation.renameable_relations == frozenset()
    # NetezzaRelation doesn't contain renameable_relations and used base macro.
    # Hence, empty.
