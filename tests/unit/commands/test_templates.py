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

import os
import shutil

from mlt.commands.templates import TemplatesCommand
from test_utils import project
from test_utils.io import catch_stdout


def test_template_list():
    args = {
        'template': 'test',
        'list': True,
        '--template-repo': project.basedir()
    }
    templates = TemplatesCommand(args)
    with catch_stdout() as caught_output:
        templates.action()
        assert caught_output.getvalue() is not None

def test_template_list_invalid_repo():
    args = {
        'template': 'test',
        'list': True,
        '--template-repo': "git@github.com:1ntelA1/mlt.git"
    }
    templates = TemplatesCommand(args)
    with catch_stdout() as caught_output:
        templates.action()
        assert caught_output.getvalue() is not None

def test_template_list_invalid_repo_dir():
    invalid_repo_dir = "/tmp/invalid-mlt-dir"
    args = {
        'template': 'test',
        'list': True,
        '--template-repo': invalid_repo_dir
    }

    if os.path.exists(invalid_repo_dir):
        shutil.rmtree(invalid_repo_dir)

    templates = TemplatesCommand(args)
    with catch_stdout() as caught_output:
        templates.action()
        assert caught_output.getvalue() is not None
