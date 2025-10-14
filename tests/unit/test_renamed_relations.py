from dbt.adapters.db2.relation import DB2Relation
from dbt.adapters.contracts.relation import RelationType


def test_renameable_relation():
    relation = DB2Relation.create(
        database="testdbt",
        schema="my_schema",
        identifier="my_table",
        type=RelationType.Table,
    )
    assert relation.renameable_relations == frozenset()
    # DB2Relation doesn't contain renameable_relations and used base macro.
    # Hence, empty.
