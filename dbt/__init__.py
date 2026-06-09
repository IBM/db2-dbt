# -------------------------------------------------------------------------------------------------#
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
# -------------------------------------------------------------------------------------------------#

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import click

from pathlib import Path
from dbt.cli import params as p
from dbt.cli import requires
from dbt.cli.main import cli, global_flags
from dbt.task.init import InitTask
from dbt.events.types import SettingUpProfile, InvalidProfileTemplateYAML
from dbt_common.events.functions import fire_event
from dbt.adapters.db2.et_options_parser import create_et_options


class Db2InitTask(InitTask):
    def setup_profile(self, profile_name: str) -> None:
        """Set up a new profile for a project"""
        fire_event(SettingUpProfile())
        if not self.check_if_can_write_profile(profile_name=profile_name):
            return
        # If a profile_template.yml exists in the project root, that effectively
        # overrides the profile_template.yml for the given target.
        profile_template_path = Path("profile_template.yml")
        if profile_template_path.exists():
            try:
                # This relies on a valid profile_template.yml from the user,
                # so use a try: except to fall back to the default on failure
                self.create_profile_using_project_profile_template(profile_name)
                return
            except Exception:
                fire_event(InvalidProfileTemplateYAML())
        adapter = self.ask_for_adapter_choice()
        if adapter == "db2":
            create_et_options(".")
        self.create_profile_from_target(adapter, profile_name=profile_name)


# dbt init
@cli.command("init")
@click.pass_context
@global_flags
# for backwards compatibility, accept 'project_name' as an optional positional argument
@click.argument("project_name", required=False)
@p.profiles_dir_exists_false
@p.project_dir
@p.skip_profile_setup
@p.vars
@requires.postflight
@requires.preflight
def db2_init(ctx, **kwargs):
    """Initialize a new dbt project for Db2 driver."""

    with Db2InitTask(ctx.obj["flags"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success


init = db2_init
