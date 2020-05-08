from _database import cursor_exec_select, cursor_exec_edit
import psycopg2
from typing import Union

def is_user_allowed(name: str, raw_user_id: int):
    user_id = str(raw_user_id)
    #self_autoinit_user(name, init_id)
    ans = False #презумпция недопуска 
    query = f"SELECT * FROM allowed_users WHERE id = '{user_id}' and is_blocked = false"
    lines = cursor_exec_select(query)
    if len(lines) == 1: #а больше быть не может, база данных в порядке
        ans = True
    return ans

def init_user(name: str, user_id: str): #also useful for unblocking users 
    try: #если пройдет - айдишник уникален и новый пользователь допущен 
        cursor_exec_edit("INSERT INTO allowed_users" + 
            f"(name, id, is_blocked) VALUES ('{name}', '{user_id}', false)")
        info = f'User "{name}" is allowed now'
    except psycopg2.errors.lookup('23505'):
        #чтобы ВСЦ не орал "Module 'psycopg2.errors' has no 'UniqueViolation' member"
        lines = cursor_exec_select(f"SELECT is_blocked FROM allowed_users WHERE id = '{user_id}'")
        is_user_blocked: bool = lines[0][0] #lines: List[tuple] или List[empty]
        #fetchone возвращает тьюпл, fetchall - лист тьюплов (список кортежей)
        if is_user_blocked: #если он есть, но заблочен - разблочить (ОТКЛ ПРИ _SELF_INIT)
            cursor_exec_edit("UPDATE allowed_users" + 
                f" SET is_blocked = false WHERE id = '{user_id}'")
            info = f'State of user "{name}" changed to active' #user unblocked
        else:
            info = f'User "{name}" is already admitted'
    return info

def block_user(name: Union[str, None], user_id: str):
    user_row: list = cursor_exec_select(
        f"SELECT * FROM allowed_users WHERE id = '{user_id}'")
    if len(user_row) == 1:
        name: str = user_row[0][0]
        #is_user_blocked: bool = user_row[2] если уже был заблокирован - молчим
        cursor_exec_edit("UPDATE allowed_users" + 
            f" SET is_blocked = true WHERE id = '{user_id}'")
        info = f'User "{name}" is not allowed more. Block is succsessfull'
    else: #if user_row == 0 (user_row = [])
        cursor_exec_edit("INSERT INTO allowed_users (name, id, is_blocked)"
             + f" VALUES ('{name}', '{user_id}', true)")
        info = (f'New user "{name}" added in database ' + 
            'but is not allowed to use bot still')
    return info

def self_autoinit_user(name: str, user_id: str):
    #то же, что и init_user, только разблочить себя нельзя
    pass