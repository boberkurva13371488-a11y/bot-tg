import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

TOKEN = "8977965833:AAHdXevXIbB4vFUIbhjx8GUPhO5LLhhnAYs"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Кто моя бусинка?❤️",
                    callback_data="my_bussinka"
                )
            ]
        ]
    )

    await message.answer(
        "Нажми на кнопку ❤️",
        reply_markup=keyboard
    )


@dp.callback_query(lambda call: call.data == "my_bussinka")
async def bussinka(callback: CallbackQuery):
    await callback.answer(
        "Моя любимая дашуля❤️",
        show_alert=True
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
