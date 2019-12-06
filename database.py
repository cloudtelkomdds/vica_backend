import mysql.connector
from secret import Secret
from model.database_response import DatabaseResponse

class Database:
    READ = 0
    WRITE = 1

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
                return DatabaseResponse(data=cursor.fetchall(),
                                        message="",
                                        status=True)
            elif operation == Database.WRITE:
                cursor.execute(query, param)
                connection.commit()
                return DatabaseResponse(data=[],
                                        message="",
                                        status=True)
        except Exception as e:
            return DatabaseResponse(data=[],
                                    message=str(e),
                                    status=False)