from _repeat_class import Repeat

#заменили global user_langs на аргумент get_langs_from_txt()
#это выглядит громоздко (можно передавать только нужную строку в кач-ве аргумента)

def get_langs_from_txt(): #прочесть словарь из файла (по имени ключу получить пару языков)
    file = "langs.txt"
    with open (file, 'rb') as F:
        user_langs = {}
        for line in F:
            line_dcd = line.decode('utf-8')
            line_dcd = line_dcd.replace('\n','')
            s = line_dcd.split(" -||- ")
            user_langs[s[0]] = [s[1], s[2]]
    return user_langs

def create_R_with_langs(name, user_langs):
    try: #если такого элемента еще нет, то создаем его, перехватывая keyError.
        ln = user_langs[name]
    except KeyError: #если юзер новенький - добавить строку
        user_langs[name] = ["none","none"]
        ln = user_langs[name]
    R = Repeat(ln[0],'none', ln[1],'none','none')
    return R

def update_langs(l_n, name, tag, user_langs):#апдейтим  словарь (и его файл)
    if tag.startswith(' '):
        tag = tag.replace(" ",'',1)
    print(tag)
    try:
        langs = user_langs[name] #pick dict element
    except KeyError: #если юзер новенький - добавить строку
        user_langs[name] = ["none","none"]
        langs = user_langs[name]
    if l_n == 'language':
        langs[0] = tag
    if l_n == 'native':
        langs[1] = tag
    user_langs[name] = langs #place changed dict element back
    with open('langs.txt','wb') as F:
        for key in user_langs: #ключи это юзернеймы
            s = (key + " -||- " + user_langs[key][0] +
                    " -||- " + user_langs[key][1] + "\n")
            bytes_str = s.encode('utf-8')
            F.write(bytes_str)
