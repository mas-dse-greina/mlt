#!/usr/bin/env python
"""mlt.
Usage:
  mlt (-h | --help)
  mlt --version
  mlt init [--template=<template> --template-repo=<repo>]
      [--registry=<registry> --namespace=<namespace] <name>
  mlt update [--template-repo=<repo>] [--template=<template>]
  mlt build [--watch]
  mlt deploy [--no-push]
  mlt undeploy
  mlt (template | templates) list [--template-repo=<repo>]

Options:
  --template=<template>   Template name for app
                          initialization [default: hello-world].
  --template-repo=<repo>  Git URL of template repository.
                          [default: git@github.com:NervanaSystems/mlt.git]
  --registry=<registry>   Container registry to use.
                          If none is set, will attempt to use gcloud.
  --namespace=<namespace> Kubernetes Namespace to use.
                          If none is set, will attempt to create or
                          use a namespace identical to username.
"""
from docopt import docopt

from mlt.commands import (BuildCommand, DeployCommand, InitCommand,
                          TemplatesCommand, UndeployCommand, UpdateCommand)

# every available command and its corresponding action will go here
COMMAND_MAP = (
    ('build', BuildCommand),
    ('deploy', DeployCommand),
    ('init', InitCommand),
    ('template', TemplatesCommand),
    ('templates', TemplatesCommand),
    ('undeploy', UndeployCommand),
    ('update', UpdateCommand),
)


def run_command(args):
    """maps params from docopt into mlt commands"""
    for command, CommandClass in COMMAND_MAP:
        if args[command]:
            CommandClass(args).action()
            return


def main():
    args = docopt(__doc__, version="ML Container Templates v0.0.1")
    run_command(args)
