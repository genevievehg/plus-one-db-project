#!/bin/bash
apt-get update
NEEDRESTART_MODE=a apt-get install -y python3 python3-pip python3-venv jq awscli
git clone https://github.com/genevievehg/plus-one-db-project
cd plus-one-db-project/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

SECRET_NAME="${secret_name}"
DB_HOST="${db_endpoint}"
DB_PORT="${db_port}"
DB_NAME="${db_name}"
DB_ENDPOINT="${db_endpoint}"

SECRET_JSON=$(aws secretsmanager get-secret-value \
    --secret-id "$SECRET_NAME" \
    --query SecretString \
    --output text \
    --region eu-west-2)

USERNAME=$(echo "$SECRET_JSON" | jq -r '.username')
PASSWORD=$(echo "$SECRET_JSON" | jq -r '.password')


cat > .env <<EOF
PG_USER=$USERNAME
PG_PASSWORD=$PASSWORD
PG_HOST=$DB_ENDPOINT
PG_PORT=$DB_PORT
PG_DATABASE=$DB_NAME
JWT_SECRET=
DEBUG=False
EOF

uvicorn main:app --host 0.0.0.0 --port 8000
EOF