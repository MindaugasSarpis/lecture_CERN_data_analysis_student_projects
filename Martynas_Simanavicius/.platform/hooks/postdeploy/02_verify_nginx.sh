#!/bin/bash

echo "=== Verifying Nginx Configuration ==="

# Check if config file exists
if [ -f /etc/nginx/conf.d/proxy.conf ]; then
    echo "✅ Found /etc/nginx/conf.d/proxy.conf"
    echo "Content:"
    cat /etc/nginx/conf.d/proxy.conf
else
    echo "⚠️  /etc/nginx/conf.d/proxy.conf not found"
fi

# Check .platform config
if [ -f /var/proxy/staging/nginx/conf.d/client_max_body_size.conf ]; then
    echo "✅ Found .platform nginx config"
    cat /var/proxy/staging/nginx/conf.d/client_max_body_size.conf
fi

# Test nginx config
echo ""
echo "Testing nginx configuration..."
sudo nginx -t 2>&1

# Check current nginx settings
echo ""
echo "=== Current Nginx Settings ==="
sudo nginx -T 2>&1 | grep -i "client_max_body_size" || echo "client_max_body_size not found in nginx config"

echo "=== Verification Complete ==="

