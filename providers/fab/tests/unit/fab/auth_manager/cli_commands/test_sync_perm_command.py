#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from importlib import reload
from unittest import mock

import pytest

from airflow.cli import cli_parser

from tests_common.test_utils.compat import ignore_provider_compatibility_error
from tests_common.test_utils.config import conf_vars

with ignore_provider_compatibility_error("2.9.0+", __file__):
    from airflow.providers.fab.auth_manager.cli_commands import sync_perm_command

pytestmark = pytest.mark.db_test


class TestCliSyncPerm:
    @classmethod
    def setup_class(cls):
        with conf_vars(
            {
                (
                    "core",
                    "auth_manager",
                ): "airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager",
            }
        ):
            # Reload the module to use FAB auth manager
            reload(cli_parser)
            # Clearing the cache before calling it
            cli_parser.get_parser.cache_clear()
            cls.parser = cli_parser.get_parser()

    @mock.patch("airflow.providers.fab.auth_manager.cli_commands.utils.get_application_builder")
    def test_cli_sync_perm(self, mock_get_application_builder):
        mock_appbuilder = mock.MagicMock()
        mock_get_application_builder.return_value.__enter__.return_value = mock_appbuilder

        args = self.parser.parse_args(["sync-perm"])
        sync_perm_command.sync_perm(args)

        mock_appbuilder.add_permissions.assert_called_once_with(update_perms=True)
        mock_appbuilder.sm.sync_roles.assert_called_once_with()
        mock_appbuilder.sm.create_dag_specific_permissions.assert_not_called()

    @mock.patch("airflow.providers.fab.auth_manager.cli_commands.utils.get_application_builder")
    def test_cli_sync_perm_include_dags(self, mock_get_application_builder):
        mock_appbuilder = mock.MagicMock()
        mock_get_application_builder.return_value.__enter__.return_value = mock_appbuilder

        args = self.parser.parse_args(["sync-perm", "--include-dags"])
        sync_perm_command.sync_perm(args)

        mock_appbuilder.add_permissions.assert_called_once_with(update_perms=True)
        mock_appbuilder.sm.sync_roles.assert_called_once_with()
        mock_appbuilder.sm.create_dag_specific_permissions.assert_called_once_with()
