import discord
from discord.ext import commands
import psycopg2
from _database import cursor_exec_select, cursor_exec_edit
from _readalong_class import (Book, Readalong, read_book_instance_from_discord_channel, 
    load_readalong_from_embed)


def is_me():#decorator for is_me check
    def is_me_check(ctx):
        return ctx.message.author.id == 303115719644807168 #my_id
    return commands.check(is_me_check)

def is_bookish_server():
    def is_language_house_check(ctx):
        return ctx.message.guild.id == 673968890325237771 #First Bookish ID
    return commands.check(is_language_house_check)

#---------------------------------converters------------------------------------
def str_to_book(argument: str) -> Book:
    return read_book_instance_from_discord_channel(argument)


#-------------------------------COMMAND LIST------------------------------------
# ----------------------------readalong commands--------------------------------
@commands.command(name = 'ra_poll_create', 
    help = '[n: int] создать пост-голосование для выбор книги на n-ное совместное чтение')
#@is_me()
@is_bookish_server()
async def create_readalong_poll(ctx, number: int):
    global readalong #CEASE GLOBAL
    readalong = Readalong(number)
    poll_message = await ctx.send(embed = readalong.form_poll_embed())
    readalong.poll_message_id = str(poll_message.id)

@commands.command(name = 'ra_poll_add_book', 
    help = ('[автор --- название --- жанр(можно опустить)' +
    '--- кол-во страниц(можно опустить)] записывает книгу в список' +
    'для голосования и обновляет пост с этим голосованием'))
#@is_me()
@is_bookish_server()
async def add_book_to_readalong_poll(ctx, *, new_book: str_to_book):
    global readalong #CEASE GLOBAL
    readalong.add_book(new_book)
    poll_message = await ctx.fetch_message(readalong.poll_message_id)
    await poll_message.edit(embed = readalong.form_poll_embed())

@commands.command(name = 'ra_poll_delete_book', 
    help = ('[номер книги в списке (от 1)] удаляет книгу из голосования'))
#@is_me()
@is_bookish_server()
async def delete_book_from_readalong_poll(ctx, number: int):
    global readalong #CEASE GLOBAL
    readalong.delete_book(number) #индексирование с 1. перевод в инд. с 0 идет внутри метода
    poll_message = await ctx.fetch_message(readalong.poll_message_id)
    await poll_message.edit(embed = readalong.form_poll_embed())

@commands.command(name = 'ra_poll_load', 
    help = '[id сообщения] загружает сообщение ')
#@is_me()
@is_bookish_server()
async def load_readalong_poll(ctx, poll_message_id: str):
    global readalong #CEASE GLOBAL
    poll_message = await ctx.fetch_message(poll_message_id) #FIND PROPER FUNC
    poll_embed = poll_message.embeds[0] #first (and the only embed in message) 
    readalong = load_readalong_from_embed(poll_embed)

@commands.command(name = 'add_reactions',
    help = '[n] [id] добавляет n реакций-чисел (начиная с единицы)' +
    ' под сообщение с указанным id. n <= 10')
#@is_me()
@is_bookish_server()
async def react_with_numbers(ctx, number: int, message_id: str):
    message = await ctx.fetch_message(message_id)
    all_number_emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
    number_reactions = all_number_emojis[:number]
    for reaction in number_reactions:
        await message.add_reaction(reaction)

# ----------------------------stats --commands--------------------------------
'''@commands.command(name = '_status_dump', help = 'get status')
@is_me()
async def get_status(ctx, server_id: str):
    guild = ctx.bot.get_guild(int(server_id))
    print(guild.name)
    with open('dump_status.txt', 'wb') as F:
        for member in guild.members:
            F.write(f"{member.status} --- {member.name}\n".encode('utf-8'))
    await ctx.send("```Status dump is succsesful```")'''


def setup(bot):
    bot.add_command(create_readalong_poll)
    bot.add_command(add_book_to_readalong_poll)
    bot.add_command(delete_book_from_readalong_poll)
    bot.add_command(load_readalong_poll)
    bot.add_command(react_with_numbers)

