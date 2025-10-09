from dbt.adapters.db2.connections import DB2ConnectionManager # noqa
from dbt.adapters.db2.connections import DB2Credentials
from dbt.adapters.db2.impl import DB2Adapter

from dbt.adapters.base import AdapterPlugin
import dbt.include.db2


Plugin = AdapterPlugin(
    adapter=DB2Adapter,
    credentials=DB2Credentials,
    include_path=dbt.include.db2.PACKAGE_PATH)
