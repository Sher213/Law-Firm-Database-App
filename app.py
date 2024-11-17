import cx_Oracle
from sshtunnel import SSHTunnelForwarder
import configparser
from tabulate import tabulate

# Initialize the configparser
config = configparser.ConfigParser()

# Read the config file
config.read('config.ini')

# Access values from the config file
db_user = config['database']['user']
db_password = config['database']['password']

ssh_host = config['ssh']['hostname']
ssh_port = 22
ssh_username = config['ssh']['username']
ssh_password = config['ssh']['password']

# Oracle DSN based on the provided connection details
oracle_dsn = (
    "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)"
    "(Host=localhost)(Port=1521))"
    "(CONNECT_DATA=(SID=orcl12c)))"
)

# Function to execute SQL statements
def execute_sql(cursor, query):
    try:
        # Determine the type of query
        query_type = query.strip().split()[0].upper()

        if query_type == "SELECT":
            cursor.execute(query)
            # Fetch column names and rows
            column_names = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            # Print results in tabular format
            if rows:
                print(tabulate(rows, headers=column_names, tablefmt="grid"))
            else:
                print("No data found.")
        else:
            # For non-SELECT queries, execute and commit changes
            cursor.execute(query)
            cursor.connection.commit()
            print(f"Query executed successfully: {query_type}")
    except cx_Oracle.DatabaseError as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

# Main code block
try:
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=("oracle12c.scs.ryerson.ca", 1521),
        local_bind_address=("localhost", 1521)
    ) as tunnel:

        # Establish the Oracle database connection using cx_Oracle
        connection = cx_Oracle.connect(db_user, db_password, oracle_dsn)
        print("Database connection successful")

        cursor = connection.cursor()

        while True:
            print("\nEnter an SQL statement (or type 'exit' to quit):")
            user_input = input("SQL> ").strip()

            if user_input.lower() == "exit":
                print("Exiting the program.")
                break

            # Execute the SQL statement
            execute_sql(cursor, user_input)

        # Close resources
        cursor.close()
        connection.close()

except Exception as e:
    print("Connection error:", e)