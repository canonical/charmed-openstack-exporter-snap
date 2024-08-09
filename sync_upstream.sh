#!/bin/bash
# Update the snap folders that contains the hooks and local scripts

# the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# the temp directory used, under $TMPDIR or /tmp
WORK_DIR=$(mktemp -d)

# check if tmp dir was created
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
  echo "Could not create temp dir"
  exit 1
fi

# deletes the temp directory
trap "rm -rf $WORK_DIR" EXIT

git clone --sparse https://github.com/openstack-exporter/openstack-exporter.git "$WORK_DIR/openstack-exporter"
cd "$WORK_DIR/openstack-exporter"
git sparse-checkout set snap/local snap/hooks
cp -r snap/local "$DIR/snap/"
cp -r snap/hooks "$DIR/snap/"
