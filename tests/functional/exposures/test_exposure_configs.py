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

from dbt.contracts.graph.model_config import ExposureConfig
from dbt.tests.util import get_manifest, run_dbt, update_config_file
from dbt_common.dataclass_schema import ValidationError
import pytest

from tests.functional.exposures import fixtures


class ExposureConfigTests:
    @pytest.fixture(scope="class", autouse=True)
    def setUp(self):
        pytest.expected_config = ExposureConfig(
            enabled=True,
        )


# Test enabled config for exposure in dbt_project.yml
class TestExposureEnabledConfigProjectLevel(ExposureConfigTests):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": fixtures.models_sql,
            "metricflow_time_spine.sql": fixtures.metricflow_time_spine_sql,
            "second_model.sql": fixtures.second_model_sql,
            "exposure.yml": fixtures.simple_exposure_yml,
            "schema.yml": fixtures.source_schema_yml,
            "semantic_models.yml": fixtures.semantic_models_schema_yml,
            "metrics.yml": fixtures.metrics_schema_yml,
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "exposures": {
                "simple_exposure": {
                    "enabled": True,
                },
            }
        }

    def test_enabled_exposure_config_dbt_project(self, project):
        run_dbt(["parse"])
        manifest = get_manifest(project.project_root)
        assert "exposure.test.simple_exposure" in manifest.exposures

        new_enabled_config = {
            "exposures": {
                "test": {
                    "simple_exposure": {
                        "enabled": False,
                    },
                }
            }
        }
        update_config_file(new_enabled_config, project.project_root, "dbt_project.yml")
        run_dbt(["parse"])
        manifest = get_manifest(project.project_root)
        assert "exposure.test.simple_exposure" not in manifest.exposures
        assert "exposure.test.notebook_exposure" in manifest.exposures


# Test disabled config at exposure level in yml file
class TestConfigYamlLevel(ExposureConfigTests):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": fixtures.models_sql,
            "second_model.sql": fixtures.second_model_sql,
            "schema.yml": fixtures.disabled_models_exposure_yml,
        }

    def test_exposure_config_yaml_level(self, project):
        run_dbt(["parse"])
        manifest = get_manifest(project.project_root)
        assert "exposure.test.simple_exposure" not in manifest.exposures
        assert "exposure.test.notebook_exposure" in manifest.exposures


# Test inheritence - set configs at project and exposure level - expect exposure level to win
class TestExposureConfigsInheritence(ExposureConfigTests):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": fixtures.models_sql,
            "second_model.sql": fixtures.second_model_sql,
            "schema.yml": fixtures.enabled_yaml_level_exposure_yml,
        }

    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"exposures": {"enabled": False}}

    def test_exposure_all_configs(self, project):
        run_dbt(["parse"])
        manifest = get_manifest(project.project_root)
        # This should be overridden
        assert "exposure.test.simple_exposure" in manifest.exposures
        # This should stay disabled
        assert "exposure.test.notebook_exposure" not in manifest.exposures

        config_test_table = manifest.exposures.get("exposure.test.simple_exposure").config

        assert isinstance(config_test_table, ExposureConfig)
        assert config_test_table == pytest.expected_config


# Test invalid config triggers error
class TestInvalidConfig(ExposureConfigTests):
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": fixtures.models_sql,
            "second_model.sql": fixtures.second_model_sql,
            "schema.yml": fixtures.invalid_config_exposure_yml,
        }

    def test_exposure_config_yaml_level(self, project):
        with pytest.raises(ValidationError) as excinfo:
            run_dbt(["parse"])
        expected_msg = "'True and False' is not of type 'boolean'"
        assert expected_msg in str(excinfo.value)
