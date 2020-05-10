from _repeat_class import Repeat
from _database import cursor_exec_select, cursor_exec_edit
  

def create_R_with_langs(user_id: str):
    #прочтем словарь из таблички (по имени ключу получить пару языков
    lines = cursor_exec_select(f"SELECT * FROM langs_config WHERE user_id = '{user_id}'")
    #запись в бд должна быть, ведь юзер вызвал команду, значит он инициализирован
    #поэтому проверку if len(lines) == 0: не делаем. Ловим баги 
    language, native = lines[0][2], lines[0][3] #language, native: str
    return Repeat(language, None, native, None, None)

def update_langs(user_id: str, tag: str, l_or_n: str):
    #if tag.startswith(' '):
    #    tag = tag.replace(" ",'',1) #ВОЗМОЖНА ОШИБКА ПРИ ПЕРЕВОРОТЕ КАРТОЧКИ
    print(tag) 
    if l_or_n == 'language': #update foreign language tag in db (for words)
        cursor_exec_edit(f"UPDATE langs_config SET language = '{tag}' " +
            f"WHERE user_id = '{user_id}'")
    elif l_or_n == 'native': #update native language tag in db (for translations)
        cursor_exec_edit(f"UPDATE langs_config SET native = '{tag}' " +
            f"WHERE user_id = '{user_id}'") 