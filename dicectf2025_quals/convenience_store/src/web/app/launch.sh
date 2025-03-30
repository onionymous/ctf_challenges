#!/bin/sh
cd /app
mkdir instance
ADMIN_PASSWORD_HASH=$(echo -n "$ADMIN_PASSWORD" | sha256sum | awk '{print $1}')
echo Admin password hash: $ADMIN_PASSWORD_HASH
sed -i "s/ADMIN_PASSWORD_HASH/${ADMIN_PASSWORD_HASH}/" database_setup.sql
sed -i "s/THE_FLAG/${THE_FLAG:-fakeflag}/" database_setup.sql
cat database_setup.sql
sqlite3 instance/database.db < database_setup.sql
gunicorn --bind 0.0.0.0:8000 -w 4 'main:app'