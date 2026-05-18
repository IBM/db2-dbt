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


read_data = partial(read, "jaffle_shop", "data")
read_doc = partial(read, "jaffle_shop", "docs")
read_model = partial(read, "jaffle_shop", "models")
read_schema = partial(read, "jaffle_shop", "schemas")
read_staging = partial(read, "jaffle_shop", "staging")


class JaffleShop:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "customers.sql": read_model("customers"),
            "docs.md": read_doc("docs"),
            "orders.sql": read_model("orders"),
            "ignored_model1.sql": "select 1 as id from SYSIBM.SYSDUMMY1",
            "ignored_model2.sql": "select 1 as id from SYSIBM.SYSDUMMY1",
            "overview.md": read_doc("overview"),
            "schema.yml": read_schema("jaffle_shop"),
            "ignore_folder": {
                "model1.sql": "select 1 as id from SYSIBM.SYSDUMMY1",
                "model2.sql": "select 1 as id from SYSIBM.SYSDUMMY1",
            },
            "staging": {
                "schema.yml": read_schema("staging"),
                "stg_customers.sql": read_staging("stg_customers"),
                "stg_orders.sql": read_staging("stg_orders"),
                "stg_payments.sql": read_staging("stg_payments"),
            },
        }

    @pytest.fixture(scope="class")
    def seeds(self):
        return {
            "raw_customers.csv": read_data("raw_customers"),
            "raw_orders.csv": read_data("raw_orders"),
            "raw_payments.csv": read_data("raw_payments"),
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "jaffle_shop",
            "models": {
                "jaffle_shop": {
                    "materialized": "table",
                    "staging": {
                        "materialized": "view",
                    },
                }
            },
        }
