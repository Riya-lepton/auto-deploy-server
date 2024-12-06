#!/bin/bash
echo "Downloading artifact..."

gh run download --repo Riya-lepton/auto-deploy-server -n build-artifact --dir /home/lepton/riya_space/test
