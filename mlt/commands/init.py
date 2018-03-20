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
import shutil
import
from subprocess import check_output
import traceback

from mlt import TEMPLATES_DIR
from mlt.commands import Command
from mlt.utils import process_helpers, git_helpers

from kubernetes import client
import kubernetes


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

        with git_helpers.clone_repo(template_repo) as temp_clone:
            templates_directory = os.path.join(
                temp_clone, TEMPLATES_DIR, template_name)

            try:
                shutil.copytree(templates_directory, self.app_name)

                # If crd-requirements.txt file exists in template
                # then check whether crd installed or not.
                crd_file = os.path.join(self.app_name, 'crd-requirements.txt')
                crd_list = []
                if os.path.exists(crd_file):
                    with open(crd_file) as f:
                        crd_list = f.read().splitlines()

                if not self._check_crds_exists(crd_list):
                    print("Do you want us to install operators? Please say yes or no")
                    flag = raw_input()
                    if flag is 'yes':
                        for crd in crd_list:
                            print("Installing {} operator on your k8 cluster".format(crd))
                            process_helpers.run(["make", "-f", "Makefile.{}".format(crd)], cwd=self.app_name)
                    else:
                        sys.exit(1)

                data = self._build_mlt_json()
                with open(os.path.join(self.app_name, 'mlt.json'), 'w') as f:
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

    def _build_mlt_json(self):
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

        return data

    def _init_git_repo(self):
        """
        Initialize new git repo in the project dir and commit initial state.
        """
        process_helpers.run(["git", "init", self.app_name])
        process_helpers.run(["git", "add", "."], cwd=self.app_name)
        print(process_helpers.run(
            ["git", "commit", "-m", "Initial commit."], cwd=self.app_name))

    def _load_kube_conf(self):
        kubernetes.config.load_kube_config(
            config_file=os.path.expanduser('~/.kube/config')
        )
        return client.ApiextensionsV1beta1Api()

    def _check_crds_exists(self, crd_list):
        """
        Check if given crd list installed on K8 or not.
        """
        crd_client = self._load_kube_conf()
        current_crds = [x['spec']['names']['kind'].lower()
                        for x in crd_client.list_custom_resource_definition().to_dict()['items']]
        flag = True
        for crd in crd_list:
            if crd not in current_crds:
                flag = False
                print("Required \"{}\" operator not installed".format(crd))

        return flag


