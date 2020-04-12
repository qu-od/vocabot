import time

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
        if s[2].startswith(" "):
            s[2] = s[2].replace(" ",'',1)
        print(s)
        self.word = s[0]
        self.translation = s[1]
        if s[2]: #ОТТЕСТИТЬ (если ключ будет пустой)
            self.key = s[2]
        self.datetime = time.asctime(time.gmtime())

    def dm_self_input(self,s): #weak split parameters :
        s = s.replace('|','') #deleting spoilers
        after_language = s.split(': ',1)[1]
        self.word = after_language.split(' --- ')[0]
        after_native = after_language.split(': ',1)[1]
        self.translation = after_native.split('\n')[0]
        after_key = after_native.split(': ',1)[1]
        self.key = after_key.split('\n')[0]
        after_time = after_key.split(': ',1)[1]
        self.datetime = after_time.split(' `',1)[0] #here is short time format 

        


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

    def dm_card(self, side):
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
            cut_list_r.append(list_r[i])
    else:
        beginning = len(list_r) + number #минус на минус
        for i in range(beginning, len(list_r)):
            cut_list_r.append(list_r[i])
    return cut_list_r

def dm_format(R): #общие костыли для удобного отображения разных форматов в ЛС
    short_time = R.datetime.split(' ')
    short_time = ' '.join(short_time[0:3])
    key_for_dm = R.key #чтобы спойлеры не выворачивались наизнанку 
    if R.key == '':
        key_for_dm = ' '
    return short_time, key_for_dm




