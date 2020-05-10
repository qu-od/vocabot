from _database import cursor_exec_select, cursor_exec_edit
import psycopg2
from typing import Union

def is_user_allowed(name: str, raw_user_id: int):
    user_id = str(raw_user_id)
    #self_autoinit_user(name, init_id)
    ans = False #презумпция недопуска 
    query = (f"SELECT * FROM allowed_users WHERE user_id = '{user_id}' " +
        "and is_blocked = false")
    lines = cursor_exec_select(query)
    if len(lines) == 1: #а больше быть не может, база данных в порядке
        ans = True
    return ans


#---------------------------ИНИЦИАЛИЗАЦИЯ ЮЗЕРА--------------------------------
#-----ЕСЛИ юзера не было вообще     : записать в таблицу допусков его. 
#  Выдать именную табличку-словарь, сделать его строку в langs_config
#-----ЕСЛИ юзер был (в блоке)       : разблокировать его в таблице допусков
#  -если у него уже была табличка-словарь - ничего не делать (в langs_config он есть)
#  -если у него таблички-словаря не было, то создать ее ему и записать в langs_config
#-----ЕСЛИ юзер уже был (не в блоке): ничего не далать
def init_user(name: str, user_id: str): #also useful for unblocking users 
    try: #если пройдет - айдишник уникален и новый пользователь допущен
        cursor_exec_edit("INSERT INTO allowed_users " + 
            f"VALUES ('{name}', '{user_id}', false)")
        #db_info = add_user_to_database(name, user_id) #создали словарь и строку-конфиг
        info = f'User "{name}" is allowed now'
    except psycopg2.errors.lookup('23505'): #если айдишник уже записан в табличку allowed_users
        #чтобы ВСЦ не орал "Module 'psycopg2.errors' has no 'UniqueViolation' member"
        lines = cursor_exec_select("SELECT is_blocked FROM allowed_users " +
                f"WHERE user_id = '{user_id}'")
        is_user_blocked: bool = lines[0][0] #lines: List[tuple] или List[empty]
        #fetchone возвращает тьюпл, fetchall - лист тьюплов (список кортежей)
        if is_user_blocked: #если он есть, но заблочен - разблочить (ОТКЛ ПРИ _SELF_INIT)
            cursor_exec_edit("UPDATE allowed_users" + 
                f" SET is_blocked = false WHERE user_id = '{user_id}'")
            #db_info = add_user_to_database(name, user_id)
            info = f'State of user "{name}" changed to active' #user unblocked
        else:
            info = f'User "{name}" is already admitted'
    db_info = add_user_to_database(name, user_id) #row and table existing check anyway
    return info + '\n' + db_info

def self_autoinit_user(name: str, user_id: str):
    #то же, что и init_user, только разблочить себя нельзя
    pass

def add_user_to_database(name: str, user_id: str):
    info = ''
    #проверяем, есть ли строка в user_langs И есть ли таблица словарь
    if len(cursor_exec_select("SELECT * FROM langs_config "
            + f"WHERE user_id = '{user_id}'")) == 0: #если строчек нет
        create_langs_row(name, user_id)
        info += 'langs_config was created. '
    if len(cursor_exec_select("SELECT * FROM INFORMATION_SCHEMA.TABLES "
                 + "WHERE TABLE_SCHEMA = 'dictionaries'" 
                 + f"AND  TABLE_NAME = '_{user_id}'")) == 0:
        create_dict_table(user_id) #если нет таблички 
        info += 'dictionary was created. ' 
    if info == '': info += "dict and lang_config exist already" #если ни то, ни то не создавалось
    return info 

def create_langs_row(name: str, user_id: str):
    cursor_exec_edit("INSERT INTO langs_config VALUES" +
        f" ('{name}', '{user_id}', NULL, NULL)")

def create_dict_table(user_id: str): 
    #создаем именную табличку-словарь и строку в langs_config
    cv = 'character varying'
    cursor_exec_edit(f"CREATE TABLE dictionaries._{user_id} " + #может по имени обратиться?
        f"(user_name {cv}(50), language {cv}(10), word {cv}(50), native {cv}(10), " +
        f"translation {cv}(50), key {cv}(70), datetime {cv}(50), PRIMARY KEY (datetime))")

#----------------------конец команд инициализации------------------------

def block_user(name: Union[str, None], user_id: str):
    user_row: list = cursor_exec_select(
        f"SELECT * FROM allowed_users WHERE user_id = '{user_id}'")
    if len(user_row) == 1:
        name: str = user_row[0][0]
        #is_user_blocked: bool = user_row[2] если уже был заблокирован - молчим
        cursor_exec_edit("UPDATE allowed_users" + 
            f" SET is_blocked = true WHERE user_id = '{user_id}'")
        info = f'User "{name}" is not allowed more. Block is succsessfull'
    else: #if user_row == 0 (user_row = [])
        cursor_exec_edit("INSERT INTO allowed_users "
             + f" VALUES ('{name}', '{user_id}', true)")
        info = (f'New user "{name}" added in database ' + 
            'but is not allowed to use bot still')
    return info
