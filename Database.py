import mysql.connector

class Database:
    #TODO: Move configuration to external file
    host = "3.217.77.161"
    user = "root"
    password = "6352"
    db = "db_staging_cloudpbx_telkom"

    READ = 0
    WRITE = 1

    def __init__(self):
        self.connection = mysql.connector.connect(host=Database.host,
                                                  user=Database.user,
                                                  passwd=Database.password,
                                                  database=Database.db)

    def execute(self, operation, query, param=None):
        cursor = self.connection.cursor()
        try:
            if operation == Database.READ:
                if param is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, param)
                return True, cursor.fetchall()
            elif operation == Database.WRITE:
                cursor.execute(query, param)
                self.connection.commit()
                return True, cursor.rowcount
        except Exception as e:
            return False, e
