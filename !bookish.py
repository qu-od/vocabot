#STATISTICS MODULE, _NOT_ GENERAL PURPOSE
import discord
from discord.ext import commands
#from _repeat_class import *
#from _language_edits import *
#from _users_admission import *

#КАТЕГОРЯ КОМАНД "bookish" (вместе с cog)
#команда для написания сообщения от имени бота (+через эмбед, + не открывая дс)
#custom_embed.txt в формате словаря для сборки для подготовки сообщений (узюму)
#создание голосовых каналов по команде, удаление по ненужности
#статистика серва (в первую очередь войсов, сообщений, их удалений, и статусов)
#welcome message с настоящими ссылками и упоминаниями (после хоста)

def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168 #my_id
    return commands.check(is_me_check)

#-------------------------------COMMAND LIST------------------------------------

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

@commands.command(name = '_set_logs_channel', #устанавливает канал для логов
help = '[id] of a channel for for welcome message')
@is_me()
async def set_channel(ctx, channel_id, server_id = None):
    with open('log_channel_ids.txt', 'w') as F:
        F.write(channel_id) #+ '-||-' + server_id)  
    await ctx.send(f'channel has been set as <#{channel_id}>')

def setup(bot):
    bot.add_command(set_channel)
    bot.add_command(custom_message)