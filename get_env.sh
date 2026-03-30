# Source this file to set up the environment for GitLab Environment Toolkit
export PATH="$HOME/bin:$PATH"
source "$(dirname "${BASH_SOURCE[0]}")/gitlab-environment-toolkit/get-python-env/bin/activate"
echo "GitLab Environment Toolkit environment activated."
terraform --version | head -n 1
ansible --version | head -n 1
