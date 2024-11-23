import cx_Oracle
from sshtunnel import SSHTunnelForwarder
import configparser
from tabulate import tabulate


def load_config(config_path="config.ini"):
    """
    Load the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def create_ssh_tunnel(config):
    """
    Create an SSH tunnel based on the configuration file.
    """
    ssh_host = config['ssh']['hostname']
    ssh_port = int(config.get('ssh', 'port', fallback=22))
    ssh_username = config['ssh']['username']
    ssh_password = config['ssh']['password']

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=("oracle12c.scs.ryerson.ca", 1521),
        local_bind_address=("localhost", 1521)
    )
    return tunnel


def connect_to_database(config):
    """
    Establish a connection to the Oracle database.
    """
    db_user = config['database']['user']
    db_password = config['database']['password']
    oracle_dsn = (
        "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)"
        "(Host=localhost)(Port=1521))"
        "(CONNECT_DATA=(SID=orcl12c)))"
    )
    connection = cx_Oracle.connect(db_user, db_password, oracle_dsn)
    return connection

"""
Execute an SQL query using the provided cursor.
"""

def execute_sql(query, cursor):
        try:
            query_type = query.strip().split()[0].upper()

            if query_type == "SELECT":
                cursor.execute(query)
                column_names = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                if rows:
                    print (tabulate(rows, headers=column_names, tablefmt="grid"))
                    return str((tabulate(rows, headers=column_names, tablefmt="grid")))
                else:
                    print ("No data found.")
                    return ("No data found.")
            else:
                cursor.execute(query)
                cursor.connection.commit()
                print (f"Query executed successfully: {query_type}")
                return (f"Query executed successfully: {query_type}")

        except cx_Oracle.DatabaseError as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"Error occurred: {e}")

def main():
    """
    Main function to interact with the database.
    """
    try:
        config = load_config()

        with create_ssh_tunnel(config) as tunnel:
            print("SSH Tunnel established")

            connection = connect_to_database(config)
            print("Database connection successful")

            cursor = connection.cursor()

            while True:
                print("\nEnter an SQL statement (or type 'exit' to quit):")
                user_input = input("SQL> ").strip()

                if user_input.lower() == "exit":
                    print("Exiting the program.")
                    break

                execute_sql(cursor, user_input)

            cursor.close()
            connection.close()

    except Exception as e:
        print("Connection error:", e)


if __name__ == "__main__":
    main()