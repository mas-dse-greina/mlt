#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#

import getpass
import json
import os
import sys
import traceback
from shutil import copytree, ignore_patterns
from subprocess import check_output

from mlt.commands import Command
from mlt.utils import (config_helpers, constants, git_helpers,
                       kubernetes_helpers, process_helpers)


class InitCommand(Command):
    def __init__(self, args):
        super(InitCommand, self).__init__(args)
        self.app_name = self.args["<name>"]

    def action(self):
        """Creates a new git repository based on an mlt template in the
           current working directory.
        """
        template_name = self.args["--template"]
        template_repo = self.args["--template-repo"]
        skip_crd_check = self.args["--skip-crd-check"]
        with git_helpers.clone_repo(template_repo) as temp_clone:
            templates_directory = os.path.join(
                temp_clone, constants.TEMPLATES_DIR, template_name)

            try:
                # The template configs get pulled into the mlt.json file, so
                # don't grab a copy of that in the app directory
                copytree(templates_directory, self.app_name,
                         ignore=ignore_patterns(constants.TEMPLATE_CONFIG))

                # Get the template configs from the template and include them
                # when building the mlt json file
                param_file = os.path.join(templates_directory,
                                          constants.TEMPLATE_CONFIG)
                template_params = config_helpers.\
                    get_template_parameters_from_file(param_file)

                if not skip_crd_check:
                    kubernetes_helpers.check_crds(app_name=self.app_name)

                data = self._build_mlt_json(template_params)
                with open(os.path.join(self.app_name,
                                       constants.MLT_CONFIG), 'w') as f:
                    json.dump(data, f, indent=2)
                self._init_git_repo()
            except OSError as exc:
                if exc.errno == 17:
                    print(
                        "Directory '{}' already exists: delete before trying "
                        "to initialize new application".format(self.app_name))
                else:
                    traceback.print_exc()

                sys.exit(1)

    def _build_mlt_json(self, template_parameters):
        """generates the data to write to mlt.json"""
        data = {'name': self.app_name, 'namespace': self.app_name}
        if not self.args["--registry"]:
            raw_project_bytes = check_output(
                ["gcloud", "config", "list", "--format",
                 "value(core.project)"])
            project = raw_project_bytes.decode("utf-8").strip()
            data['gceProject'] = project
        else:
            data['registry'] = self.args["--registry"]
        if not self.args["--namespace"]:
            data['namespace'] = getpass.getuser()
        else:
            data['namespace'] = self.args["--namespace"]

        # Add template specific parameters to the data dictionary
        if template_parameters:
            template_data = data[constants.TEMPLATE_PARAMETERS] = {}
            for param in template_parameters:
                template_data[param["name"]] = param["value"]

        return data

    def _init_git_repo(self):
        """
        Initialize new git repo in the project dir and commit initial state.
        """
        process_helpers.run(["git", "init", self.app_name])
        process_helpers.run(["git", "add", "."], cwd=self.app_name)
        print(process_helpers.run(
            ["git", "commit", "-m", "Initial commit."], cwd=self.app_name))
