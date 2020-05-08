import os
import psycopg2
from psycopg2 import sql
from typing import Union, List

#МОЖЕТ ЛИ УПАСТЬ СКОРОСТЬ ВЫПОЛНЕНИЯ КОМАНД
#ЕСЛИ НА КАЖДОМ ЗАПРОСЕ МЫ БУДЕМ ОТКРЫВАТЬ И ЗАКРЫВАТЬ ИНТЕРНЕТ СОЕДИНЕНИЕ?
#для редких операций (как функ. из _user_admission) это ничего страшного, 
#ведь они вызываются относительно_редко_
 
def get_connection(): #на локалке и в облаке использует разные url 
    db_url = os.getenv('DATABASE_URL')
    if db_url == 'localhost':
        db_password = os.getenv('DATABASE_PASSWORD')
        conn = psycopg2.connect(dbname = 'VocaBot_db', user = 'postgres', 
                    password = db_password, host = db_url)
    else: #if db_url is not 'localhost' (this is not local db)
        conn = psycopg2.connect(db_url, sslmode='require') 
    return conn

def cursor_exec_select(query: str) -> List[tuple]: 
    #даже если строк 0 возвращаемый тип - list (тогда пустой лист)
    #ans = None #how do I NoneType in mypy?
    conn = get_connection() #for "SELECT" queries
    with conn.cursor() as cursor:
        cursor.execute(query)
        ans = cursor.fetchall()
        print(len(ans))
    conn.close()
    return ans #возвращает лист тьюплов в любом случае

def cursor_exec_edit(query: str, info: str = None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
    conn.close()

def create_table(table_name: str):
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

def delete_table(table_name: str):
    conn = get_connection()
    cursor = conn.cursor()
    name_Table = "allowed_users"
    sqlDeleteTable = "DROP TABLE public." + name_Table
    cursor.execute(sqlDeleteTable)
    conn.commit()