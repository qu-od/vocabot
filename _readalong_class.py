import discord
from _database import cursor_exec_select, cursor_exec_edit
from typing import List, Tuple, Union
#класс для книжек и совместных чтений
#написать метод обновления таблички БД, записывая новые книжки
#пока что информацию о Readalong будем использовать в посте.

class Book(object):
    def __init__(self, author: str , book_name: str, genre: str = None,
            page_number: int = None):
        # в аргументах все строки
        self.author: str  = author
        self.book_name: str = book_name
        self.genre: str = genre
        self.page_number: int = page_number

    def __str__(self) -> str:
        s: str = f'{self.author} --- "{self.book_name}"'
        if self.genre: s += f' --- {self.genre}'
        if self.page_number: s += f' --- {self.page_number}стр.'
        return s

def read_book_instance_from_discord_channel(book_str: str) -> Book:
    author, book = book_str.split(' --- ')
    #добавить считывание опциональных параметров
    #PAGE NUMBER BUST BE AN INT THERE
    return Book(author, book)


class Readalong(object):
    def __init__(self, number: int, books = [], poll_message_id = None): 
        #books and poll_message_id provided when poll being loaded 
            #and doesn't provided if poll is being created
        self.number: int = number #номер совместного чтения
        self.books: list = books
        self.poll_message_id: str = poll_message_id

    def __str__(self) -> str:
        return ('\n'.join([f'**{str(i+1)}**. {self.books[i].__str__()}' for i in range(len(self.books))]) +
            f'\nid: {self.poll_message_id}')
        
    def add_book(self, book: Book): #book
        self.books.append(book)

    def delete_book(self, book_number):
        self.books.pop(book_number - 1) 
    #delete_book(1) удалит первый в списке книгу (с интексом 0)

    def form_poll_embed(self) -> discord.Embed:
        embed_text = self.__str__()
        poll_embed = discord.Embed(title = '**Варианты книг на 4-е совместное чтение.**\n__**Голосование**__', type = 'rich', 
            description = embed_text, colour = discord.Colour.blurple())
        return poll_embed

def load_readalong_from_embed(poll_embed: discord.Embed) -> Readalong:
    number = int(poll_embed.title.split('-е')[0].split(' ')[-1]) #вырезали число из Заголовка Эмбеда
    print(poll_embed.description)
    embed_lines = poll_embed.description.split('\n')
    last_embed_line = embed_lines.pop(-1) #удаляем последний элемент (в нем строка с ID)
    def dot_split(embed_line: str) -> List[str]: return embed_line.split('. ', 1)[1]
    book_strings = list(map(dot_split, embed_lines))
    print(book_strings)
    books = list(map(read_book_instance_from_discord_channel, book_strings))
    poll_message_id: str = last_embed_line.split(': ')[1]
    return Readalong(number, books = books, poll_message_id = poll_message_id)