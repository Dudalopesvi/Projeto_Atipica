import os

DB_CONFIG = {
    "host":     os.environ.get("ATIPICA_DB_HOST", "localhost"),
    "port":     int(os.environ.get("ATIPICA_DB_PORT", "3306")),
    "user":     os.environ.get("ATIPICA_DB_USER", "root"),
    "password": os.environ.get("ATIPICA_DB_PASSWORD", "Jle102030"),
    "database": os.environ.get("ATIPICA_DB_NAME", "atipica"),
   
}