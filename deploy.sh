#!/usr/bin/env bash
source activate grader
pushd serverconfig
ansible-playbook -i hosts setup_grader_server.yml
popd 