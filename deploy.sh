#!/bin/bash
set -xe

REMOTE_HOST="wired-micro"
REMOTE_PATH="/home/ubuntu/caddy/site/killall.systems"
LOCAL_BUILD_DIR="public"

hugo build
rsync -avz --delete "$LOCAL_BUILD_DIR"/ "$REMOTE_HOST:$REMOTE_PATH/"
