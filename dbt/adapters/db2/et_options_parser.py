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
import yaml
from typing import Dict


class ETOptions:
    def __init__(self, options: Dict):
        self.options = options


def et_options_constructor(loader, node):
    """
    Returns a dict of values written in et_options.yaml file
    in the client/fe project.
    """
    values = loader.construct_mapping(node)
    et_options_obj: ETOptions = ETOptions(values)
    return et_options_obj


def etoptions_representer(dumper, data: ETOptions):
    return dumper.represent_mapping('!ETOptions', {k: v for k, v in data.options.items()})


def parse_et_options_yaml(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def get_et_options_as_string(user_file_path: str):
    yaml.SafeLoader.add_constructor('!ETOptions', et_options_constructor)
    et_options_data = parse_et_options_yaml(user_file_path)
    if not et_options_data:
        return ""
    to_be_returned = ""
    for k, v in et_options_data[0].options.items():
        to_be_returned += f"{k} {v}\n"
    return to_be_returned


def create_et_options(project_path):
    yaml.add_representer(ETOptions, etoptions_representer)
    et_options = ETOptions(options={'SkipRows': '1', 'Delimiter': "','", 'DateDelim': "'-'", 'MaxErrors': '0'})
    with open(f"{project_path}/et_options.yml", "w") as file:
        yaml.dump([et_options], file, default_flow_style=False)
