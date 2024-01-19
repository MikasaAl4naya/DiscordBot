async def load_words():
    with open('CUM_words.txt', 'r', encoding='utf-8') as file:
        return {word.strip() for word in file.readlines()}


async def save_words(words):
    with open('CUM_words.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(words))