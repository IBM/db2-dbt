"""Version information for ibm-dbt-db2 adapter."""

from importlib.metadata import PackageNotFoundError, version as get_version

try:
    version = get_version("ibm-dbt-db2")
except PackageNotFoundError:
    version = "0.0.0"

__version__ = version
