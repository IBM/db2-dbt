#-------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
#-------------------------------------------------------------------------------------------------#

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
