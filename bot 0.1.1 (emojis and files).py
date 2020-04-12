import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from _repeat_class import *
from _language_edits import *
from _users_admission import *
from cmds_for_import import *

#converters (whitelist of words and commands for arguments) and proper exceptions
#простой экстеншон, чтобы не перезапускать бота во время его написания (вынести все команды в импорт)
#decos, lambdas and elif
#категории комманд
#продумать систему бэкапов логов_сообщений, словарей и langs (автоматический уровень + ручной уровень)

#отправить текстовый файл и картинку (чиатй FAQ почаще)
#использовать эмбед для карточек (вместо спойлера - черный квадратик)
'''сделать защиту от спама (максимум - 120 действий за минуту, т. е. 6 чел - действие 3 секунды, 
24 чел - действие в 12 сек(!). Для начала слоумод = 1 сек пойдет. Нужен еще и явный счетчик ивентов на случай, 
если они вместе решат провести стресс-тест и (будут кликать каждую секунду) '''
#extensions & cogs (для того, чтобы удобно классифицировать команды и подключать их через импорты)

#не во всех карточках отображается дата (число месяца) создания
#проследить, как работает R после разбиения на @commands
#ничего страшного, если в разных коммандах одинаково называть переменные F и file? 

load_dotenv()
TOKEN = os.getenv('VOCABOT_TOKEN') #unique bot token (must be secured)
GUILD = 'Первый книжный' #server name

bot_prefix = '!v ' #параметризовали префикс
bot = commands.Bot(command_prefix = bot_prefix)

@bot.event
async def on_ready(): #executes when connection made and data prepaired
    #print(f'{bot.user} has been connected to discord') #'user' = 'name' + 'id'
    for guild in bot.guilds:
        if guild.name == GUILD:
            break
    print(f'{bot.user} is connected to  {guild.name} (id: {guild.id})')
    members_string = ''
    for member in guild.members:
        members_string += (member.name + "---")
    #print(members_string)
    for member in guild.members: #finding my "member"
        if member.name == "Machine 🪐":
            my_member = member
    #print(my_member.name)
    if is_user_allowed(my_member.name): #am I even allowed lol (just in case)
        print('that user is allowed')
        await my_member.create_dm()
        await my_member.dm_channel.send("```У меня очень хорошее настроение```")
        print('start_dm_sent')
    else:
        print('that user is not allowed. Start dm was not send')

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

@bot.event 
async def on_command_error(ctx, error):
    pass # если эта функция включена, ексепшоны не принтятся. во как
    if isinstance(error, commands.errors.CheckFailure): #обрабатываем ошибку отсутствия разрешения
        await ctx.send('```You do not have permission to use bot.```')
    if isinstance(error, commands.errors.CommandNotFound):  #обрабатываем ошибку "неправильная команда"
        cool_responses = ["Try something different", "you've entered wrong command"
                    "**English, mother#$^%*1!! Can you speak it?**","There is no that command",
                    "Wrong command", "This command haven't been added yet, unfortunately"]
        #await ctx.send(random.choice(cool_responses))
        await ctx.send(f'`{random.choice(cool_responses)}`')
    if isinstance(error, commands.UserInputError):
        await ctx.send('```UserInputError worked```')# base class for several next errors
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('```MissingRequiredArgument worked```')
    if isinstance(error, commands.TooManyArguments):
        await ctx.send('```TooManyArguments worked```')
    if isinstance(error, commands.BadArgument):
        await ctx.send('```BadArgument worked```')
    if isinstance(error, commands.BadUnionArgument):
        await ctx.send('```BadUnionArgument worked```')
    if isinstance(error, commands.ArgumentParsingError):
        await ctx.send('```ArgumentParsingError worked```')

@bot.event 
async def on_reaction_add(reaction, user): #leads to card flip on 'translation' side 
    if user == bot.user:
        return
    if not is_active_card(reaction.message.id):
        return
    user_langs = get_langs_from_txt()
    R = create_R_with_langs(user.name, user_langs)
    R.dm_self_input(reaction.message.content)
    await reaction.message.edit(content = R.dm_card('translation'))

@bot.event 
async def on_reaction_remove(reaction, user): #flips card_message on 'word' side again
    if user == bot.user:
        return
    if not is_active_card(reaction.message.id):
        return
    user_langs = get_langs_from_txt()
    R = create_R_with_langs(user.name, user_langs)
    R.dm_self_input(reaction.message.content)
    await reaction.message.edit(content = R.dm_card('word'))

'''@bot.event
async def on_voice_call_or_smth(): #отслеживать войсы (кто сколько и с кем сидел)
'''

#конвертеры должны быть прописаны раньше комманд (почему так?)
def scream_case(argument): #converter example 
    print('to_upper converter worked')
    return argument.upper()

class ConverterForR(commands.Converter): #устроить тут лямбду
    async def convert(self, ctx, argument):
        name = ctx.author.name
        user_langs = get_langs_from_txt()
        R = create_R_with_langs(name, user_langs)
        R.dm_input(argument)
        return R

#-----------------------------------BEGINNING OF COMMANDS-------------------------------

@bot.command(name = 'n', help = '[word].[translation].[key] adds new word in your dictionary')
async def create_word_pair(ctx, *, R: ConverterForR):
    file = R'_Dictionaries/of ' + ctx.author.name + '.txt'
    with open(file, 'a') as F:
        R.append_to_txt(F)
    await ctx.send('`New word pair has been created`')

@bot.command(name = 'language', 
            help = "[ID] Sets up language for words")
async def set_language(ctx, *, language: scream_case):
    print(language)
    user_langs = get_langs_from_txt()
    update_langs('language', ctx.author.name, language, user_langs)
    await ctx.send(f"```Foreign language has been changed to {language}.```")

@bot.command(name = 'native', 
            help = "[ID] Sets up language for translations")
async def set_native(ctx, *, native: scream_case):
    user_langs = get_langs_from_txt()
    update_langs('native', ctx.author.name, native, user_langs)
    await ctx.send(f"```Native language has been changed to {native}.```") 

@bot.command(name = 'cards', 
            help = '[n] [first/last] to get first/last n words from your dictionary') 
async def get_some_cards(ctx, n: int, what_end: str):
    number = n #number = int(n) 
    if what_end == 'last': #нужен ли такой искусственный путь?
        number *= -1
    with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F_dm: #причесать пробелы в string.input()
        repeat_list = read_from_txt(F_dm, number)
    for R in repeat_list:
        await ctx.author.create_dm() #нужно ли это?
        card_message = await ctx.author.dm_channel.send(R.dm_card('word'))
        #await ctx.author.dm_channel.send(R.dm_card('word'))
        await card_message.add_reaction('🔁') #add reaction on card-message
        with open('active_cards.txt', 'a') as F:
            F.write(str(card_message.id) + '\n')
    response = f'{what_end} {n} words from your dictionary have been sent into your DMs'
    if len(repeat_list) == 0: #NEED TESTING
        response = 'Your file is empty. _Trust me_'
    await ctx.send(response)      

#СДЕЛАТЬ ГРУППУ КОМАНД ДЛЯ ПОЛУЧЕНИЯ КАРТОЧЕК
'''@bot.command(name = 'all_cards', help = 'sends all cards in DM')
@bot.command(name = 'today_cards', help = 'sends your today's cards in DM')
@bot.command(name = 'delete_last', help = 'deletes your last card from dictionary')
@bot.command(name = '', help = '')
@bot.command(name = '', help = '')
'''
@bot.command(name = 'clr_cards', 
            help = 'Deletes your dictionary without backups')
async def clear_dictionary(ctx):
    with open('_' + ctx.author.name + '.txt',"w") as F_clr:
        F_clr.write('')
    await ctx.send(" Your data has been deleted. " +
     "Though you'll never be able to check this")
     #сделать подтверждение (are you sure)

@bot.command(name = 'update', help = 'staff only')
@is_me
async def update_commands(ctx):
    await ctx.send('upd_cmd worked')

#--------------------------END OF COMMANDS. BEGINNING OF THE LIST OF FUNCTIONS--------------------

@commands.command() #сначала подключаем команды тут, потом из импорта(ов)
async def addition_command(ctx):
    await ctx.send('command was added via the extention')

def toggle_commands(bot):
    bot.add_command(addition_command)

def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168
    return commands.is_me_check(predicate)

def log_message(message): #вынесли сюда функцию ведения стенограммы целиком
    time = message.created_at 
    author = message.author
    print(f'--- message from {author} ---')
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

def is_active_card(msg_id: int): #check whether this message is an active card or not
#при отключении кэш сообщений пропадает и on reaction не работает
    ans = False 
    with open('active_cards.txt', 'r') as F:
        for line in F:
            line = line.replace('\r','')
            line = line.replace('\n','')
            if line == str(msg_id):
                return True
    return ans

def create_folders():
    dirs = os.listdir()
    if ('_Dictionaries' in dirs) == False:
        os.mkdir('_Dictionaries')
    if ('_DMs_history' in dirs) == False:
        os.mkdir('_DMs_history')
    if ('_Server_msg_hisory' in dirs) == False:
        os.mkdir('_Server_msg_hisory')

def clear_active_cards():
    with open('active_cards.txt', 'w') as F:
        F.write('')

toggle_commands(bot)
create_folders()
clear_active_cards() #чтобы не обманываться 
#на счет соответствия настоящего кэша и списка id

bot.run(TOKEN)
