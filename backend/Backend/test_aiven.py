import os
import sys
import mysql.connector
from urllib.parse import urlparse

# This script tests connection to Aiven MySQL.
# Pass a DATABASE_URL environment variable, or it will try to read individual DB_* env vars.
db_url = os.environ.get("DATABASE_URL")

try:
    if db_url:
        print("Connecting using DATABASE_URL...")
        parsed = urlparse(db_url)
        # Handle ssl-disabled query param if present
        ssl_disabled = False
        if "ssl_disabled=False" in db_url:
            ssl_disabled = False
        
        # mysql.connector expects user, password, host, port, database
        # URL format: mysql+mysqlconnector://user:password@host:port/database
        # Let's extract the credentials
        user = parsed.username
        password = parsed.password
        # urllib.parse might keep '+' or URL-encoded characters in username/password
        from urllib.parse import unquote
        if user:
            user = unquote(user)
        if password:
            password = unquote(password)
            
        host = parsed.hostname
        port = parsed.port or 3306
        database = parsed.path.lstrip('/')
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
    else:
        print("Connecting using individual DB_* environment variables...")
        host = os.environ.get("DB_HOST", "localhost")
        user = os.environ.get("DB_USER", "avnadmin")
        password = os.environ.get("DB_PASSWORD", "")
        port = int(os.environ.get("DB_PORT", 12793))
        database = os.environ.get("DB_NAME", "defaultdb")
        
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
    
    print("Connection successful!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
    sys.exit(1)
