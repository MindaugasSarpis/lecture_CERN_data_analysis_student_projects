#!/bin/bash

echo "=== Checking Node.js Version ==="
echo "Node.js version: $(node --version)"
echo "Node.js path: $(which node)"
echo "NPM version: $(npm --version)"
echo "================================"

# Check if Node.js 18 is being used (as specified in .platform/nodejs/configuration.yml)
NODE_VERSION=$(node --version)
if [[ $NODE_VERSION == v18* ]]; then
    echo "✅ Node.js 18 detected - .platform/nodejs/configuration.yml is working!"
elif [[ $NODE_VERSION == v22* ]]; then
    echo "⚠️  Node.js 22 detected - .platform/nodejs/configuration.yml may not be applied!"
    echo "⚠️  Check AWS EB Platform Configuration."
else
    echo "ℹ️  Node.js version: $NODE_VERSION"
fi

