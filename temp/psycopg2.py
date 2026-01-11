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
