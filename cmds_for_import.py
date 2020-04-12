import os
import discord
import random
from dotenv import load_dotenv
from discord.ext import commands
from _repeat_class import *
from _language_edits import *
from _users_admission import *

bot_prefix = '!v ' #на случай, если забудем параметризовать парс команд

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
        await my_member.dm_channel.send("```modules test run```")
        print('start_dm_sent')
    else:
        print('that user is not allowed. Start dm was not send')      

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure): #обрабатываем ошибку отсутствия разрешения
        await ctx.send('`You do not have permission to use bot.`')
    if isinstance(error, commands.errors.CommandNotFound):  #обрабатываем ошибку "команды нет"
        cool_responses = ["Try something different","I've got you.. _Or not really_",
                    "**English, mother#$^%*1!! Can you speak it?**","I'm speechless","Wrong command",
                    "This command haven't been added yet, unfortunately"]
        #await ctx.send(random.choice(cool_responses))
        await ctx.send(f'`{random.choice(cool_responses)}`')

@bot.check #global permission check
def user_permission_check(ctx): #applying permitted users list
    name = ctx.author.name #потом сделать проверку по [user snowflake id] и не парится
    #и получать его из сообщения/процедуры инициализации
    #print(f'author.name equals {name}') #почему этот принт срабатывает много раз после !vhelp?
    return is_user_allowed(name) #возвращаем флаг для проверки
    

#---------------------------------------------TESTING FACILITY---------------------

    
bot.run(TOKEN)