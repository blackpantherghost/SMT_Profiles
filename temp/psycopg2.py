import psycopg2

# Database connection details
DB_HOST = "your_server_ip_or_hostname"
DB_PORT = 5432
DB_NAME = "info_db"
DB_USER = "your_username"
DB_PASSWORD = "your_password"

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()
    print("Connected to database successfully.\n")

    # Get all table names from public schema
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
    else:
        for table in tables:
            table_name = table[0]
            print(f"\n--- Contents of table: {table_name} ---")

            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Get column names
            col_names = [desc[0] for desc in cursor.description]
            print("Columns:", col_names)

            for row in rows:
                print(row)

    # cursor.close()
    # conn.close()

except Exception as e:
    print("Error while connecting to PostgreSQL:", e)

try:
    sql = """
    INSERT INTO info
    VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (104, 'MAN', 'Tan'))
    conn.commit()
    print("Row Inserted successfully")
    cursor.close()
    conn.close()

except Exception as e:
    print("Error while Row Insertion:", e)

# firewall.cpl (Inbound, Outbound rules), #services.msc, pg_hba.conf (host    all    all    0.0.0.0/0    md5), 
# postgresql.conf (listen_addresses = '*')


######################################################################
# SSL
# hostssl all all <CLIENT_IP>/32 scram-sha-256
"""
❌ REMOVE from postgresql.conf : 
listen_addresses = '*'
With:
listen_addresses = 'your_server_ip'
ssl = on
password_encryption = scram-sha-256

from pg_hba.conf update the following :
#hostssl all all <CLIENT_IP>/32 scram-sha-256

Need to update :

✅ Force SSL (required for hostssl)
✅ Use scram-sha-256 compatible auth
✅ Close connections safely
✅ Avoid SQL injection for table reads
❌ Removed insecure config comments (0.0.0.0/0, md5, listen_addresses='*')

| Issue                    | Status  |
| ------------------------ | ------- |
| `md5` authentication     | ❌ Fixed |
| No TLS encryption        | ❌ Fixed |
| `0.0.0.0/0` access       | ❌ Fixed |
| SQL injection risk       | ❌ Fixed |
| Unclean connection close | ❌ Fixed |

Uses encrypted SSL
Works with hostssl
Is compatible with modern PostgreSQL security
Is safe for LAN/VPN or production

After connecting, run:
SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid();

"""
######################################################################

import psycopg2
from psycopg2 import sql

# Database connection details
DB_HOST = "your_server_ip_or_hostname"   # must match cert CN if using verify-full
DB_PORT = 5432
DB_NAME = "info_db"
DB_USER = "your_username"
DB_PASSWORD = "your_password"

try:
    # Connect to PostgreSQL using SSL (required for hostssl)
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"   # IMPORTANT
        # For higher security:
        # sslmode="verify-full",
        # sslrootcert="/path/to/ca.crt"
    )

    cursor = conn.cursor()
    print("Connected to database successfully.\n")

    # Get all table names from public schema
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
    else:
        for table in tables:
            table_name = table[0]
            print(f"\n--- Contents of table: {table_name} ---")

            # Safe SQL identifier usage
            cursor.execute(
                sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            )
            rows = cursor.fetchall()

            # Get column names
            col_names = [desc[0] for desc in cursor.description]
            print("Columns:", col_names)

            for row in rows:
                print(row)

    # Insert data
    insert_sql = """
        INSERT INTO info (id, code, name)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert_sql, (104, 'MAN', 'Tan'))
    conn.commit()
    print("Row inserted successfully")

except Exception as e:
    print("Error:", e)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()





