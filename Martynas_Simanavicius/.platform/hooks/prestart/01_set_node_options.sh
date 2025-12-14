#!/bin/bash

# Note: --openssl-legacy-provider is now passed directly in package.json start script
# This is more reliable than using NODE_OPTIONS environment variable
# The flag is supported in Node.js 17-21, but may be deprecated in Node.js 22+

echo "🔒 SSL/TLS: --openssl-legacy-provider flag is set in start script"
echo "🔍 Node.js version: $(node --version)"

