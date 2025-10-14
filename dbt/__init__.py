__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import click

from pathlib import Path
from dbt.cli import params as p
from dbt.cli import requires
from dbt.cli.main import cli, global_flags
from dbt.task.init import InitTask
from dbt.events.types import SettingUpProfile, InvalidProfileTemplateYAML
from dbt_common.events.functions import fire_event
from dbt.adapters.db2.et_options_parser import create_et_options

class DB2InitTask(InitTask):
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
        if adapter == 'db2':
            create_et_options('.')
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
    """Initialize a new dbt project for DB2 driver."""

    with DB2InitTask(ctx.obj["flags"]) as task:
        results = task.run()
        success = task.interpret_results(results)
    return results, success

init = db2_init
