#!/bin/bash
echo "Downloading artifact..."

gh run download --repo Riya-lepton/auto-deploy-server --artifact build-artifact --dir /var/www/html
