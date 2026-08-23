GRANT CONNECT
ON DATABASE smart_office
TO debezium_user;

GRANT USAGE
ON SCHEMA
    hr,
    office,
    access,
    meeting,
    signing,
    iot
TO debezium_user;

GRANT SELECT
ON ALL TABLES IN SCHEMA
    hr,
    office,
    access,
    meeting,
    signing,
    iot
TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA hr
GRANT SELECT ON TABLES TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA office
GRANT SELECT ON TABLES TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA access
GRANT SELECT ON TABLES TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA meeting
GRANT SELECT ON TABLES TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA signing
GRANT SELECT ON TABLES TO debezium_user;

ALTER DEFAULT PRIVILEGES
FOR ROLE smartoffice_admin
IN SCHEMA iot
GRANT SELECT ON TABLES TO debezium_user;
