from dbt.adapters.db2.connections import Db2ConnectionManager # noqa
from dbt.adapters.db2.connections import Db2Credentials
from dbt.adapters.db2.impl import Db2Adapter

from dbt.adapters.base import AdapterPlugin
import dbt.include.db2


Plugin = AdapterPlugin(
    adapter=Db2Adapter,
    credentials=Db2Credentials,
    include_path=dbt.include.db2.PACKAGE_PATH)
