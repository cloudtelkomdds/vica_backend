import mysql.connector
from Secret import Secret

class Database:
    READ = 0
    WRITE = 1

    def __init__(self):
        self.connection = mysql.connector.connect(host=Secret.host,
                                                  user=Secret.user,
                                                  passwd=Secret.password,
                                                  database=Secret.db)

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
