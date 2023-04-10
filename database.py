import psycopg2, os

def database_connect():
    conn = None
    try:
        # deploying on Fly.io
        database_url = os.environ.get("DATABASE_URL")
        # testing locally

        conn = psycopg2.connect(database_url)  
    except psycopg2.OperationalError as e:
        print("database: database_connection: Database Connection Failed!\n")
        print(e)
    except psycopg2.ProgrammingError as e:
        print("database: database_connection: Incorrect username and password!\n")
        print(e)
    except Exception:
        print(e)

    return conn

def get_role(id):
    conn = database_connect()
    if (conn is None):
        return None
    
    cursor = conn.cursor()
    sql = "SELECT role from Users WHERE id=%s"
    cursor.execute(sql, (id,))
    result = cursor.fetchall()
    if len(result) == 0:
        return None
    role = result[0][0]
    return role

def add_user(profile):
    conn = database_connect()
    if (conn is None):
        return None
    
    cursor = conn.cursor()
    sql = "INSERT INTO Users VALUES (%s, %s, 'user')"
    try:
        cursor.execute(sql, (profile.user_id, profile.display_name))
        return True

    except KeyError as e:
        print(f"database: add_user: key {e} was not found in the given profile")
        return False

    except psycopg2.errors.UniqueViolation as e:
        print(f"database: add_user: User ID '{profile.user_id}' already existed in the Users table")
        return False

    except psycopg2.errors.StringDataRightTruncation as e:
        print(f"database: add_user: User ID '{profile.user_id}' length is too long")
        return False
    
    
if __name__ == "__main__":
    pass