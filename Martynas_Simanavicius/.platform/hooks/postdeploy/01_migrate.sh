#!/bin/bash

# Post-deployment migration hook
# This script runs database migrations after deployment
# Uncomment and configure if you want automatic migrations

echo "Running database migrations..."
cd /var/app/current
npm run typeorm migration:run || echo "Migration failed or no migrations to run"

# For now, migrations should be run manually via SSH or EB console
echo "Post-deployment hook executed. Run migrations manually if needed."

