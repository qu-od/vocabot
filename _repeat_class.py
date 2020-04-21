import time
import discord
from math import fabs, copysign

''' язык, слово, перевод, комментарий, дата и время.
 в целом нужно будет native language выбрать. Часовой пояс знать не нужно,
 ведь для повторения важна лишь относительная разница между временем
 записи слова и временем н-ного повторения. '''
'''поставить деструктор'''
#лучше всего, если KEY это сильная ассоциация и/или контекст, в котором это
#слово встретилось будучи незнакомым
#юзерам придется избежать многоточий в середине (и знаков " -||- ")

class Repeat():
    
    def __init__(self, l, w, nl, t, k):
        self.language = l
        self.word = w
        self.native = nl
        self.translation = t
        self.key = k
        self.datetime = time.asctime(time.gmtime())
        
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
            self.key = 'none'
            print('DM_INPUT() key left "none"')
        self.datetime = time.asctime(time.gmtime())

    def append_to_txt(self,F):
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

    def append_active_card(self, msg_id: int):
        with open('active_cards.txt', 'a') as F: #log card and R inatance in one line
            s = (f'{str(msg_id)} -||- {self.language} -||- {self.word} -||- ' +
                f'{self.native} -||- {self.translation} -||- {self.key} -||- {self.datetime}\n')
            F.write(s)

def dm_format(R): #общие костыли для удобного отображения разных форматов в ЛС
    short_time = R.datetime.split(' ')
    short_time = ' '.join(short_time[0:3])
    key_for_dm = R.key #чтобы спойлеры не выворачивались наизнанку 
    if R.key == '':
        key_for_dm = 'none'
    return short_time, key_for_dm

def fetch_active_card(msg_id: int):
    #check whether this message is an active card or not. If yes - read R
    #при отключении кэш сообщений пропадает и on reaction не работает
        with open('active_cards.txt', 'r') as F: 
            for line in F:
                line = line.replace('\r','')
                line = line.replace('\n','')
                if line.split(' -||- ', 1)[0] == str(msg_id):
                    s = line.split(' -||- ')
                    R = Repeat(s[1], s[2], s[3], s[4], s[5])
                    R.datetime = s[6]
                    return R
        return None #если цикл прошел и msg_id не найдено в файле

def cards_from_dict_end(F, number: int): #, *, start = None, end = None):
    raw_number = number
    info = 'cards formed successfully' #по умолчанию все хорошо
    list_R = read_all_R_from_dict(F)
    cut_list_R = []
    if fabs(number) > 10:
        info = "Too much cards requested"
        number = int(copysign(10, raw_number)) #знак сохраняем
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

def cards_from_dict_array(F, start: int, end: int): #слить с предыд. функ?
    list_R = []
    slice_R = []
    info = 'Cards read successfully'
    if len(range(start, end)) > 10:
        print('test')
        #попросить ввести интервал поменьше
    return slice_R, info

def delete_last_card(F, user_name: str):
    list_R = read_all_R_from_dict(F)
    if len(list_R) > 0: #если вообще карточки в словаре есть. (если нет - ПОФИГУ)
        new_list_R = list_R[:-1] #удаление последнего элемента
        F.close() #вроде работает без этой строки, но оставлю ее
        with open('_Dictionaries/of ' + user_name + '.txt','w') as F_rewrite: 
            for R in new_list_R:
                R.append_to_txt(F_rewrite)
    return list_R[-1]
    

def read_all_R_from_dict(F):
    list_R = []
    #достаточно ли слов в словаре для запроса или нет. Или словарь пуст
    for line in F:
        line = line.replace('\n','')
        line = line.replace('\r','')
        if line.startswith("---OBJECT---"):
            R = Repeat("none","none","none","none","none")
            s = line.split(" -||- ")
            R.language = s[1]
            R.word = s[2]
            R.native = s[3]
            R.translation = s[4]
        if line.startswith("KEY:"):
            s = line.split(" -||- ")
            R.key = s[1]
        if line.startswith("CREATED:"):
            s = line.split(" -||- ")
            R.datetime = s[1]
            list_R.append(R) # добавление только после считывания времени
    return list_R
