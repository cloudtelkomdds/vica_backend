import mysql.connector
from Secret import Secret

class Database:
    READ = 0
    WRITE = 1

    def __init__(self):
        pass

    @staticmethod
    def execute(operation, query, param=None):
        connection = mysql.connector.connect(host=Secret.HOST,
                                             user=Secret.USER,
                                             passwd=Secret.PASSWORD,
                                             database=Secret.DB)
        cursor = connection.cursor()
        try:
            if operation == Database.READ:
                if param is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, param)
                return True, cursor.fetchall()
            elif operation == Database.WRITE:
                cursor.execute(query, param)
                connection.commit()
                return True, cursor.rowcount
        except Exception as e:
            return False, e