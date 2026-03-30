#!/bin/bash
export PATH="$HOME/bin:$PATH"
source gitlab-environment-toolkit/get-python-env/bin/activate

echo "Verifying Setup..."
echo "------------------"
echo -n "Terraform: "
terraform --version | head -n 1
echo -n "Ansible: "
ansible --version | head -n 1
echo -n "Ansible Galaxy: "
ansible-galaxy --version | head -n 1
echo -n "TFLint: "
tflint --version | head -n 1
echo -n "Ansible Lint: "
ansible-lint --version
echo "------------------"
echo "Setup verified!"
