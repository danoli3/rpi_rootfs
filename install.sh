#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

sudo apt update && sudo apt dist-upgrade -y
sudo apt-get install -y build-essential gawk gcc g++ gfortran git texinfo bison libncurses-dev tar wget qemu-user-static rsync xz-utils unzip python3 python3-pip