import os
from os import chdir
from os.path import normcase, normpath
from io import StringIO
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, Optional

from dbt.cli.main import dbtRunner
from dbt_common.events.functions import (
    capture_stdout_logs,
    reset_metadata_vars,
    stop_capture_stdout_logs,
)
from dbt_common.events.base_types import EventMsg

from dbt.adapters.db2.et_options_parser import create_et_options


@contextmanager
def up_one(return_path: Optional[Path] = None):
    current_path = Path.cwd()
    chdir("../")
    try:
        yield
    finally:
        chdir(return_path or current_path)


def normalize(path):
    """On windows, neither is enough on its own:

    >>> normcase('C:\\documents/ALL CAPS/subdir\\..')
    'c:\\documents\\all caps\\subdir\\..'
    >>> normpath('C:\\documents/ALL CAPS/subdir\\..')
    'C:\\documents\\ALL CAPS'
    >>> normpath(normcase('C:\\documents/ALL CAPS/subdir\\..'))
    'c:\\documents\\all caps'
    """
    return normcase(normpath(path))


def update_seed_file_names(seeds_path: str):
    if os.path.exists(seeds_path):
        for i in os.listdir(seeds_path):
            if i.endswith(".csv"):
                new_name = i.split('.csv')[0].upper() + '.csv'
                os.rename(seeds_path + '/' + i, seeds_path + '/' + new_name)
    else:
        pass


def run_dbt(
    args: Optional[List[str]] = None,
    expect_pass: bool = True,
    callbacks: Optional[List[Callable[[EventMsg], None]]] = None
):
    print("run_dbt invoked for functional tests...")
    reset_metadata_vars()
    if args is None:
        args = ["run"]

    from dbt.flags import get_flags
    flags = get_flags()

    project_dir = getattr(flags, "PROJECT_DIR", None)
    profiles_dir = getattr(flags, "PROFILES_DIR", None)

    # Create the et_options.yaml as required by nz-dbt.
    # run_dbt is overriden for this.
    create_et_options(project_dir)
    update_seed_file_names(project_dir + '/seeds')

    if project_dir and "--project-dir" not in args:
        args.extend(["--project-dir", project_dir])
    if profiles_dir and "--profiles-dir" not in args:
        args.extend(["--profiles-dir", profiles_dir])
    dbt = dbtRunner(callbacks=callbacks)
    res = dbt.invoke(args)

    # the exception is immediately raised to be caught in tests
    # using a pattern like `with pytest.raises(SomeException):`
    if res.exception is not None:
        raise res.exception

    if expect_pass is not None:
        assert res.success == expect_pass, "dbt exit state did not match expected"
    return res.result


def run_dbt_and_capture(args: Optional[List[str]] = None, expect_pass: bool = True):
    # _set_flags()
    try:
        stringbuf = StringIO()
        capture_stdout_logs(stringbuf)
        res = run_dbt(args, expect_pass=expect_pass)
        stdout = stringbuf.getvalue()

    finally:
        stop_capture_stdout_logs()

    return res, stdout


def _set_flags():
    # in order to call dbt's internal profile rendering, we need to set the
    # flags global. This is a bit of a hack, but it's the best way to do it.
    from dbt.flags import set_from_args
    from argparse import Namespace

    set_from_args(Namespace(), None)
