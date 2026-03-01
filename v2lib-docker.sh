#!/usr/bin/env bash
# Wrapper to run the containerized v2lib tool
# Maps current directory to /workspace, so any relative paths passed
# into args like --in tests/simple_adder.v will correctly resolve in /workspace

WORK_DIR=$(pwd)

# Convert any absolute paths starting with $WORK_DIR to relative paths
# so that the container sees them relative to /workspace
args=()
for arg in "$@"; do
    if [[ "$arg" == "$WORK_DIR"* ]]; then
        rel_path="${arg#$WORK_DIR/}"
        args+=("/workspace/${rel_path}")
    else
        args+=("$arg")
    fi
done

docker run --user $(id -u):$(id -g) --rm \
    -v "${WORK_DIR}:/workspace" \
    v2lib-tool "${args[@]}"
