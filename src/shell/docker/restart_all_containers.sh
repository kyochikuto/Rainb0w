#!/bin/bash
source $PWD/src/shell/base/colors.sh
source $PWD/src/shell/docker/docker_utils.sh

fn_restart_docker_container "sing-box"
fn_restart_docker_container "nginx"

echo -e "${B_GREEN}<< Finished applying changes! >>${RESET}"
