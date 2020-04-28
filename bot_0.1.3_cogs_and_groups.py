import os
import random
import discord
from importlib import reload
#from dotenv import load_dotenv
from discord.ext import commands
import _repeat_class as rc #так можно делать reload(rc)!
#from _repeat_class import Repeat, fetch_active_card
from _users_admission import is_user_allowed
#from !cards import cards_imports_reload (! мешает импорту) 

#load_dotenv()
#TOKEN = os.getenv('VOCABOT_TOKEN') #unique bot token (must be secured)
with open('DANGER_NSFGITHUB.txt', 'r') as F:
    TOKEN = F.read()

#!native не создает новую строку для пользователя
#get_dirs_from_cloud - ошибка кодировки при записи файлов
#НАСТРАИВАЕМ БАЗЫ ДАННЫХ НА ХЕРОКУ (ЧТОБЫ СЛОВАРИ НЕ УДАЛЯЛИСЬ ПРИ ПЕРЕЗАПУСКЕ)
#service command: "delete bot messages"
#help message only in DM
#RENEGATTO COMPRENDO CHITAT' REVIEW
#прочитать "twelve-factor app"
#категории комманд (и ивентов - listenerov?) (extentions & cogs)
#events тоже раскидать по файлам (логично, если реакции для bookish будут в bookish)
#lambdas and decos
#user assigning via id
#message logging via "nonce"


#использовать "nonce" вместо "message/user.ID" при кэшировании в файлы 
#проследить, как работает R после разбиения на @commands
#ничего страшного, если в разных коммандах одинаково называть переменные F и file? 
#ВЫТАЩИТЬ ОШИБКИ РАСШИРЕНИЙ
#из хелпы убрать "staff only" команды
#done with 0.1.3 --- next ver: bot 0.1.4 (sql database). Then 0.2.4 (pics sending)

#свои эксепшены 
#РефАкТоРитЬ (начиная с билт-ин методов и заканчивая новыми функциями, типами, [суб]классами)
#продумать систему бэкапов логов_сообщений, словарей и langs (автоматический уровень + ручной уровень)
#отправить текстовый файл и картинку (чиатй FAQ почаще)
'''сделать защиту от спама (максимум - 120 действий за минуту, т. е. 6 чел - действие 3 секунды, 
24 чел - действие в 12 сек(!). Для начала слоумод = 1 сек пойдет. Нужен еще и явный счетчик ивентов на случай, 
если они вместе решат провести стресс-тест и (будут кликать каждую секунду) '''


GUILD = 673968890325237771 #server name (ПК)

bot_prefix = '!v ' #параметризовали префикс
bot = commands.Bot(command_prefix = bot_prefix)

@bot.event
async def on_ready(): #executes when connection made and data prepaired
    for guild in bot.guilds:
        if guild.id == GUILD:
            break
    print(f'{bot.user} is connected to  {guild.name} (id: {guild.id})')
    for member in guild.members: #finding my "member"
        if member.name == "Machine 🪐":
            my_member = member
    if is_user_allowed(my_member.name): #am I even allowed lol (just in case)
        await my_member.create_dm()
        await my_member.dm_channel.send("```ты нужен людям```")
        print('start_dm_sent')
    else:
        print('that user is not allowed. Start dm was not send')
    смотрит = discord.ActivityType.watching #cyrillics test
    await bot.change_presence(activity = discord.Activity(type = смотрит, name = '!v help'))

@bot.event  #стенограмма
async def on_message(message): #saving of all dialogues
    log_message(message)
    await bot.process_commands(message) #эта функция разблокирует работу других комманд (смотри FAQ почаще)

@bot.check #global permission check
def user_permission_check(ctx): #applying permitted users list
    name = ctx.author.name #потом сделать проверку по [user snowflake id] и не парится
    #и получать его из сообщения/процедуры инициализации
    #print(f'author.name equals {name}') #почему этот принт срабатывает много раз после !vhelp?
    return is_user_allowed(name) #возвращаем флаг для проверки

def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168 #my_id
    return commands.check(is_me_check)

@bot.event  #при отладке отключаем это, чтобы все ошибки шли в консоль а не терялись 
async def on_command_error(ctx, error):
    pass # если эта функция включена, ексепшоны не принтятся. во как
    if isinstance(error, commands.errors.CheckFailure): #обрабатываем ошибку отсутствия разрешения
        await ctx.send("```You don't have permission to use it```")
    if isinstance(error, commands.errors.CommandNotFound):  #обрабатываем ошибку "неправильная команда"
        cool_responses = ["Try something different", "you've entered wrong command",
                    "**English, mother#$^%*1!! Can you speak it?**","There is no that command",
                    "Wrong command", "This command haven't been added yet, unfortunately"]
        #await ctx.send(random.choice(cool_responses))
        await ctx.send(f'`{random.choice(cool_responses)}`')
    if isinstance(error, commands.UserInputError):
        await ctx.send('```UserInputError occured```')# base class for several next errors
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('```Not enough arguments for that command```')
    if isinstance(error, commands.TooManyArguments):
        await ctx.send("```You've entered too many arguments```")
    if isinstance(error, commands.BadArgument):
        await ctx.send('```Wrong argument```')
    if isinstance(error, commands.BadUnionArgument):
        await ctx.send('```Wrong union argument```')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send('```ArgumentParsingError occured```')
    if isinstance(error, commands.ExtensionFailed): #NE ROBIT см. "update" command
        await ctx.send('```ExtensionFailed ```')

@bot.event #делаем эмбед
async def on_reaction_add(reaction, user): #leads to card flip on 'translation' side 
    msg_id = reaction.message.id
    if user == bot.user: return
    R = rc.fetch_active_card(msg_id)
    if R == None: return #значит он пустой и карточка не найдена
    await reaction.message.edit(embed = R.dm_embed_card('translation'))

@bot.event 
async def on_reaction_remove(reaction, user): #flips card_message on 'word' side again
    msg_id = reaction.message.id
    if user == bot.user: return
    R = rc.fetch_active_card(msg_id)
    if R == None: return #значит он пустой и карточка не найдена
    await reaction.message.edit(embed = R.dm_embed_card('word'))


#------------------группа ивентов для книжного---------------------
 
def is_bookish_message(message): #func for sprcific guild check. id is for ПК server
    if isinstance(message.channel, discord.TextChannel): 
        return message.guild.id == 673968890325237771
    else:
        return False

def is_bookish_member(member): return member.guild.id == 673968890325237771

@bot.event
async def on_member_join(member):
    if is_bookish_member(member):
        log_channel = get_log_channel(member.guild)#или (member.guild, 'general_logs')
        print(log_channel)
        await log_channel.send('on_member_join worked')

@bot.event
async def on_member_remove(member):
    if is_bookish_member(member):
        log_channel = get_log_channel(member.guild)
        print(log_channel)
        await log_channel.send('on_member_remove worked')

@bot.event
async def on_message_edit(before, after):
    if is_bookish_message(before) and before.author != bot.user:
    #добавление ембеда == edit. так что нужна таблетка от самоответов
        log_channel = get_log_channel(before.guild)
        embed = discord.Embed(title = '__**message edited**__', type = 'rich', 
                        description = f'`author:` {before.author}\n`msg`: {before.content}\n`edited:` {after.content}', 
                        colour = discord.Colour.dark_teal())
        await log_channel.send(embed = embed)

@bot.event
async def on_message_delete(message):
    if is_bookish_message(message) and message.author != bot.user:
    #тут таблетка ради удобства. А то сбщ от бота были неудаляемыми
        log_channel = get_log_channel(message.guild)
        embed = discord.Embed(title = '__**message deleted**__', type = 'rich', 
                        description = f'`author:` {message.author}\n`msg`: {message.content}',
                        colour = discord.Colour.gold())
        await log_channel.send(embed = embed)

def str_to_status(argument):
    if (argument in ('dnd','do_not_disturb', 'otsosi')):
        status = discord.Status.dnd
    elif (argument in ('idle','sleep', 'не активен', 'афк')):
        status = discord.Status.idle
    else: status = discord.Status.online
    return status

#-----------------------------------COMMANDS-------------------------------

@bot.command(name = '_custom', help = 'staff only') #можно сюда пихать любую временную команду
@is_me()
async def getdirs(ctx): #посмотрим файлы в облаке
    print('1')
    with open('pull_listdir.txt', 'wb') as F:
        for element in os.listdir():
            F.write((element + '\n').encode('utf-8'))
    print('2')
    file = discord.File('pull_listdir.txt')
    #await ctx.author.create_dm()
    print('3')
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = file)
    await ctx.author.dm_channel.send('`create_dm needed only once`')
    print('4')
'''dict_file = discord.File(
            f'_Dictionaries/of {cursedtea}.txt', filename = 'Tea card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)
    
    dict_file = discord.File(
            f'_Dictionaries/of {cursedtea}.txt', filename = 'Tea card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)'''

@bot.command(name = '_status', help = 'staff only') #status update
@is_me() #в случае ошибки штатно срабатывает CheckFailure
async def status_setup(ctx, status_input: str_to_status, *args):
    game = discord.Game(' '.join(args))
    await ctx.bot.change_presence(status = status_input, activity = game)

@bot.command(name = '_update', help = 'staff only')
@is_me()
async def update_commands(ctx): #for updating commands during runtime
    #try:
    ctx.bot.reload_extension('!bookish')
    #except: 
    ctx.bot.reload_extension('!pics')
    ctx.bot.reload_extension('!cards')
    reload(rc)
    #reload(Repeat) #как бы перезагрузить сразу все..
    #reload(fetch_active_card)
    #reload(is_user_allowed) 
    #cards_import_reload() #еще можно так обновить косвенные импорты 
    await ctx.send('```Extensions have been updated```')

#--------------------------LIST OF FUNCTIONS---------------------------- 

def log_message(message): #вынесли сюда функцию ведения стенограммы целиком
    time = message.created_at 
    author = message.author
    #print(f'--- message from {author} --- ')
    print(f'--- message from {author} --- in {message.channel}\n{message.content}\n')
    if type(message.channel) == discord.channel.DMChannel: 
        name = message.channel.recipient.name #имя собеседника DM-канала
        with open(fR'_DMs_history\of {name}.txt', 'ab') as F:
            if author == bot.user:
                F.write(f'{bot.user.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
            else: #проблемы с битой кириллицей разрешились после удаления старого файла
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
    if type(message.channel) == discord.channel.TextChannel:
        guild = message.guild
        dirs = os.listdir('_Server_msg_hisory')
        if (f'of {guild}' in dirs) == False:
            os.mkdir(Rf'_Server_msg_hisory\of {guild}')
        with open(fR'_Server_msg_hisory\of {guild}\{message.channel}.txt', 'ab') as F:
            if author == bot.user:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
            else:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
    #еще есть типы каналов кроме DMChannel и TextChannel?

def get_log_channel(guild: discord.guild, logs_type: str = 'general_logs') -> discord.TextChannel:
    if logs_type == 'general_logs':
        with open('log_channel_ids.txt', 'r') as F:
            channel_id = int(F.readline())
    #elif purpose == <purpose_name> ... id возвратить по ключу (сервер id + logs_type) 
    #(напр: important_audit_logs, deletion_logs, welcome_bye_logs)
    return guild.get_channel(channel_id)

def create_folders():
    dirs = os.listdir()
    if ('_Dictionaries' in dirs) == False:
        os.mkdir('_Dictionaries')
    if ('_DMs_history' in dirs) == False:
        os.mkdir('_DMs_history')
    if ('_Server_msg_hisory' in dirs) == False:
        os.mkdir('_Server_msg_hisory')

def clear_cache(): #удаляем содержимое файлов (по сути - подготовка глобальных переменных)
    with open('active_cards.txt', 'w') as F:
        F.write('') 
    with open('pending_dict_deletion.txt', 'w') as F:
        F.write('')

#------------------------ВОТ PARAMETERS AND START UP----------------------------

bot.load_extension('!cards') #подключаем команды
bot.load_extension('!bookish')
bot.load_extension('!pics') 
create_folders() #создаем папки для логов, если их не было
clear_cache() #чистка кэша карточек чтобы не обманываться 
#на счет соответствия настоящего кэша и списка id.
#ЧСХ при вызове !clr_cards эту функ. не вызываем
#а значит карточки из кэша не пропадают до перезапуска бота 

bot.run(TOKEN)