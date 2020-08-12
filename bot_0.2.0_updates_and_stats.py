import os
import random
import discord
from importlib import reload
from discord.ext import commands
import _repeat_class as rc #так можно делать reload(rc)!
#from _repeat_class import Repeat, fetch_active_card
import _users_admission as ua
#from _users_admission import is_user_allowed, init_user
import _language_edits as le
import _database as db
import _readalong_class as rac
#from !cards import cards_imports_reload (! мешает импорту) 
#sql запросы написаны в одну строку (т. е. есть опасность sql-injection)

версия_бота = 'b'  #'b' for VocaBot 't' for VocaTest 
if версия_бота == 'b': TOKEN = os.getenv('VOCABOT_TOKEN') 
if версия_бота == 't': TOKEN = os.getenv('VOCATEST_TOKEN')
discord_error_handling = True
#False - все трейсбеки в консоли, True - не все ошибки, но будут в дискорде.
#деплоить с True, фигачить с False. Т. к. c True бот иногда падает молча. 

#BUG: карточки отваливаются через некоторое время (когда соединение прерывается)
#Попробовать восстанавливать активные карточки на on_ready(). Взяв эти сообщения в кэш снова

#BUG: второй раз словарь не удаляется (!cards_clr) 2 раза подряд, бэкап уже занят.
#нужно их нумеровать

#сделать команду для сброса логов на сервере
#сделать нормальные логи сообщений (см. SQL.type.test)
#поставить себе линию на 80-том столбце в VSC, чтоб не смотреть каждый раз на номер колонки
#datetime in active_cards (time instead of char_var). НУЖНО ДЛЯ СОРТИРОВКИ
#ПОКА-ЧТО В ЮЗЕР_НЕЙМ СТОЛБЕЦ СЛОВАРЕЙ БУДЕМ ПИСАТЬ ИНКРЕМЕНТ (ЦИФЕРКУ В ФОРМАТЕ СТРОКИ)
#сделать мощную статистику в !bookish.py
'''переделать все варианты None именно в NoneType, а не str. В бд это будет null. 
    Только надо переписать запросы вместе с %s'''
#проверку if len == 1 при запросах SELECT .. WHERE заменить на что-то более осмысленное
#добавить во все Dict.tables имя пользователя куда-то на видное место (коммент например)
#ПОЧИТАТЬ ПЕП (например про то, как переносить длинные строки)
#проверить все МУПУем
#написать FIND()
#help message customisation (embed, send in DM not in server)
#прочитать про декораторы https://habr.com/ru/post/141411/
#RENEGATTO COMPRENDO CHITAT' DMs
#категории комманд (и ивентов - listenerov?) (extentions & cogs)
#events тоже раскидать по файлам (логично, если реакции для bookish будут в bookish)
#проследить, как работает R после разбиения на @commands
#done with 0.1.3 --- next ver: bot 0.2.0 (sql database). Then 0.2.1 (pics sending)

#РефАкТоРитЬ (начиная с билт-ин методов и заканчивая новыми функциями, типами, [суб]классами)
#продумать систему бэкапов всех таблиц баз данных (автоматический уровень + ручной уровень)
#отправить картинку (чиатй FAQ почаще)
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
    if ua.is_user_allowed(my_member.name, my_member.id): #am I even allowed lol (just in case)
        await my_member.create_dm()
        await my_member.dm_channel.send("```скоро мама позовет```")
        print('start_dm_sent')
    else:
        print('that user is not allowed. Start dm was not send')
    смотрит = discord.ActivityType.watching #cyrillics test succ
    await bot.change_presence(activity = discord.Activity(type = смотрит, name = '!v help'))

@bot.event  #стенограмма
async def on_message(message): #saving of all dialogues
    log_message(message)
    await bot.process_commands(message) #эта функция разблокирует работу других комманд (смотри FAQ почаще)

@bot.check #global permission check
def user_permission_check(ctx): #applying permitted users list
    #print(f'author.name equals {name}') #почему этот принт срабатывает много раз после !vhelp?
    return ua.is_user_allowed(ctx.author.name, ctx.author.id) #возвращаем флаг для проверки

def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168 #my_id
    return commands.check(is_me_check)

if discord_error_handling:
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
            await ctx.send('```ExtensionFailed```')

@bot.event #делаем эмбед
async def on_reaction_add(reaction, user): #leads to card flip on 'translation' side 
    msg_id = reaction.message.id
    if user == bot.user: return #если бот не сам поставил эту реакцию
    if reaction.emoji != '🔁': return #если эмодзи именно это
    R = rc.fetch_active_card(msg_id) #ищем это сообщ в БД сообщений-карточек
    if R == None: return #значит он пустой и карточка не найдена
    await reaction.message.edit(embed = R.dm_embed_card('translation'))

@bot.event 
async def on_reaction_remove(reaction, user): #flips card_message on 'word' side again
    msg_id = reaction.message.id
    if user == bot.user: return
    if reaction.emoji != '🔁': return
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
        if log_channel: #если он задан
            print(log_channel)
            await log_channel.send('on_member_join worked')

@bot.event
async def on_member_remove(member):
    if is_bookish_member(member):
        log_channel = get_log_channel(member.guild)
        if log_channel: #если он задан
            print(log_channel)
            await log_channel.send('on_member_remove worked')

@bot.event
async def on_message_edit(before, after):
    if is_bookish_message(before) and not before.author.bot:
    #добавление ембеда == edit. так что нужна таблетка от самоответов
        log_channel = get_log_channel(before.guild)
        if log_channel: #если он задан
            embed = discord.Embed(title = '__**message edited**__', type = 'rich', 
                            description = f'`author:` {before.author}\n`msg`: {before.content}\n`edited:` {after.content}', 
                            colour = discord.Colour.dark_teal())
            await log_channel.send(embed = embed)

@bot.event
async def on_message_delete(message):
    if is_bookish_message(message) and message.author != bot.user:
    #тут таблетка ради удобства. А то сбщ от бота были неудаляемыми
        log_channel = get_log_channel(message.guild)
        if log_channel: #если он задан
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
    with open('pull_listdir.txt', 'wb') as F:
        for element in os.listdir():
            F.write((element + '\n').encode('utf-8'))
    file = discord.File('pull_listdir.txt')
    #await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = file)
    await ctx.author.dm_channel.send('`create_dm needed only once`')
'''dict_file = discord.File(
            f'_Dictionaries/of {cursedtea}.txt', filename = 'Tea card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)
    
    dict_file = discord.File(
            f'_Dictionaries/of {cursedtea}.txt', filename = 'Tea card collection.txt')
    await ctx.author.create_dm()
    await ctx.author.dm_channel.send('`Here is your dictionary file`', file = dict_file)'''

@commands.command(name = '_msg', help = 'staff only') #custom message. 
#to channels or users on the sever where command is invoked
@is_me()
async def custom_message(ctx, id_type: str, opt_id: int, *args): #слишком длинный инт для питона?
    #РАБОТАЕТ ЧЕРЕЗ РАЗ
    print(id_type, opt_id, args)
    message = ' '.join(args)
    if id_type == 'ch':
        await ctx.guild.get_channel(opt_id).send(message)
    elif id_type == 'dm':
        member = ctx.guild.get_member(opt_id)
        await member.create_dm()
        await member.dm_channel.send(message)
    else:
        await ctx.send('`Wrong id_type argument`')

@bot.command(name = '_init', 
    help = '[name] [id] for user initialization')
@is_me()
#на тесте (пока бот приватный) разрешения давать вручную
#после того, как бот станет публичным, обслуживать юзеров с серверов-подписчиков
async def admit_user(ctx, name: str, snowflake_id: str):
    info = ua.init_user(name, snowflake_id)
    await ctx.send(f'`{info}`')

@bot.command(name = '_block', help = '[id] [name: Optional]' + 
    'for blocking user with this id. Or just to log new user without admission')
@is_me() 
async def block_user(ctx, snowflake_id: str, name: str = None):
    info = ua.block_user(name, snowflake_id)
    await ctx.send(f'`{info}`')

@bot.command(name = '_status', help = 'staff only') #status update
@is_me() #в случае ошибки штатно срабатывает CheckFailure
async def status_setup(ctx, status_input: str_to_status, *args):
    game = discord.Game(' '.join(args))
    await ctx.bot.change_presence(status = status_input, activity = game)

@bot.command(name = '_update', help = 'staff only')
@is_me()
async def update_commands(ctx): #for updating commands during runtime
    try:
        ctx.bot.reload_extension('!bookish')
        ctx.bot.reload_extension('!pics')
        ctx.bot.reload_extension('!cards')
    except commands.ExtensionFailed: 
        await ctx.send('```Some error in command-extentions being reloaded```')
        return
    try: 
        reload(rc) #update _repeat_class module
        reload(le) #update _language_edits module
        reload(ua) #update _users_admission module
        reload(db) #update _database module
        reload(rc) #update _readalong_class module
        #reload(fetch_active_card) #как бы перезагружать функции из импорта а не модули..
        #!cards.cards_import_reload() #еще хотелось бы так обновить косвенные импорты 
        #восклицательный знак запрещает import !cards 
    except Exception:
        await ctx.send('```Some error in modules being reloaded```')
        return
    await ctx.send('```Extensions have been updated successfully```')

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
    r'''if type(message.channel) == discord.channel.TextChannel: 
    #не может создать файл в облаке
    #поэтому кттс перевести логи на таблички
        guild = message.guild
        dirs = os.listdir('_Server_msg_hisory')
        if (f'of {guild}' in dirs) == False:
            os.mkdir(Rf'_Server_msg_hisory\of {guild}')
        with open(fR'_Server_msg_hisory\of {guild}\{message.channel}.txt', 'ab') as F:
            if author == bot.user:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
            else:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))'''
    #еще есть типы каналов кроме DMChannel и TextChannel?

def get_log_channel(guild: discord.guild, logs_type: str = 'all') -> discord.TextChannel:
    if logs_type == 'all':
        lines = db.cursor_exec_select("SELECT * FROM log_channels WHERE "
            + f"server_id = '{guild.id}' AND logs_type = 'all'")
    if len(lines) == 1:
        channel_id = int(lines[0][2])
    elif len(lines) == 0: 
        print("log channel hasn't been chosen")
        return None #канал не задан
    elif len(lines) > 1: 
        print('МЯУ! неожиданный дубликат в базе данных')
        return None #ошибка 
    #elif purpose == <purpose_name> ... id возвратить по ключу (сервер id + logs_type) 
    #(напр: important_audit_logs, deletion_logs, welcome_bye_logs)
    return guild.get_channel(channel_id)

def create_folders():
    dirs = os.listdir()
    if ('_DMs_history' in dirs) == False:
        os.mkdir('_DMs_history')
    if ('_Server_msg_hisory' in dirs) == False:
        os.mkdir('_Server_msg_hisory')

#------------------------ВОТ PARAMETERS AND START UP----------------------------

bot.load_extension('!cards') #подключаем команды
bot.load_extension('!bookish')
bot.load_extension('!pics') 
create_folders() #создаем папки для логов, если их не было

bot.run(TOKEN)