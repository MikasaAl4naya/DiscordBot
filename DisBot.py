import random

from discord.ext import commands

from CUMgen import load_words, save_words
import discord

PREFIX = '#'
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
available_words = set()

async def load_available_words():
    global available_words
    available_words = await load_words()

class MyBOT():
    def __init__(self,bot):
        self.bot = bot


@bot.event
async def on_member_join(member):
    role_id = 771010023177453609
    role = discord.utils.get(member.guild.roles, id=role_id)
    print(role)
    if role:
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print(f"Bot doesn't have permission to manage roles or send a message to {member}")
    else:
        print(f"Role with ID {role_id} not found on the server")

    if available_words:
        # Выбор случайного слова
        random_word = random.choice(list(available_words))
        # Удаляем использованное слово из доступных и обновляем файл
        available_words.remove(random_word)
        await save_words(available_words)

        # Заменяем "кам/ком" на "CUM" внутри слова
        cum_word = random_word.replace("кам", "CUM").replace("ком", "CUM")

        await member.edit(nick=f'{cum_word}')
        for ch in bot.get_guild(member.guild.id).channels:
            if ch.name == 'хуй':
                try:
                    await bot.get_channel(ch.id).send(f'{member}, Теперь тебя зовут {member.nick}, чушпан')
                except:
                    pass


@bot.event
async def on_member_remove(member):
    global available_words
    # Возвращаем слово в доступные при выходе участника
    nick = member.nick
    if nick and nick.startswith("CUM"):
        word = f"ком{nick[3:]}"
        available_words.add(word)
        # Обновляем файл
        await save_words(available_words)
        print(f'Слово {word} было добавлено ')


