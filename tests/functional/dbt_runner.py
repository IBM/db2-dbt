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

import os
from typing import Callable, List, Optional

from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest
from dbt.tests.util import get_run_results
from dbt_common.events.base_types import EventMsg


def assert_run_results_have_compiled_node_attributes(
    args: List[str], result: dbtRunnerResult
) -> None:
    commands_with_run_results = ["build", "compile", "docs", "run", "test"]
    if not [a for a in args if a in commands_with_run_results] or not result.success:
        return

    run_results = get_run_results(os.getcwd())
    for r in run_results["results"]:
        if r["unique_id"].startswith("model") and r["status"] == "success":
            assert "compiled_code" in r
            assert "compiled" in r


_STANDARD_ASSERTIONS = [assert_run_results_have_compiled_node_attributes]


class dbtTestRunner(dbtRunner):
    exit_assertions: List[Callable[[List[str], dbtRunnerResult], None]]

    def __init__(
        self,
        manifest: Optional[Manifest] = None,
        callbacks: Optional[List[Callable[[EventMsg], None]]] = None,
        exit_assertions: Optional[List[Callable[[List[str], dbtRunnerResult], None]]] = None,
    ):
        self.exit_assertions = exit_assertions if exit_assertions else _STANDARD_ASSERTIONS  # type: ignore
        super().__init__(manifest, callbacks)

    def invoke(self, args: List[str], **kwargs) -> dbtRunnerResult:
        result = super().invoke(args, **kwargs)

        for assertion in self.exit_assertions:
            assertion(args, result)

        return result
