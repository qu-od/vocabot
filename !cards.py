#LANGUAGES MODULE
import discord
from discord.ext import commands
from _repeat_class import Repeat, cards_from_dict
from _language_edits import get_langs_from_txt, create_R_with_langs, update_langs
#from _users_admission import *

#send cards in embed
#----------------------------EVENTS AND CONVERTERS----------------------
#конвертеры должны быть прописаны раньше комманд (почему так?)
def dict_end_converter(what_end):
    if not what_end in ['first', 'last']:
        what_end = 'wrong_argument' 
    print('dict_end_converter worked')
    return what_end

def scream_case(argument): 
    print('to_upper converter worked')
    return argument.upper()

class ConverterForR(commands.Converter):
    async def convert(self, ctx, argument):
        user_langs = get_langs_from_txt()
        R = create_R_with_langs(ctx.author.name, user_langs)
        #user_langs = lambda x: get_langs_from_txt()
        R.dm_input(argument)
        return R

#------------------------------COMMANDS LIST-------------------------

#эмодзи писать в карточки пока нельзя (из-за траблов с кодировкой)
@commands.command(name = 'n', help = ' [word].[translation].[key]' + 
'adds new word in your dictionary. Key is not nessesarily')
async def create_word_pair(ctx, *, R: ConverterForR):
    file = R'_Dictionaries/of ' + ctx.author.name + '.txt'
    with open(file, 'a') as F:
        R.append_to_txt(F)
    await ctx.send('`New word pair has been created`')

@commands.command(name = 'language', 
            help = " [ID] Sets up language for words")
async def set_language(ctx, *, language: scream_case):
    print(language)
    user_langs = get_langs_from_txt()
    update_langs('language', ctx.author.name, language, user_langs)
    await ctx.send(f"```Foreign language has been changed to {language}.```")

@commands.command(name = 'native', 
            help = " [ID] Sets up language for translations")
async def set_native(ctx, *, native: scream_case):
    user_langs = get_langs_from_txt()
    update_langs('native', ctx.author.name, native, user_langs)
    await ctx.send(f"```Native language has been changed to {native}.```") 

@commands.command(name = 'cards',
        help = ' [n] [first/last] to get first/last n words in embed')
async def get_some_embed_cards(ctx, number: int, what_end: dict_end_converter):
    if what_end == 'wrong_argument':
        await ctx.send('`Wrong first/last argument`')
        return
    repeat_list = [] #чтобы len(repeat_list) была=0 если словаря нет 
    if what_end == 'last':
        number *= -1
    try:
        with open('_Dictionaries/of ' + ctx.author.name + '.txt','r') as F_dm: #причесать пробелы в string.input()
            repeat_list, info = cards_from_dict(F_dm, number)
    except FileNotFoundError:
        await ctx.send("`Your dictionary doesn't even exist. Try to enter some word pairs first`")
        return
    for R in repeat_list: #для каждой карточке в выданном списке
        #await ctx.author.create_dm() #dictionary in DMs not in ctx.channel
        #card_message = await ctx.author.dm_channel.send(embed = R.dm_embed_card('word'))
        card_message = await ctx.send(embed = R.dm_embed_card('word')) #for public testing
        await card_message.add_reaction('🔁') #add reaction on card-message
        R.append_active_card(card_message.id) #лог id и R
    info = f'`{info}\n{what_end} {len(repeat_list)} cards have sent in dm`'
    await ctx.send(info)     

#СДЕЛАТЬ ГРУППУ КОМАНД ДЛЯ ПОЛУЧЕНИЯ КАРТОЧЕК
'''@commands.command(name = 'all_cards', help = 'sends all cards in DM')
@commands.command(name = 'today_cards', help = 'sends your today's cards in DM')
@commands.command(name = 'delete_last', help = 'deletes your last card from dictionary')
@commands.command(name = '', help = '')
@commands.command(name = '', help = '')
'''
@commands.command(name = 'clr_cards', 
            help = ' Deletes your dictionary without backups')
async def clear_dictionary(ctx):
    with open('_' + ctx.author.name + '.txt',"w") as F_clr:
        F_clr.write('')
    await ctx.send(" Your data has been deleted. " +
     "Though you'll never be able to check this")
     #сделать подтверждение (are you sure)

#-----------------------FUNCS AND EXTENSION START UP-----------------------

def setup(bot):
    bot.add_command(create_word_pair)
    bot.add_command(set_language)
    bot.add_command(set_native)
    bot.add_command(get_some_embed_cards)
    bot.add_command(clear_dictionary)