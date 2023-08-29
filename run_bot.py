import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from sqlalchemy.exc import NoResultFound

from tg_bot.models import User, Post
from tg_bot.db.connection import db

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=os.getenv("TG_TOKEN"))
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    print(message.from_user.id)
    await message.answer("Hello!")


@dp.message(Command("me"))
async def me(message: types.Message) -> None:
    try:
        user = await User.get(tg_id=message.from_user.id)
    except NoResultFound:
        await message.answer("Зарегистрируйтесь на сайте ....")

    else:
        await message.answer(
            f"Вы зарегистрированы на сайте:\n"
            f"{user.username}, {user.id}, {user.date_joined}"
        )


@dp.message(Command("posts"))
async def posts(message: types.Message) -> None:
    try:
        await User.get(tg_id=message.from_user.id)
    except NoResultFound:
        await message.answer("Зарегистрируйтесь на сайте ....")
        return

    all_posts = await Post.get_all()
    answer_text = ""

    for post in all_posts:
        answer_text += f"<a href=\"http://127.0.0.1:8000/posts/{post.id}\">{post.title}</a>\n{post.content}\n\n"

    await message.answer(answer_text, parse_mode="html")


# Запуск процесса поллинга новых апдейтов
async def main():
    db.init()  # Подключение к базе
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
