#!/bin/bash
set -xe

hugo build --cleanDestinationDir
npx wrangler deploy
