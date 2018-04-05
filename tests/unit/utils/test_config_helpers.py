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

import pytest

from mlt.utils import constants
from mlt.utils.config_helpers import load_config, get_template_parameters
from test_utils.io import catch_stdout


def test_needs_init_command_bad_init():
    with catch_stdout() as caught_output:
        with pytest.raises(SystemExit) as bad_init:
            load_config()
            assert caught_output.getvalue() == "This command requires you " + \
                   "to be in an `mlt init` built directory"
            assert bad_init.value.code == 1


def test_get_empty_template_params():
    config = {"namespace": "foo", "registry": "bar",
              constants.TEMPLATE_PARAMETERS: {}}
    assert get_template_parameters(config) == {}


def test_get_template_params():
    config = {"namespace": "foo", "registry": "bar",
              constants.TEMPLATE_PARAMETERS:
                  {"epochs": "10", "num_workers": "4"}}
    assert get_template_parameters(config) == \
        {"epochs": "10", "num_workers": "4"}
