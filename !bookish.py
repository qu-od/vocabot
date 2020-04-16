import discord
from discord.ext import commands
from _repeat_class import *
from _language_edits import *
from _users_admission import *

bot_prefix = '!v ' #на случай, если забудем параметризовать парс команд

@commands.command(name = 'import ext test', help = 'import-able command')
async def imported_command(ctx):
    await ctx.send('output prior to embed')
    await ctx.send({embed: {
  color: 3447003,
  description: "__**IMPORT COMMAND VIA EXTENSION WORKED!**__"
}})

    
