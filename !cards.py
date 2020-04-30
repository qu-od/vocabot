#LANGUAGES MODULE (здешние команды оставить без категории)
import discord
import time
from typing import List, Union
from importlib import reload
from discord.ext import commands
from _language_edits import get_langs_from_txt, create_R_with_langs, update_langs
import _repeat_class as rc
#import _embdict_class as ec
#from _users_admission import *  
#ds.AllowedMentions еще не ввели (ждем ds.py1.4)

#команда-инициализация юзера
#попросить отполировать английский
#брать отредактированный .txt-словарь обратно (формат должен быть строго соблюден)
#class for big_embed_dict_message? (настроить кнопки перелистывания и удаления)
#вынести try: open dic.txt with: в отдельную функцию  (передать функцию выбора карточек в эту функцию?)
#explain prefix with space: "!v command@"


#---------------------------EVENTS AND CONVERTERS----------------------


#конвертеры должны быть прописаны раньше комманд (почему так?)
def mmdd_converter(date):
    month, day = date.split('.')
    month = month.capitalize()
    year = time.strftime('%Y')
    return year, month, day

def short_alpha_upper(argument): 
    print('to_upper converter worked')
    if len(argument) > 5:
        return 'error: too long id'
    #применить лямбду?
    for symbol in argument:
        if not symbol.isalpha():
            return 'error: non-alphabet symbol'
    return argument.upper()

def dict_end_converter(what_end):
    if not what_end in ['first', 'last']:
        what_end = 'wrong_argument' 
    print('dict_end_converter worked')
    return what_end

class ConverterForR(commands.Converter):
    async def convert(self, ctx, argument):
        user_langs = get_langs_from_txt()
        R = create_R_with_langs(ctx.author.name, user_langs)
        #user_langs = lambda x: get_langs_from_txt()
        R.dm_input(argument)
        return R

#------------------------------COMMANDS LIST-------------------------

#эмодзи писать в карточки пока нельзя (из-за траблов с кодировкой)
@commands.command(name = 'n', help = ' [word].[translation].[key]' + 
'adds new word in your dictionary. Key is not nessesarily')
async def create_word_pair(ctx, *, R: ConverterForR):
    file = R'_Dictionaries/of ' + ctx.author.name + '.txt'
    with open(file, 'a') as F:
        R.append_to_txt(F)
    await ctx.send(f'`New card {R.short_info()} has been created`')

@commands.command(name = 'del', help = 'deletes your last card from dictionary')
async def delete_recent_card(ctx):
    try: #MAKE TRY_DICT_FUNC
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F: 
            last_R = rc.delete_last_card(F, ctx.author.name)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    await ctx.send(f'`Last card {last_R.short_info()} has been deleted`')

@commands.command(name = 'language', 
            help = " [ID] Sets up language for words. Max length: 5 symbols")
async def set_language(ctx, *, language: short_alpha_upper):
    if language.startswith('error: '):
        await ctx.send(f'`{language}`') #this is error message not a language
        return 
    user_langs = get_langs_from_txt()
    update_langs('language', ctx.author.name, language, user_langs)
    await ctx.send(f"`Foreign language has been changed to {language}.`")

@commands.command(name = 'native', 
            help = " [ID] Sets up language for translations. Max length: 5 symbols")
async def set_native(ctx, *, native: short_alpha_upper):
    if native.startswith('error: '):
        await ctx.send(f'`{native}`')
        return
    user_langs = get_langs_from_txt()
    update_langs('native', ctx.author.name, native, user_langs)
    await ctx.send(f"`Native language has been changed to {native}.`") 

@commands.command(name = 'cards', 
    help = '[start] [end]. Sends cards from "start" to "end" in DMs.' + 
            'For getting single card drop out [end] argument. Length <= 5')
async def send_particular_cards(ctx, start: int, end: int = None):
    repeat_list = [] #чтобы при FileNotFoundError лист был определен для create_cards   
    if end == None: end = start #если один аргумент, значит это отдельная карточка
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F:
            repeat_list, info, slice_start, slice_end = rc.cards_from_dict_array(F, start, end)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    await create_cards(repeat_list, ctx)
    info = f'`{info}\ncards from #{slice_start} to #{slice_end} have sent in dm`'
    await ctx.send(info)

@commands.command(name = 'day_cards', #need more tests
    help = '[Mon.dd] sends cards created on that month and day.' + 
        'Example: "!v day_cards Apr 28". If empty, today date is implied')
async def send_day_cards(ctx, date: mmdd_converter = None):
    if date == None: #внутри конвертера это не работает
        month, day = time.asctime(time.gmtime()).split(' ')[1:3]
        date = [time.strftime('%Y'), month, day] #это массив года, месяца и дня в строгом формате
    repeat_list = [] #чтобы при FileNotFoundError лист был определен для create_cards 
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F:
            repeat_list, info = rc.cards_from_dict_day(F, date)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    await create_cards(repeat_list, ctx)
    await ctx.send(f'`{info}`')

@commands.command(name = 'cards_end',
        help = ' [n] [first/last] to get first/last n words in embed. n <= 5')
async def send_end_cards(ctx, number: int, what_end: dict_end_converter):
    if number < 0: #take negative number requests as usual ones
        number *= -1 
    if what_end == 'wrong_argument':
        await ctx.send('`Wrong first/last argument`')
        return
    if what_end == 'last':
        number *= -1
    repeat_list = [] #чтобы len(repeat_list) была = 0 если словаря нет 
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F:
            repeat_list, info = rc.cards_from_dict_end(F, number)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    await create_cards(repeat_list, ctx) #либо в DMs либо в ctx.channel
    info = f'`{info}\n{what_end} {len(repeat_list)} cards have sent in dm`'
    await ctx.send(info)

#BEING CODED
@commands.command(name = 'dict', help = ' [page] sends list of words in dms')
async def send_embed_dict(ctx, page: int):
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F:
            repeat_list = rc.read_all_R_from_dict(F)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    ii = 10 * (page - 1) #index shift
    if ii > len(repeat_list):
        await ctx.send(f"`Too big page value." + 
            f"\nLength of your dictionary is {len(repeat_list)}." +
            f"It has {len(repeat_list)//10 + 1} pages`")
        return
    try:
        page_repeat_list = repeat_list[0 + ii: 9 + ii]
    except IndexError: #если не умещается
        page_repeat_list = repeat_list[ii:]
    dict_str = '\n'.join([f'#{repeat_list.index(R)} {R.language}-{R.native}' + 
        f'{R.short_info()}' for R in page_repeat_list])
    #в генераторе асимптотика - квадрат.
    embed = discord.Embed(type = 'rich', title = f'page {page} of your dictionary', 
            description = dict_str, colour = discord.Colour.green())
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send(embed = embed)
    await ctx.send('`Dictionary has been sent in dms`')
    '''
    append_active_dict()
    await add_reaction #листать влево
    await add_reaction #листать вправо
    await add_reaction #удалить
    '''

@commands.command(name = 'dict_txt', help = ' sends your dictionary file into dms')
async def send_txt_dict(ctx): #вроде текст весит немного, поэтому ограничений не давать
    dict_file = discord.File(
            f'_Dictionaries/of {ctx.author.name}.txt', filename = 'My card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)  

'''#BEING CODED
@commands.command(name = 'upload', 
        help = '[.txt file] with your edited dictionary in right format')
async def take_dict_back(ctx):
    pass'''

@commands.command(name = 'clr_cards', 
            help = ' Deletes your dictionary without backups')
async def clr_cards_request(ctx):
    await ctx.send("`Do you really want to delete all your cards?" + 
    "\nAnswer with !v _confirm yes/no`")
    str_id = str(ctx.author.id)
    is_id_in_file, new_ids_list = is_id_in_deletion_pending(str_id) #bool flag
    if is_id_in_file == False: #если он не записан еще
        with open('pending_dict_deletion.txt', 'a') as F:
            F.write(str_id + '\n')

@commands.command(name = '_confirm', help = ' service command') 
#только пока нет когов, только для удаления
#потом прекращать ожидание ответа через некоторое время
#зачем я это пишу? все равно же временная и некрасивая команда
async def clr_cards(ctx, ans: bool):
    is_id_in_file, new_ids_list = is_id_in_deletion_pending(str(ctx.author.id)) #bool flag
    if not is_id_in_file: #если звпроса не было, то пусть идет лесом
        await ctx.send("`Your confirmation are not essential`")
        return
    if ans is True: #dict deletion confirmed by user
        update_deletion_pending(new_ids_list)
        with open('_Dictionaries/of ' + ctx.author.name + '.txt',"w") as F:
            F.write('') #чистка словаря
        await ctx.send("`Your data has been deleted. " +
                    "Though you'll never be able to check this`")
    elif ans is False: #dict deletion rejected by user
        update_deletion_pending(new_ids_list)
        await ctx.send("`Deletion failed sucсessfully`")
    #если bool converter не сработает (ни yes ни no), то выведеся BadArgumentError

'''
@commands.command(name = 'init_me', 
    help = 'forms request on bot using. Need some time to be processed')
#на тесте (бот приватный) разрешения давать вручную
#после того, как бот станет публичным, обслуживать юзеров с серверов-подписчиков
async def admission_request(ctx):
    pass'''

'''
@commands.command(name = '', help = '')
@commands.command(name = '', help = '')
'''    

#-----------------------FUNCS AND EXTENSION START UP-----------------------

async def create_cards(repeat_list: List[rc.Repeat], ctx): #анно. типов (пока для себя)
    for R in repeat_list: #для каждой карточке в выданном списке
        #await ctx.author.create_dm() #dictionary in DMs not in ctx.channel
        #card_message = await ctx.author.dm_channel.send(embed = R.dm_embed_card('word'))
        card_message = await ctx.send(embed = R.dm_embed_card('word')) #for public testing
        await card_message.add_reaction('🔁') #add reaction on card-message
        R.append_active_card(card_message.id) #лог id и R

def is_id_in_deletion_pending(user_id: str):
    is_id_in_file = False
    ids_list = []
    with open('pending_dict_deletion.txt', 'r') as F:
        for line in F:
            line = line.replace('\n','')
            line = line.replace('\r','')
            ids_list.append(line)
    if user_id in ids_list:
        is_id_in_file = True
        i = ids_list.index(user_id) #заявка на удаление была подана 
        new_ids_list = ids_list[:i] + ids_list[i+1:] #удаление ай||д||ишника
    else: new_ids_list = ids_list
    return is_id_in_file, new_ids_list
        
def update_deletion_pending(new_ids_list: list):
    with open('pending_dict_deletion.txt', 'w') as F:
        for Id in new_ids_list:
            F.write(Id + '\n')  

def setup(bot):
    bot.add_command(create_word_pair)
    bot.add_command(delete_recent_card)
    bot.add_command(set_language)
    bot.add_command(set_native)
    bot.add_command(send_particular_cards)
    bot.add_command(send_day_cards)
    bot.add_command(send_end_cards)
    bot.add_command(send_embed_dict)
    bot.add_command(send_txt_dict)
    #bot.add_command(take_dict_back)
    bot.add_command(clr_cards_request)
    bot.add_command(clr_cards)
    #bot.add_command(admission_request)

def cards_imports_reload(): #для импорта в майн, нужно убрать ! из !cards.py
    reload(get_langs_from_txt)
    reload(rc.cards_from_dict_end)
    reload(rc.cards_from_dict_day)
    reload(rc.cards_from_dict_array)
    reload(rc.delete_last_card)
    reload(get_langs_from_txt)
    reload(create_R_with_langs)
    reload(update_langs)
