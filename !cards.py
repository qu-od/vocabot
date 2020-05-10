#LANGUAGES MODULE (здешние команды оставить без категории)
import discord
import time
import os
from typing import List, Union
from importlib import reload
from discord.ext import commands
from _language_edits import create_R_with_langs, update_langs
from _users_admission import create_dict_table
from _database import cursor_exec_select, cursor_exec_edit
import _repeat_class as rc
#import _embdict_class as ec
#from _users_admission import *  
#ds.AllowedMentions еще не ввели (ждем ds.py1.4)

#попросить отполировать английский
#брать отредактированный .txt-словарь обратно (формат должен быть строго соблюден)
#class for big_embed_dict_message? (настроить кнопки перелистывания и удаления)
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
        R = create_R_with_langs(ctx.author.id)
        #user_langs = lambda x: get_langs_from_txt()
        R.dm_input(argument)
        return R

#------------------------------COMMANDS LIST-------------------------

#эмодзи писать в карточки пока нельзя (из-за траблов с кодировкой)
@commands.command(name = 'n', help = ' [word].[translation].[key]' + 
'adds new word in your dictionary. Key is not nessesary')
async def create_word_pair(ctx, *, R: ConverterForR):
    R.append_to_db(str(ctx.author.id), ctx.author.name) #записываем в именную табличку
    await ctx.send(f'`New card {R.short_info()} has been created`')

@commands.command(name = 'del', help = 'deletes your last card from dictionary')
async def delete_recent_card(ctx):
    newest_R = rc.delete_last_card(str(ctx.author.id))
    await ctx.send(f'`Last card {newest_R.short_info()} has been deleted`')

@commands.command(name = 'language', 
            help = " [ID] Sets up language for words. Max length: 5 symbols")
async def set_language(ctx, *, language_tag: short_alpha_upper):
    if language_tag.startswith('error: '):
        await ctx.send(f'`{language_tag}`') #this is error message not a tag
        return 
    update_langs(ctx.author.id, language_tag, 'language')
    await ctx.send(f"`Foreign language has been changed to {language_tag}.`")

@commands.command(name = 'native', 
            help = " [ID] Sets up language for translations. Max length: 5 symbols")
async def set_native(ctx, *, native_tag: short_alpha_upper):
    if native_tag.startswith('error: '):
        await ctx.send(f'`{native_tag}`') #this is error message not a tag
        return
    update_langs(ctx.author.id, native_tag, 'native')
    await ctx.send(f"`Native language has been changed to {native_tag}.`") 

@commands.command(name = 'cards', 
    help = '[start] [end]. Sends cards from "start" to "end" in DMs.' + 
            'For getting single card drop out [end] argument. Length <= 5')
async def send_particular_cards(ctx, start: int, end: int = None):
    repeat_list = [] #чтобы при FileNotFoundError лист был определен для create_cards   
    if end == None: end = start #если один аргумент, значит это отдельная карточка
    repeat_list, info, slice_start, slice_end = rc.cards_from_dict_array(str(ctx.author.id), start, end)
    await create_cards(repeat_list, ctx)
    info = f'`{info}\ncards from #{slice_start} to #{slice_end} have sent in dm`'
    await ctx.send(info)

@commands.command(name = 'cards_day', #need more tests
    help = '[Mon.dd] sends cards created on that month and day.'
        + 'Example: "!v day_cards Apr.28". If empty, today date is implied. '
        + 'Warning: time is being saved in (UTC +0). '
        + 'So today really means present day in (UTC +0) timezone')
async def send_day_cards(ctx, date: mmdd_converter = None):
    if date == None: #внутри конвертера это не работает
        tl = time.asctime(time.gmtime()).split(' ')
        if tl[2] == '': #КОСТЫЛЬ
            tl = tl[:2] + tl[3:]
        date = [tl[4], tl[1], tl[2]] #это [год, месяц, день] в (UTC +0)
    repeat_list = [] #чтобы при FileNotFoundError лист был определен для create_cards 
    repeat_list, info = rc.cards_from_dict_day(str(ctx.author.id), date)
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
    repeat_list, info = rc.cards_from_dict_end(str(ctx.author.id), number)
    await create_cards(repeat_list, ctx) #либо в DMs либо в ctx.channel
    info = f'`{info}\n{what_end} {len(repeat_list)} cards have sent in dm`'
    await ctx.send(info)

#BEING CODED
@commands.command(name = 'dict', help = ' [page] sends list of words in dms')
async def send_embed_dict(ctx, page: int):
    repeat_list = rc.read_all_R_from_dict_table(str(ctx.author.id))
    ii = 10 * (page - 1) #index shift
    if ii > len(repeat_list):
        await ctx.send(f"`Too big page value." + 
            f"\nLength of your dictionary is {len(repeat_list)}." +
            f" It has {len(repeat_list)//10 + 1} pages`")
        return
    try:
        page_repeat_list = repeat_list[0 + ii: 10 + ii]
    except IndexError: #если не умещается
        page_repeat_list = repeat_list[ii:] #обрезать, чтобы уместилось
    dict_str = '\n'.join([f'#{repeat_list.index(R) + 1} {R.language}-{R.native} ' + 
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
    list_R = rc.read_all_R_from_dict_table(str(ctx.author.id))
    with open('temp_dict.txt', 'w') as F: 
        for R in list_R: #запись в файл
            R.append_to_txt(F)
    dict_file = discord.File('temp_dict.txt', filename = 'My card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)  
    os.remove("temp_dict.txt") #удаление этого файла

'''#BEING CODED
@commands.command(name = 'upload', 
        help = '[.txt file] with your edited dictionary in right format')
async def take_dict_back(ctx):
    pass'''

@commands.command(name = 'dict_full_deletion', #не удаляет активные карточки из БД
            help = ' Deletes your dictionary without backups')
async def clr_cards_request(ctx):
    await ctx.send("`Do you really want to delete all your cards?" + 
        "\nAnswer with !v confirm yes/no`")
    user_id = str(ctx.author.id)
    if is_id_in_deletion_pending(user_id) == False: #записываем id юзера, если еще не
        cursor_exec_edit("INSERT INTO cards_clr_pending VALUES "
            + f"('{ctx.author.name}', '{user_id}', '{time.asctime(time.gmtime())}')")

@commands.command(name = 'confirm', help = ' service command') 
#только пока нет когов, только для удаления
#потом прекращать ожидание ответа через некоторое время
#зачем я это пишу? все равно же временная и некрасивая команда
async def clr_cards(ctx, ans: bool):
    user_id = str(ctx.author.id)
    is_id_in_file = is_id_in_deletion_pending(str(ctx.author.id)) #bool flag
    if not is_id_in_file: #если звпроса не было, то пусть идет лесом
        await ctx.send("`Your confirmation is not essential`")
        return
    if ans is True: #dict deletion confirmed by user
        cursor_exec_edit(f"DELETE FROM cards_clr_pending WHERE user_id = '{user_id}'")
        #удалили айдишник из таблицы ожидания
        create_dict_table('b' + user_id) #бэкап перед удалением (table_name = b_123id321)
        cursor_exec_edit(f"DELETE FROM dictionaries._{user_id}") 
        #почистили таблицу, но не удалили
        await ctx.send("`Your data has been deleted. " +
                    "Though you'll never be able to check this`")
    elif ans is False: #dict deletion rejected by user
        cursor_exec_edit(f"DELETE FROM cards_clr_pending WHERE user_id = '{user_id}'")
        #удалили айдишник из таблицы ожидания
        await ctx.send("`Deletion failed sucсessfully`")
    #если bool converter не сработает (ни yes ни no), то выведеся BadArgumentError


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
        R.append_active_card(str(card_message.id), 
            ctx.author.name, str(ctx.author.id)) #лог id и R

def is_id_in_deletion_pending(user_id: str):
    is_id_in_file = False
    if len(cursor_exec_select("SELECT user_id FROM cards_clr_pending "
            + f"WHERE user_id = '{user_id}'")) == 1:
        is_id_in_file = True
    return is_id_in_file


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

'''def cards_imports_reload(): #для импорта в майн, нужно убрать ! из !cards.py
    reload(get_langs_from_txt)
    reload(rc.cards_from_dict_end)
    reload(rc.cards_from_dict_day)
    reload(rc.cards_from_dict_array)
    reload(rc.delete_last_card)
    reload(get_langs_from_txt)
    reload(create_R_with_langs)
    reload(update_langs)'''
