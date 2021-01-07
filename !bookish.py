from typing import List, Tuple, Dict, Union, Optional
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

def is_bookish_moderator(): #принадлежит ли юзер к администрации ПК
    # NEED TESTING
    def is_bookish_moderator_check(ctx):
        author = ctx.message.author
        admin_role     = ctx.guild.get_role(679731966228037719)
        moderator_role = ctx.guild.get_role(679732018073960475)
        # print(author.roles)
        return (admin_role in author.roles
             or moderator_role in author.roles
             or author.id == 303115719644807168
             ) #my_id
    return commands.check(is_bookish_moderator_check)

def is_bookish_server():
    def is_bookish_check(ctx):
        return ctx.message.guild.id == 673968890325237771 #First Bookish ID
    return commands.check(is_bookish_check)

def is_my_servers():
    def is_bookish_check(ctx):
        return ((ctx.message.guild.id == 673968890325237771) #First Bookish ID
            or ctx.message.guild.id == 693476909677412363)
    return commands.check(is_bookish_check)

#---------------------------------converters------------------------------------
def str_to_book(argument: str) -> Book:
    return read_book_instance_from_discord_channel(argument)


#-------------------------------COMMAND LIST------------------------------------

"""@commands.command(name = 'когда_др?')
@is_bookish_server()
async def when_bookish_created(ctx):
    await ctx.send(str(ctx.guild.created_at))"""

#----------------------------messaging commands---------------------------------
@commands.command(name = '_custom_msg',
    help = 'отправляет сообщение в канал var_id, если channel_type == server' + 
    'или отправляет сообщение юзеру var_id в личку, если channel_type == direct')
#to channels or users on the sever where command is invoked
@is_me()
@is_my_servers()
async def custom_message(ctx, channel_type: str, var_id_str: str, *args): #слишком длинный инт для питона?
    #РАБОТАЕТ ЧЕРЕЗ РАЗ
    var_id = int(var_id_str)
    print(channel_type, var_id, args)
    message = ' '.join(args)
    if channel_type == 'server':
        await ctx.guild.get_channel(var_id).send(message)
    elif channel_type == 'direct':

        print(ctx.guild)
        print(var_id)
        member = ctx.guild.get_member(var_id)
        print(member)

        await member.create_dm()
        await member.dm_channel.send(message)
    else:
        await ctx.send('`Wrong channel_type argument`')

@commands.command(
    name = '_embed_server_msg', 
    help = 'sends embed with these title, text and picture in this text channel') 
#to channels or users on the sever where command is invoked
@is_me()
@is_my_servers()
async def embed_server_msg(
        ctx, channel_id_str: str, embed_title: str, embed_text: str, 
        embed_picture_link: str):
    embed = discord.Embed(
        type = 'rich', 
        title = embed_title, 
        description = embed_text, 
        colour = discord.Colour.green())
    embed.set_image(url = embed_picture_link)
    # embed.set_image(url = another_embed_picture_link)
    channel_id = int(channel_id_str)
    await ctx.guild.get_channel(channel_id).send(embed = embed)

@commands.command(
    name = '_all_advice_embeds', #для всех эмбедов сразу
    help = 'для заполнения всех советов одним сообщением') 
#to channels or users on the sever where command is invoked
@is_me()
@is_my_servers()
async def all_advice_embeds(
        ctx, channel_id_str: str, *advice_strings): #embed_strings: List[str]
    channel_id = int(channel_id_str)
    channel = ctx.guild.get_channel(channel_id)
    # строки для каждого совета разделяются пробелами
    # параметры эмбеда внутри строки эмбеда разделяются переносом строки "\n"
    # на совет может приходиться по несколько ембедов (если надо больше одной картинки)
    for advice_string in advice_strings:
        advice_params = advice_string.split('\n')
        embed_title: str = advice_params[0]
        embed_text: str  = advice_params[1]
        embed_picture_link: str = advice_params[2]
        embed = discord.Embed(
            type = 'rich', 
            title = embed_title, 
            description = embed_text, 
            colour = discord.Colour.green())
        embed.set_image(url = embed_picture_link)
        await channel.send(embed = embed)

        #на случай, если нужны будут дополнительные ембеды для пар описание-картинка
        advice_params_number: int = len(advice_params)
        additional_embeds_number: int = (advice_params_number - 1) // 2
        for i in range(additional_embeds_number - 1):
            embed_text         = advice_params[3 + 2*i]
            embed_picture_link = advice_params[3 + 2*i + 1]
            embed = discord.Embed(
                type = 'rich', 
                description = embed_text, 
                colour = discord.Colour.green())
            embed.set_image(url = embed_picture_link)
            await channel.send(embed = embed)
    await channel.send(
        "```⬆️ ⬆️ Пожалуйста, листайте в начало канала, "
        +" чтобы увидеть всю информацию ⬆️ ⬆️```")


# ----------------------------readalong commands--------------------------------
@commands.command(name = 'ra_poll_create', 
    help = '[n: int] создать пост-голосование для выбор книги на n-ное совместное чтение')
@is_my_servers()
@is_bookish_moderator()
async def create_readalong_poll(ctx, number: int):
    global readalong #CEASE GLOBAL
    readalong = Readalong(number)
    poll_message = await ctx.send(embed = readalong.form_poll_embed())
    readalong.poll_message_id = str(poll_message.id)

@commands.command(
    name = 'ra_poll_add_book', 
    help = ('[автор --- название --- жанр(можно опустить)' +
        '--- кол-во страниц(можно опустить)] записывает книгу в список' +
        'для голосования и обновляет пост с этим голосованием'))
@is_my_servers()
@is_bookish_moderator()
async def add_book_to_readalong_poll(ctx, *, new_book: str_to_book):
    global readalong #CEASE GLOBAL
    readalong.add_book(new_book)
    poll_message = await ctx.fetch_message(readalong.poll_message_id)
    await poll_message.edit(embed = readalong.form_poll_embed())

@commands.command(
    name = 'ra_poll_delete_book', 
    help = '[номер книги в списке (от 1)] удаляет книгу из голосования')
@is_my_servers()
@is_bookish_moderator()
async def delete_book_from_readalong_poll(ctx, number: int):
    global readalong #CEASE GLOBAL
    readalong.delete_book(number) #индексирование с 1. перевод в инд. с 0 идет внутри метода
    poll_message = await ctx.fetch_message(readalong.poll_message_id)
    await poll_message.edit(embed = readalong.form_poll_embed())

@commands.command(
    name = 'ra_poll_load', 
    help = '[id сообщения] загружает сообщение ')
@is_my_servers()
@is_bookish_moderator()
async def load_readalong_poll(ctx, poll_message_id: str):
    global readalong #CEASE GLOBAL
    poll_message = await ctx.fetch_message(poll_message_id) #FIND PROPER FUNC
    poll_embed = poll_message.embeds[0] #first (and the only embed in message) 
    readalong = load_readalong_from_embed(poll_embed)

@commands.command(
    name = 'add_reactions',
    help = '[n] [id] добавляет n реакций-чисел (начиная с единицы)' +
        ' под сообщение с указанным id. n <= 10')
@is_my_servers()
@is_bookish_moderator()
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
    # bot.add_command(when_bookish_created)
    bot.add_command(create_readalong_poll)
    bot.add_command(add_book_to_readalong_poll)
    bot.add_command(delete_book_from_readalong_poll)
    bot.add_command(load_readalong_poll)
    bot.add_command(react_with_numbers)
    bot.add_command(custom_message)
    bot.add_command(embed_server_msg)
    bot.add_command(all_advice_embeds)