import discord
from discord.ext import commands
from _repeat_class import *
from _language_edits import *
from _users_admission import *

@commands.command(name = 'экст', help = 'команда из подключаемого файла')
async def test_general(ctx):
    await ctx.send('Участник ')

def setup(bot): #_somehow_ function identificator are fixed as "setup"
    bot.add_command(test_ext)
