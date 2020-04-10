import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands
from repeat_class import *
from language_edits import *

'''эмодзи в никах и сообщениях ломают кодировку (по крайней мере в блокноте)
.encode('utf-8') дает писать в файл, но ломается кириллица (так? нужны еще тесты)
сообщения из каналов сервера пишутся корректно. А в DMs - КИРИЛЛИЦА НЕ ВИДНА КАК НАДО 
'''

#создать папку, если ее нет (по аналогии с файлом в режиме W)
#продумать систему бэкапов логов_сообщений, словарей и langs (автоматический уровень + ручной уровень)
#отправить текстовый файл и картинку (чиатй FAQ почаще)
#позволить писать несколько слов взяв аргументы не сразу,а из ctx.message.content
#проследить, как работает R после разбиения на @commands
#ничего страшного, если в разных коммандах одинаково называть переменные F и file? 
#отправить все словари в отдельную папку
#сделать защиту для дурака (или хотя бы обратную связь для него) например отреагировать на #MissingArgument
#прочие цели в тг (reaction flips, reactions roles)
#ДОЧИТАТЬ СОВЕТЫ РЕНЕГАТТО
# example of that sign: `

load_dotenv()
TOKEN = os.getenv('VOCABOT_TOKEN') #unique bot token (must be secured)
GUILD = 'Первый книжный' #server name

bot = commands.Bot(command_prefix = '!v')

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
async def on_message(message): #saving of all dialogues #разобраться, какие переменные переназывать, а какие - нет.
    log_message(message) 
    await bot.process_commands(message) #эта функция разблокирует работу других комманд (смотри FAQ почаще)

@bot.check #global permission check
def user_permission_check(ctx): #applying permitted users list
    name = ctx.author.name #потом сделать проверку по [user snowflake id] и не парится
    #и получать его из сообщения/процедуры инициализации
    #print(f'author.name equals {name}') #почему этот принт срабатывает много раз после !vhelp?
    return is_user_allowed(name) #возвращаем флаг для проверки

@bot.event #обрабатываем ошибку в global permission check (читай: ошибка отсутствия разрешения)
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('```You do not have permission to use bot.```')

'''# RAISE CommandNotFound (kewl jokes are implied in this case)
if response == "I've got you, " + user + "." :
    cool_responses = ["Try something different","I've got you.. _Or not really_",
                "**English, mother#$^%*1!! Can you speak it?**","I'm speechless","Wrong command",
                "This command haven't been added yet, unfortunately"]
response = random.choice(cool_responses)'''

@bot.command(name = '.n', help = "[word] [translation] [key] For new word pair.")
async def create_word_pair(ctx, word, translation, key):
    name = ctx.author.name
    user_langs = get_langs_from_txt() # здесь и в 2х других местах всавить функцию прямо в аргуент - нельзя
    R = create_R_with_langs(name, user_langs)
    R.word = word
    R.translation = translation
    R.key = key
    s = R.info()
    print(s)
    #raw string test: R and r  worked.    
    file = R'_Dictionaries/of ' + name + R'.txt'
    #если папки нет, она не создается и ПРОГРАММА НЕ ДАЕТ ОШИБКИ
    #СОЗДАТЬ ПАПКУ, ЕСЛИ ЕЕ НЕТ! (запихнуть проверку и создание в спец функ. или найти ее)
    with open(file, 'a') as F:
        R.append_to_txt(F)
    await ctx.send(r'```New word pair has been created```')
    #это конечно хорошо, но КАК ЗАПИСЫВАТЬ СЛОВА С ПРОБЕЛАМИ?!

@bot.command(name = '.language', 
            help = "[ID] Sets up language for words")
async def set_language(ctx, language):
    user_langs = get_langs_from_txt()
    update_langs('language', ctx.author.name, language, user_langs)
    await ctx.send("```Foreign language has been changed.```") 

@bot.command(name = '.native', 
            help = "[ID] Sets up language for translations")
async def set_native(ctx, native):
    user_langs = get_langs_from_txt()
    update_langs('native', ctx.author.name, native, user_langs)
    await ctx.send("```Native language has been changed.```") 

@bot.command(name = '.dictionary', 
            help = 'Sends your dictionary in dm')
async def get_whole_dictionary(ctx):
    with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F_dm: #причесать пробелы в string.input()
        repeat_list = read_from_txt(F_dm)
    dm_dict = ''
    for i in range(len(repeat_list)):
        dm_dict += repeat_list[i].dm_info()
    #какие слова слать - большой вопрос (подумать как удобно разбить их по дате)     
    if dm_dict == '': 
        dm_dict = 'Your file is empty. _Trust me_'
    await ctx.author.create_dm()  #CHECK THIS METHOD!
    await ctx.author.dm_channel.send(dm_dict)
    print('dictionary sent in DMs')
    await ctx.send("Your dictionary is sent to your dms")

@bot.command(name = '.clr_dictionary', 
            help = 'Deletes your dictionary without backups')
async def clear_dictionary(ctx):
    with open('_' + ctx.author.name + '.txt',"w") as F_clr:
        F_clr.write('')
    await ctx.send(" Your data has been deleted. " +
     "Though you'll never be able to check this")


#-------------------------END OF COMMANDS. BEGINNING OF THE LIST OF FUNCTIONS--------------------


def is_user_allowed(user):
    ans = False #презумпция недопуска 
    with open('assigned_bot_users.txt', 'rb') as F_users: 
        for line in F_users:
            s = line.decode('utf-8')
            if (s.startswith("#") or s.startswith(' ')) == False:
                s = s.replace('\r','')
                s = s.replace('\n','')
                if user == s:
                    ans = True
                    return ans
    return ans

def log_message(message): #вынесли сюда функцию ведения стенограммы целиком
    time = message.created_at 
    author = message.author
    print(f'{message.content} --- {author} ---')
    if type(message.channel) == discord.channel.DMChannel:
        print('This is a DMChannel')
        name = message.channel.recipient.name #имя собеседника DM-канала
        with open(fR'_DMs_history\of {name}.txt', 'ab') as F:
            if author == bot.user:
                F.write(f'{bot.user.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
            else:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
    if type(message.channel) == discord.channel.TextChannel:
        print('This is a TextChannel')
        guild = message.guild
        print(message.channel)
        dirs = os.listdir('_Server_msg_hisory')
        if (f'of {guild}' in dirs) == False:
            os.mkdir(Rf'_Server_msg_hisory\of {guild}')
        with open(fR'_Server_msg_hisory\of {guild}\{message.channel}.txt', 'ab') as F:
            if author == bot.user:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
            else:
                F.write(f'{author.name} - {time}\n{message.content}\n\n'.encode('utf-8'))
    #еще есть типы каналов кроме DMChannel и TextChannel?

def create_folders():
    dirs = os.listdir()
    if ('_Dictionaries' in dirs) == False:
        os.mkdir('_Dictionaries')
    if ('_DMs_history' in dirs) == False:
        os.mkdir('_DMs_history')
    if ('_Server_msg_hisory' in dirs) == False:
        os.mkdir('_Server_msg_hisory')

create_folders()

bot.run(TOKEN)
