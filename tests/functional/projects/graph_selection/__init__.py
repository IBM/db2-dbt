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

from functools import partial

import pytest

from tests.functional.projects.utils import read


read_data = partial(read, "graph_selection", "data")
read_model = partial(read, "graph_selection", "models")
read_schema = partial(read, "graph_selection", "schemas")


class GraphSelection:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "schema.yml": read_schema("schema"),
            "patch_path_selection_schema.yml": read_schema("patch_path_selection"),
            "base_users.sql": read_model("base_users"),
            "users.sql": read_model("users"),
            "versioned_v3.sql": read_model("base_users"),
            "users_rollup.sql": read_model("users_rollup"),
            "users_rollup_dependency.sql": read_model("users_rollup_dependency"),
            "emails.sql": read_model("emails"),
            "emails_alt.sql": read_model("emails_alt"),
            "alternative.users.sql": read_model("alternative_users"),
            "never_selected.sql": read_model("never_selected"),
            "test": {
                "subdir.sql": read_model("subdir"),
                "versioned_v2.sql": read_model("subdir"),
                "subdir": {
                    "nested_users.sql": read_model("nested_users"),
                    "versioned_v1.sql": read_model("nested_users"),
                },
            },
        }

    @pytest.fixture(scope="class")
    def seeds(self, test_data_dir):
        return {
            "properties.yml": read_schema("properties"),
            "seed.csv": read_data("seed"),
            "summary_expected.csv": read_data("summary_expected"),
        }
