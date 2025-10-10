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
    from dbt.adapters.factory import register_adapter, get_adapter_class_by_name
    
    print("Registered adapters before:")
    try:
        from dbt.adapters.factory import FACTORY
        print(f"Factory: {FACTORY}")
        print(f"Registered adapters: {FACTORY.adapters}")
    except Exception as e:
        print(f"Could not access factory: {e}")
    
    try:
        adapter_class = get_adapter_class_by_name('db2')
        print(f"✅ Successfully got adapter class by name: {adapter_class}")
    except Exception as e:
        print(f"❌ Failed to get adapter class by name: {e}")
        
    try:
        register_adapter('db2')
        print("✅ Successfully registered adapter")
        adapter_class = get_adapter_class_by_name('db2')
        print(f"✅ After registration, got adapter class: {adapter_class}")
    except Exception as e:
        print(f"❌ Failed to register adapter: {e}")
except Exception as e:
    print(f"❌ Error in dbt adapter factory: {e}")

# Made with Bob
