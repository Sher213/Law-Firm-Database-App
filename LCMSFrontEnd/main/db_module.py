import cx_Oracle
from sshtunnel import SSHTunnelForwarder
import configparser

class DBModule:
    def __init__(self, config_path):
        """
        Initialize the DBModule with config data.
        """
        self.config = self.load_config(config_path)
        self.tunnel = None
        self.connection = None

    def load_config(self, config_path):
        """
        Load the configuration file.
        """
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def create_ssh_tunnel(self):
        """
        Create an SSH tunnel.
        """
        ssh_host = self.config['ssh']['hostname']
        ssh_port = int(self.config.get('ssh', 'port', fallback=22))
        ssh_username = self.config['ssh']['username']
        ssh_password = self.config['ssh']['password']

        self.tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            remote_bind_address=("oracle12c.scs.ryerson.ca", 1521),
            local_bind_address=("localhost", 1521)
        )
        self.tunnel.start()

    def connect_to_database(self):
        """
        Establish a connection to the Oracle database.
        """
        db_user = self.config['database']['user']
        db_password = self.config['database']['password']
        oracle_dsn = (
            "(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)"
            "(Host=localhost)(Port=1521))"
            "(CONNECT_DATA=(SID=orcl12c)))"
        )
        self.connection = cx_Oracle.connect(db_user, db_password, oracle_dsn)

    def execute_sql(self, query):
        """
        Execute an SQL query and return the result.
        """
        cursor = self.connection.cursor()
        try:
            query_type = query.strip().split()[0].upper()
            if query_type == "SELECT":
                cursor.execute(query)
                column_names = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                if rows:
                    return rows, column_names
                else:
                    return "No data found.", []
            else:
                cursor.execute(query)
                self.connection.commit()
                return f"Query executed successfully: {query_type}", []
        except cx_Oracle.DatabaseError as e:
            return f"Database error: {e}", []
        finally:
            cursor.close()

    def close(self):
        """
        Close the database connection and SSH tunnel.
        """
        if self.connection:
            self.connection.close()
        if self.tunnel:
            self.tunnel.stop()