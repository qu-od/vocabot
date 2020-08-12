#STATISTICS MODULE, _NOT_ GENERAL PURPOSE
import discord
import psycopg2
from discord.ext import commands
from _database import cursor_exec_select, cursor_exec_edit
#from _repeat_class import *
#from _language_edits import *
#from _users_admission import *

#ЛОГАТЬ приход/уход, все сообщения, и все статусы. 

#use this for stats _predictions_ https://pytorch.org/tutorials/
#КАТЕГОРЯ КОМАНД "stats" (вместе с cog)
#создание голосовых каналов по команде, удаление по ненужности
#статистика серва (в первую очередь войсов, сообщений, их удалений, и статусов)
#welcome message с настоящими ссылками и упоминаниями (после хоста)

def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168 #my_id
    return commands.check(is_me_check)

#-------------------------------COMMAND LIST------------------------------------

@commands.command(name = '_logs', #устанавливает канал для логов
help = '[id] of a channel for for welcome message')
@is_me()
async def set_channel(ctx, channel_id: str, server_id = None):
    try:
        query = ("DELETE FROM log_channels WHERE "
                + f"server_id = '{str(ctx.guild.id)}' AND logs_type = 'all'")
        cursor_exec_edit(query)
        query = (f"INSERT INTO log_channels VALUES ('{str(ctx.guild.id)}', 'all', "
                + f"'{channel_id}', '{str(ctx.author.id)}')")
        cursor_exec_edit(query)
        await ctx.send(f'```all_logs channel set as <#{channel_id}>```')
    except psycopg2.errors.lookup('23505'): #UniqueViolationError in sql table
        query = ("UPDATE log_channels" + 
                f" SET channel_id = '{channel_id}', logs_type = 'all'"
                + f" WHERE channel_id = '{channel_id}'")
        cursor_exec_edit(query)
        await ctx.send(f'```all_logs channel changed to <#{channel_id}> ```')

@commands.command(name = '_status_dump', help = 'get status')
@is_me()
async def get_status(ctx, server_id: str):
    guild = ctx.bot.get_guild(int(server_id))
    print(guild.name)
    with open('dump_status.txt', 'wb') as F:
        for member in guild.members:
            F.write(f"{member.status} --- {member.name}\n".encode('utf-8'))
    await ctx.send("```Status dump is succsesful```")


def setup(bot):
    bot.add_command(set_channel)
    bot.add_command(get_status)