from mysql.connector import connect, Error
from dotenv import load_dotenv
import os

load_dotenv()

def init_database():
    try:
        connection = connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(connection, query, params=None):
    # Clean the query of any markdown formatting
    query = query.replace('```sql', '').replace('```', '').strip()
    
    cursor = connection.cursor()
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    cursor.close()
    return result