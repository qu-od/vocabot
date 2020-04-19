import time
import discord
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
            print('DM_INPUT() key left "None"')
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
        #False mean that this is not a flip but a card creation
        short_time, key_for_dm = dm_format(self)
        if side == 'word':
            word_side_str = f"{self.language}: {self.word} --- {self.native}:" \
                f" ||{self.translation}||\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time}"
            embed = discord.Embed(type = 'rich', title = '__word side__', 
                    description = word_side_str,
                    colour = discord.Colour.blue())
        if side == 'translation':
            translation_side_str = f"{self.language}: ||{self.word}|| --- {self.native}:" \
                f" {self.translation}\nKey: ||{key_for_dm}||\n" \
                f"Created: {short_time}"
            embed = discord.Embed(type = 'rich', title = '__translation side__', 
                    description = translation_side_str,
                    colour = discord.Colour.dark_blue())
        if not (side in ['word','translation']):
            embed = discord.Embed(type = 'rich', title = '__**Error occured**__', 
                    description = 'wrong "side" argument',
                    colour = discord.Colour.red())
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
        key_for_dm = ' '
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

def read_from_txt(F, number: int):
    list_r = []
    for line in F:
        line = line.replace('\n','')
        line = line.replace('\r','')
        if line.startswith("---OBJECT---"):
            r = Repeat("none","none","none","none","none")
            s = line.split(" -||- ")
            r.language = s[1]
            r.word = s[2]
            r.native = s[3]
            r.translation = s[4]
        if line.startswith("KEY:"):
            s = line.split(" -||- ")
            r.key = s[1]
        if line.startswith("CREATED:"):
            s = line.split(" -||- ")
            r.datetime = s[1]
            list_r.append(r)
    cut_list_r = []
    if number >= 0:
        for i in range(number):
            try:
                cut_list_r.append(list_r[i])
            except IndexError:
                #ДАТЬ ОБРАТКУ О ТОМ, ЧТО NUMBER МАЛОВАТО
                break
    else:
        beginning = len(list_r) + number #минус на минус
        for i in range(beginning, len(list_r)):
            cut_list_r.append(list_r[i])
    return cut_list_r
