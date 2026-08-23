#!/bin/bash
set -e

# Change to project root directory
cd "$(dirname "$0")/.."

# Load .env
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | xargs)
fi

echo "Registering Debezium Postgres Source Connector..."

curl -s -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:8083/connectors/ -d "
{
  \"name\": \"smartoffice-postgres-source\",
  \"config\": {
    \"connector.class\": \"io.debezium.connector.postgresql.PostgresConnector\",
    \"tasks.max\": \"1\",
    \"database.hostname\": \"source-postgres\",
    \"database.port\": \"5432\",
    \"database.user\": \"${DEBEZIUM_DB_USER}\",
    \"database.password\": \"${DEBEZIUM_DB_PASSWORD}\",
    \"database.dbname\": \"smart_office\",
    \"topic.prefix\": \"smartoffice\",
    \"plugin.name\": \"pgoutput\",
    \"slot.name\": \"smartoffice_debezium_slot\",
    \"publication.name\": \"smartoffice_pub\",
    \"publication.autocreate.mode\": \"disabled\",
    \"schema.include.list\": \"hr,office,access,meeting,signing,iot\",
    \"snapshot.mode\": \"initial\",
    \"heartbeat.interval.ms\": \"10000\"
  }
}
" | jq

echo -e "\nConnector submitted!"
