# Template Developers Manual

The easiest way to add a new template to MLT is to make a copy of one
of the existing templates and then modify it.  The following
instructions will go through those steps:

1. Start by making a copy of one of the folders in the `mlt-templates`
 directory.  Either start with something simple like the `hello-world`
 template, or pick a template that is similar to the one that you are
 going to add.

2. Rename the new folder with the name for your template.

3. Update the `README.md` file with a short description of your
template.  Note that this is the description that will be displayed with
`mlt templates list`

4. Other files that typically need to be modified for new templates are:
* `*.py` files
* `requirements.txt` with any libraries that your app uses
* `Dockerfile` if the name of the python file to execute is different,
etc.
* `k8s-templates/job.yaml` for the kubernetes job may need to be
modified depending on if a CRD is used, if multiple replicas are needed,
if environment variables need to be set, etc.  Note that all files in
the `k8s-templates` directory can have variables like `$app`, `$run`,
and `$image` that will be subbed into the template when the app is
deployed.
* `parameters.json` (optional) to define any _additional_ parameters
specific to your template.  These parameters are added to the app's
`mlt.json` file when it's initialized.  The parameter values are subbed
in to the `k8s-templates` directory when the app is deployed.

5. To test your template, you need to use the `--template-repo`
parameter with `mlt templates list` and `mlt templates init` in order
to specify the git url for  template repo (otherwise, this defaults to
`git@github.com:IntelAI/mlt.git`).

