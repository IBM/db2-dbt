import sys
import os
import importlib
import pkg_resources

print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

print("\nChecking if modules can be imported directly:")
try:
    import dbt.adapters.db2
    print("✅ dbt.adapters.db2 can be imported")
except ImportError as e:
    print(f"❌ dbt.adapters.db2 cannot be imported: {e}")

try:
    import dbt.include.db2
    print("✅ dbt.include.db2 can be imported")
except ImportError as e:
    print(f"❌ dbt.include.db2 cannot be imported: {e}")

print("\nListing entry points:")
for entry_point in pkg_resources.iter_entry_points(group='dbt.adapters'):
    print(f"Entry point: {entry_point}")
    try:
        adapter_class = entry_point.load()
        print(f"✅ Successfully loaded {entry_point.name} adapter: {adapter_class}")
    except Exception as e:
        print(f"❌ Failed to load {entry_point.name} adapter: {e}")

print("\nTrying to load adapter through dbt's mechanism:")
try:
    from dbt.adapters.factory import load_plugin
    
    try:
        credentials = load_plugin('db2')
        print(f"✅ Successfully loaded db2 plugin: {credentials}")
    except Exception as e:
        print(f"❌ Failed to load db2 plugin: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f"❌ Error importing dbt.adapters.factory: {e}")
    print(f"Exception type: {type(e)}")
    import traceback
    traceback.print_exc()

# Made with Bob
