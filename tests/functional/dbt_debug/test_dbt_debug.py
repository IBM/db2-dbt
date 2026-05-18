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

import pytest

from tests.functional.utils import run_dbt_and_capture

MODELS__MODEL_SQL = """
seled 1 as id
"""


class BaseDebug:
    @pytest.fixture(scope="class")
    def models(self):
        return {"model.sql": MODELS__MODEL_SQL}

    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def assertGotValue(self, linepat, result):
        found = False
        output = self.capsys.readouterr().out
        for line in output.split("\n"):
            if linepat.match(line):
                found = True
                assert result in line
        if not found:
            with pytest.raises(Exception) as exc:
                msg = f"linepat {linepat} not found in stdout: {output}"
                assert msg in str(exc.value)

    def check_project(self, splitout, msg="ERROR invalid"):
        for line in splitout:
            if line.strip().startswith("dbt_project.yml file"):
                assert msg in line
            elif line.strip().startswith("profiles.yml file"):
                assert "ERROR invalid" not in line


class BaseDebugProfileVariable(BaseDebug):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"config-version": 2, "profile": '{{ "te" ~ "st" }}'}


class TestDebugPostgres(BaseDebug):
    def test_ok(self, project):
        result, log = run_dbt_and_capture(["debug"])
        assert "ERROR" not in log


class TestDebugProfileVariablePostgres(BaseDebugProfileVariable):
    pass
