import cx_Oracle
from sshtunnel import SSHTunnelForwarder

# SSH server details
ssh_host = "moon.cs.ryerson.ca"
ssh_port = 22
ssh_username = "asher"
ssh_password = "jEEET9S*3Sj@rAU"

# Oracle DB credentials
oracle_username = "asher"
oracle_password = "07101750"

# Oracle DSN based on the provided connection details
oracle_dsn = (
    "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)"
    "(Host=localhost)(Port=1521))"
    "(CONNECT_DATA=(SID=orcl12c)))"
)

# Set up the SSH tunnel
try:
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=("oracle12c.scs.ryerson.ca", 1521),
        local_bind_address=("localhost", 1521)
    ) as tunnel:
        
        # Establish the Oracle database connection using cx_Oracle
        connection = cx_Oracle.connect(oracle_username, oracle_password, oracle_dsn)
        print("Database connection successful")

        # Example query
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM user_tables")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                print(row)
        else:
            print("No data found")

        # Close resources
        cursor.close()
        connection.close()

except Exception as e:
    print("Connection error:", e)