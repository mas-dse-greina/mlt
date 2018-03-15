# mlt
Machine Learning Container Tool

[![CircleCI](https://circleci.com/gh/NervanaSystems/mlt.svg?style=svg&circle-token=239cc4305ca25063bf9a40cd332c822f5e64663f)](https://circleci.com/gh/NervanaSystems/mlt)

`mlt` aids in the creation of containers for machine learning jobs.
It does so by making it easy to use container and kubernetes object templates.

![MLT flow diagram](docs/mlt.png)

We have found it useful to share project templates for various machine learning frameworks. Some have native support from Kubernetes operators, such as mxnet and TensorFlow. Others do not, but still have best practices for how to run on a Kubernetes cluster.

On top of getting boiler plate code at the beginning of a project to work, the best practices may change over time. `mlt` allows existing projects to adapt to these without having to reset and start over.

![MLT watch](docs/watch.png)

`mlt` addresses another aspect of the application development: _iterative_ container creation. Storage and container creation is supposed to be fast - so why not rebuild containers automatically?
`mlt` has a `--watch` option, which lets you write code and have an IDE-like experience.
When changes are detected, a timer starts and triggers container rebuilds.
lint and unit tests can be run in this step, as an early indicator of whether the code will run in the cluster.
When the container is built, it is pushed to the cluster container registry.
From here, it is a quick step to redeploy the Kubernetes objects, through `mlt deploy`


## Build

Prerequisites:
- git
- python
- virtualenv

Installation:

```bash
$ make
# Two different options to running `mlt`:
$ source ./.venv/bin/activate
# add this to ~/.bash_profile, ~/.bashrc, etc and then source it
alias mlt='{path_to_mlt_repo}/.venv/bin/mlt'
```

## Usage summary

```bash
# cd outside of the mlt tree
$ cd ..
$ mlt templates list
Template        Description
--------------  ----------------------------------------------------------------------------------------------
hello-world     A TensorFlow python HelloWorld example run through Kubernetes Jobs.
tf-distributed  A distributed TensorFlow matrix multiplication run through the TensorFlow Kubernetes Operator.
tf-single-node

$ mlt init my-app --template=hello-world
[master (root-commit) 40239a2] Initial commit.
 7 files changed, 191 insertions(+)
 create mode 100644 mlt.json
 create mode 100644 Dockerfile
 create mode 100644 Makefile
 create mode 100644 k8s-templates/tfjob.yaml
 create mode 100644 k8s/README.md
 create mode 100644 main.py
 create mode 100644 requirements.txt

$ cd my-app
$ mlt build
Starting build my-app:71fb176d-28a9-46c2-ab51-fe3d4a88b02c
Building |######################################################| (ETA:  0:00:00)
Pushing  |######################################################| (ETA:  0:00:00)
Built and pushed to gcr.io/my-project-12345/my-app:71fb176d-28a9-46c2-ab51-fe3d4a88b02c

$ mlt deploy
Deploying gcr.io/my-project-12345/my-app:71fb176d-28a9-46c2-ab51-fe3d4a88b02c

Inspect created objects by running:
  $ kubectl get --namespace=my-app all
```
