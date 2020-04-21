#LANGUAGES MODULE (здешние команды оставить без категории)
import discord
from importlib import reload
from discord.ext import commands
from _repeat_class import Repeat, cards_from_dict_end, cards_from_dict_array, delete_last_card
from _language_edits import get_langs_from_txt, create_R_with_langs, update_langs
#from _users_admission import *  
#ds.AllowedMentions еще не ввели (ждем ds.py1.4)

#запрос большого эмбед-словаря (с нумерацией по месту)
#позволять запрашивать наборы карточек по интервалу номеров (не больше 10 опять же)
#карточки за сегоднящний день ()
#обработать ошибки в последних трех

#explain prefix with space: "!v command@"
#(для продвинутых) возможность отдавать .txt-словарь на редактирование и брать его обратно
#public test - VocaBot 0.2.0


#---------------------------EVENTS AND CONVERTERS----------------------

#конвертеры должны быть прописаны раньше комманд (почему так?)
def dict_end_converter(what_end):
    if not what_end in ['first', 'last']:
        what_end = 'wrong_argument' 
    print('dict_end_converter worked')
    return what_end

def short_alpha_upper(argument): 
    print('to_upper converter worked')
    if len(argument) > 5:
        return 'error: too long id'
    #применить лямбду?
    for symbol in argument:
        if not symbol.isalpha():
            return 'error: non-alphabet symbol'
    return argument.upper()

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
        help = ' [n] [first/last] to get first/last n words in embed. n <= 10')
async def get_some_embed_cards(ctx, number: int, what_end: dict_end_converter):
    if number < 0: #against "cards -3 last"
        number *= -1 
    if what_end == 'wrong_argument':
        await ctx.send('`Wrong first/last argument`')
        return
    repeat_list = [] #чтобы len(repeat_list) была=0 если словаря нет 
    if what_end == 'last':
        number *= -1
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F: #причесать пробелы в string.input()
            repeat_list, info = cards_from_dict_end(F, number)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    for R in repeat_list: #для каждой карточке в выданном списке
        #await ctx.author.create_dm() #dictionary in DMs not in ctx.channel
        #card_message = await ctx.author.dm_channel.send(embed = R.dm_embed_card('word'))
        card_message = await ctx.send(embed = R.dm_embed_card('word')) #for public testing
        await card_message.add_reaction('🔁') #add reaction on card-message
        R.append_active_card(card_message.id) #лог id и R
    info = f'`{info}\n{what_end} {len(repeat_list)} cards have sent in dm`'
    await ctx.send(info)     

@commands.command(name = 'dict_txt', help = ' sends your dictionary file into dms')
async def send_txt_dict(ctx): #вроде текст весит немного, поэтому ограничений не давать
    dict_file = discord.File(
            f'_Dictionaries/of {ctx.author.name}.txt', filename = 'My card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)

#BEING CODED
@commands.command(name = 'embed_list', help = ' sends list of words in dms')
async def send_embed_dict(ctx):
    await ctx.send(ctx.message.content,
            tts = True, nonce = 282, delete_after = 30.5)

#BEING CODED
@commands.command(name = 'cards_interval', help = '') #КОНВЕРТЕР int > 0 c ОШИБКОЙ
async def get_particular_embed_cards(ctx, start: int, end: int):
    with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F: #причесать пробелы в string.input()
        repeat_list, info = cards_from_dict_array(F, start, end)
    
    pass

#BEING CODED
@commands.command(name = 'today_cards', help = 'sends your todays cards in DM')
async def get_today_cards(ctx):
    pass

'''
@commands.command(name = '', help = '')
@commands.command(name = '', help = '')
'''

@commands.command(name = 'del', help = 'deletes your last card from dictionary')
async def delete_recent_card(ctx):
    try: #MAKE TRY_DICT_FUNC
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F: 
            last_R = delete_last_card(F, ctx.author.name)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    await ctx.send(f'`Last card {last_R.short_info()} has been deleted`')

@commands.command(name = 'clr_cards', 
            help = ' Deletes your dictionary without backups')
async def clear_cards_request(ctx):
    await ctx.send("`Do you really want to delete all your cards?" + 
    "\nAnswer with !v confirm yes/no`")
    str_id = str(ctx.author.id)
    is_id_in_file, new_ids_list = is_id_in_deletion_pending(str_id) #bool flag
    if is_id_in_file == False: #если он не записан еще
        with open('pending_dict_deletion.txt', 'a') as F:
            F.write(str_id + '\n')

@commands.command(name = 'confirm', help = ' service command') 
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
        
#-----------------------FUNCS AND EXTENSION START UP-----------------------

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
    bot.add_command(set_language)
    bot.add_command(set_native)
    bot.add_command(get_some_embed_cards)
    bot.add_command(clear_cards_request)
    bot.add_command(clr_cards)
    bot.add_command(delete_recent_card)
    bot.add_command(send_txt_dict)
    bot.add_command(send_embed_dict)
    bot.add_command(get_particular_embed_cards)
    bot.add_command(get_today_cards)

def cards_imports_reload(): #для импорта в майн, нужно убрать ! из !cards.py
    reload(get_langs_from_txt)
    reload(cards_from_dict_end)
    reload(cards_from_dict_array)
    reload(delete_last_card)
    reload(get_langs_from_txt)
    reload(create_R_with_langs)
    reload(update_langs)
