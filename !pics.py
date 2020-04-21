#"POPULAR BUT NOT YET DONE FUNCS" MODULE
import discord
from discord.ext import commands
#from _users_admission import is_user_allowed

#-

@commands.command(name = 'pics_test', help = 'pics extension')
async def pics_test(ctx):
    await ctx.send('pics_test worked')

def setup(bot):
    bot.add_command(pics_test)

#print('RUNNING PICS EXTENTION AFTER SETUP') 
# это работает при вызове bot.load_extension() в main

