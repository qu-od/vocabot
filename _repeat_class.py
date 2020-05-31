import time
import discord
from typing import List, Union
from math import fabs, copysign
from _database import cursor_exec_select, cursor_exec_edit

''' язык, слово, перевод, комментарий, дата и время.
 в целом нужно будет native language выбрать. Часовой пояс знать не нужно,
 ведь для повторения важна лишь относительная разница между временем
 записи слова и временем н-ного повторения. '''
'''поставить деструктор'''
#лучше всего, если KEY это сильная ассоциация и/или контекст, в котором это
#слово встретилось будучи незнакомым
#юзерам придется избежать многоточий в середине (и знаков " -||- ")

class Repeat():
    
    def __init__(self, l, w, nl, t, k): #сделать эти аргументы необязательными
        self.language = l
        self.word = w
        self.native = nl
        self.translation = t
        self.key = k
        self.datetime = time.asctime(time.gmtime()) #UTC +0

    def info(self):
        s = f" {self.language}: {self.word} --- {self.native}:" \
                f" {self.translation}\n KEY: {self.key}\n" \
                f" CREATED: {self.datetime}\n"
        return s

    def short_info(self): #используется в ответах на !n и !del
        s = f'"{self.word}"-"{self.translation}"'
        return s
    
    def console_input(self):
        #s = "The Table. стол. то место, где едят" -  образец строки на входе
        s = input()
        s = s.split(".")
        #удаляем пробелы с переди строк-переменных (если они там стоят)
        if s[1].startswith(" "):
            s[1] = s[1].replace(" ",'',1)
        if s[2].startswith(" "):
            s[2] = s[2].replace(" ",'',1)
        print(s,"\n")
        self.word = s[0]
        self.translation = s[1]
        self.key = s[2]
        self.datetime = time.asctime(time.gmtime())

    def dm_input(self,s):
        s = s.split(".")
        #удаляем пробелы с переди строк-переменных (если они там стоят)
        #пробелы могут быть, из-за точек. После них юзеру хочется поставить пробел
        if s[1].startswith(" "):
            s[1] = s[1].replace(" ",'',1)
        print('dm_input:', s)
        self.word = s[0]
        self.translation = s[1]
        try:
            if s[2].startswith(" "):
                s[2] = s[2].replace(" ",'',1) 
            self.key = s[2]
        except IndexError:
            self.key = None
            print('DM_INPUT() key = None')
        self.datetime = time.asctime(time.gmtime())

    #ВОТ ТУТ NONE НУЖНО В NULL. ОДНОСТРОЧНЫМ ЗАПРОСОМ ЭТОГО НЕ СДЕЛАТЬ
    def append_to_db(self, user_id: str, user_name: str):
        #ЖИИРНЫЙ КОСТЫЫЫЛЬ, ПОКА НЕ ОСВОИЛИ sql.timestamp:
        #ПИШЕМ В СТОЛБЕЦ NAME ИНДЕКС ДЛЯ СОРТИРОВКИ ПО ВРЕМЕНИ СОЗДАНИЯ
        #ИНДЕКСЫ В ЭТОЙ КОЛОНКЕ НАДО СОХРАНИТЬ УНИКАЛЬНЫМИ
        lines = cursor_exec_select("SELECT user_name FROM " +
            f"dictionaries._{user_id} ORDER BY user_name") #ascending sort by default
        try: 
            last_index = int(lines[-1][0]) + 1 #первый элемент в последнем тьюпле листа lines
        except IndexError: #если словарь был пуст и строк не было
            print('МЯУ! СТРОК В СЛОВАРЕ НЕТУ! ЗАПИШУ СТРОКУ С ЕДИНИЧКОЙ')
            last_index = 1
        indx = str(last_index) if last_index >= 10 else '0' + str(last_index) #КОСТЫЛЬ В КОСТЫЛЕ
        cursor_exec_edit(f"INSERT INTO dictionaries._{user_id} VALUES "
            #+ f"('{user_name}', '{self.language}', '{self.word}', " #_СО ВРЕМЕНЕМ_ ВЕРНЕМ ЭТО
            + f"('{indx}', '{self.language}', '{self.word}', "
            + f"'{self.native}', '{self.translation}', '{self.key}', "
            + f"'{self.datetime}')")

    def append_to_txt(self, F):
        F.write(f"---OBJECT--- -||- {self.language} -||- {self.word} -||- " \
                f"{self.native} -||- {self.translation}\nKEY: -||- {self.key}\n" \
                f"CREATED: -||- {self.datetime}\n\n")

    def append_to_bytefile(self):
        pass

    def dm_info(self): #метод устарел
        short_time, key_for_dm = dm_format(self)
        s = f"{self.language}: {self.word} --- {self.native}:" \
                f" ||{self.translation}||\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time}"
        return s

    def dm_card(self, side): #устарел из за введения dm_embed_card()
        short_time, key_for_dm = dm_format(self)
        if side == 'word':
            s = f"{self.language}: {self.word} --- {self.native}:" \
                f" ||{self.translation}||\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time} `word side`"
        if side == 'translation':
            s = f"{self.language}: ||{self.word}|| --- {self.native}:" \
                f" {self.translation}\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time} `translation side`"
        if not (side in ['word','translation']):
            s = 'wrong "side" argument' 
        return s

    def dm_embed_card(self, side: str):
        short_time, key_for_dm = dm_format(self)
        if side == 'word':
            word_side_str = f"{self.language}: {self.word} --- {self.native}:" \
                f" ||{self.translation}||\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time}"
            embed = discord.Embed(type = 'rich', title = 'word side', 
                    description = word_side_str,
                    colour = discord.Colour.blue())
        if side == 'translation':
            translation_side_str = f"{self.language}: ||{self.word}|| --- {self.native}:" \
                f" {self.translation}\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time}"
            embed = discord.Embed(type = 'rich', title = 'translation side', 
                    description = translation_side_str,
                    colour = discord.Colour.dark_blue())
        return embed

    def append_active_card(self, msg_id: str, user_name: str, user_id: str):
        query = (f"INSERT INTO active_cards VALUES ('{msg_id}', '{user_name}', " +
        f"'{user_id}', '{self.language}', '{self.word}', '{self.native}', " +
        f"'{self.translation}', '{self.key}', '{self.datetime}')")
        cursor_exec_edit(query)
    
#-------------------------------End of class description----------------            

def fetch_active_card(msg_id: int):
    #check whether this message is an active card or not. If yes - read R
    #при отключении кэш сообщений пропадает и on reaction не работает
    lines = cursor_exec_select(f"SELECT * FROM active_cards WHERE msg_id = '{str(msg_id)}'")
    if len(lines) == 1: #если ответ есть
        R = Repeat(*lines[0][3:8]) #lines[0] - извлечение тьюпла из листа
        R.datetime = lines[0][8]
        return R
    return None #если цикл прошел и msg_id не найдено в файле

def cards_from_dict_array(user_id: str, raw_start: int, raw_end: int): #слить с предыд. функ?
    start, end, = raw_start, raw_end #raw_end от юзера ВКЛЮЧИТЕЛЬНО 
    list_R, slice_R =  [], [] 
    list_R.append(Repeat(None, None, None, None, None))#забили нулевой элемент, чтобы индексы начинались с 1
    list_R = list_R + read_all_R_from_dict_table(user_id) #сохраняем нулевой элемент
    info = 'Cards list has formed successfully' #по умолчанию все хорошо
    #indexes_R = range(0, len(list_R))
    if raw_end < raw_start: #если границы перепутаны, перевернем их
        raw_end, raw_start, end, start = raw_start, raw_end, raw_start, raw_end
    if raw_start < 1: #проверим нижнюю границу
        info = "start number is to small"
        start = 1
    if raw_end > len(list_R) - 1: #проверим верхнюю границу
        info = "end number is too big (isn't enough cards in your dictionary)"
        end = len(list_R) - 1
    if len(range(start, end)) > 5: #если все еще больше пяти
        info = "You've requested too much cards (more than 5)"
        end = start + 4
    index_list = range(start, end + 1) #чтобы включительно брать
    for i in index_list: #в общем случае тут могут быть ЛЮБЫЕ индексы
        slice_R.append(list_R[i])
    return slice_R, info, start, end

def cards_from_dict_day(user_id: str, date: List[str]): #удобно, если мало слов
    info = f'Cards created on {date[1]} the {date[2]} have sent in dm. '
    list_R = read_all_R_from_dict_table(user_id)
    #dated_R = [] 
    dated_R = list(filter(lambda R: is_requested_date(R, date), list_R))
    if len(dated_R) > 5: 
        dated_R = dated_R[:5] #максимум 5 карточек
        info += 'First 5 cards for this date sent in dm\nUse "dict" to see all at once'
    if len(dated_R) == 0:
        info = 'There are no cards for this date'
    return dated_R, info

def cards_from_dict_end(user_id: str, number: int): #, *, start = None, end = None):
    raw_number = number
    info = 'Cards has formed successfully' #по умолчанию все хорошо
    list_R = read_all_R_from_dict_table(user_id)
    cut_list_R = []
    if fabs(number) > 5:
        info = "Too much cards requested in one command (more than 5)"
        number = int(copysign(5, raw_number)) #знак сохраняем
    if fabs(number) > len(list_R): #если все еще больше длины словаря
        #если меньше десяти карточек в словаре
        info = "You don't have enough cards"
        number = int(copysign(len(list_R), raw_number)) #знак сохраняем
    if number > 0: #first {number} of words
        index_list = range(number)
    if number < 0: #last {number} of words
        index_list = range(len(list_R) + number, len(list_R))
    if raw_number == 0: #0 words requested. 
    #(number - what is requested, cut_nuber - number shortened to len(list_R) if should
        index_list = [] #цикл тогда пропустится
        info = "You just requested 0 words, don't you?"
    if len(list_R) == 0 and raw_number != 0: 
        #проcили больше 0, а словарь пуст
        index_list = []  
        info += '\nYour dictionary is empty. Trust me'
    print(f'INDEX_LIST {index_list}')
    for i in index_list:
        cut_list_R.append(list_R[i])
    return cut_list_R, info

def delete_last_card(user_id: str):
    newest_R = []
    #word is a key var in dict-tables
    list_R = read_all_R_from_dict_table(user_id) #ОНИ СОРТИРОВАНЫ _ПО ИНДЕКСУ_ 
    #_СО ВРЕМЕНЕМ_ ВЫБИРАТЬ ПОСЛЕДНЮЮ СТРОКУ СОРТИРОВКОЙ ПО СТОЛБЦУ ВРЕМЕНИ
    if len(list_R) > 0: #если вообще карточки в словаре есть. (если нет - ПОФИГУ)
        newest_R = list_R[-1]
        cursor_exec_edit(f"DELETE FROM dictionaries._{user_id} WHERE word = '{newest_R.word}'")
    else: #если в словаре пусто
        print('МЯУ! rc.delete_last_cards_upd : В СЛОВАРЕ ПУСТО')
    return newest_R #самая новая карточка (САМЫЙ БОЛЬШОЙ ИНДЕКС)

def read_all_R_from_dict_table(user_id: str):
    list_R: List[Repeat] = []
    lines = cursor_exec_select(f"SELECT * FROM dictionaries._{user_id} "
        + "ORDER BY user_name") #сорт по возрастанию индекса (ПОТОМ ВРЕМЕНИ)
    for line in lines: #итерация по листу тьюплов
        R = Repeat(*line[1:6])
        R.datetime = line[6] 
        list_R.append(R)
    return list_R

    #list_R = [] #оставим для истории
    #for line in F:
    #    line = line.replace('\n','')
    #    line = line.replace('\r','')
    #    if line.startswith("---OBJECT---"):
    #        R = Repeat("none","none","none","none","none")
    #        s = line.split(" -||- ")
    #        R.language = s[1]
    #        R.word = s[2]
    #        R.native = s[3]
    #        R.translation = s[4]
    #    if line.startswith("KEY:"):
    #        s = line.split(" -||- ")
    #        R.key = s[1]
    #    if line.startswith("CREATED:"):
    #        s = line.split(" -||- ")
    #        R.datetime = s[1]
    #        list_R.append(R) # добавление только после считывания времени

def dm_format(R): #общие костыли для удобного отображения разных форматов в ЛС
    short_time = R.datetime.split(' ')
    short_time = ' '.join(short_time[0:3])
    key_for_dm = R.key #чтобы спойлеры не выворачивались наизнанку 
    if R.key == '':
        key_for_dm = 'none'
    return short_time, key_for_dm

def is_requested_date(R: Repeat, date: List[str]):
    ans = False
    R_dttm_list = R.datetime.split(' ')
    if R_dttm_list[2] == '': #если месяц однозначный
        R_dttm_list = R_dttm_list[:2] + R_dttm_list[3:] #удаляем этот пустой элемент
    if (R_dttm_list[1] == date[1] and R_dttm_list[2] == date[2] 
        and R_dttm_list[4] == date[0]):
        ans = True
    return ans
    
    