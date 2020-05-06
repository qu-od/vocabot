import os
import psycopg2 as db
from psycopg2 import sql

def is_user_allowed(int_cmd_user_id: int):
    cmd_user_id = str(int_cmd_user_id)
    ans = False #презумпция недопуска 
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM allowed_users LIMIT 10')
    records = cursor.fetchall()
    for elem in records:
        user_id = elem[1]
        if user_id: #если ячейка не пуста (она не должна, ведь этот столбец - primary key)
            if user_id.startswith("#") == False: #если эта ячейка в не закоменчена мной
                print(type(user_id), type(cmd_user_id))
                print(user_id, cmd_user_id)
                if user_id == cmd_user_id: #если айдишник записан
                    ans = True
                    cursor.close()
                    conn.close()
                    return ans
    cursor.close()
    conn.close()
    return ans

def init_user(name: str, user_id: str):
    conn = get_connection()
    with conn.cursor() as cursor:
        conn.autocommit = True
        insert = sql.SQL('INSERT INTO allowed_users' + 
        f"(name, id) VALUES ('{name}', '{user_id}')" )
        #sql.SQL(',').join(map(sql.Literal, values))
        cursor.execute(insert)
    cursor.close()
    conn.close()
#далее функции для разрешения  на отдельные комманды

def get_connection(): #на локалке и в облаке использует разные url 
    db_url = os.getenv('DATABASE_URL')
    if db_url == 'localhost':
        db_password = os.getenv('DATABASE_PASSWORD')
        conn = db.connect(dbname = 'VocaBot_db', user = 'postgres', 
                    password = db_password, host = db_url)
    else: #if db_url is not 'localhost' (this is not local db)
        conn = db.connect(db_url, sslmode='require') 
    return conn

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    name_Table = "allowed_users"
    sqlCreateTable = ("CREATE TABLE public." + name_Table + 
    " (name character varying(50), id character varying(30), PRIMARY KEY (id));") 
    cursor.execute(sqlCreateTable)
    conn.commit()

    sqlGetTableList = "SELECT table_schema,table_name FROM information_schema.tables where table_schema='public' ORDER BY table_schema,table_name ;"
    cursor.execute(sqlGetTableList)
    tables = cursor.fetchall()
    for table in tables:
        print(table)

def delete_table():
    conn = get_connection()
    cursor = conn.cursor()
    name_Table = "allowed_users"
    sqlDeleteTable = "DROP TABLE public." + name_Table
    cursor.execute(sqlDeleteTable)
    conn.commit()