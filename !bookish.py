#STATISTICS MODULE, _NOT_ GENERAL PURPOSE
import discord
from discord.ext import commands
from _repeat_class import *
from _language_edits import *
from _users_admission import *

#welcome message с настоящими ссылками и упоминаниями
#создание голосовых каналов по команде, удаление по ненужности
#ведение большой статистики серва (в первую очередь войсов, сообщений, их удалений, и статусов)

@commands.command(name = 'set_logs_channel', 
help = '[id] of a channel for for welcome message')
async def set_channel(ctx, channel_id, server_id = None):
    with open('log_channel_ids.txt', 'w') as F:
        F.write(channel_id) #+ '-||-' + server_id)  
    await ctx.send(f'channel has been set as <#{channel_id}>')

def setup(bot):
    bot.add_command(set_channel)