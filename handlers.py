from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import UserProfilePhotos, File
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)
from db import connect_to_mongodb, get_collection, insert_data, check_duplicate_data

my_router = Router()


@my_router.message(CommandStart())
async def command_start(message: Message, bot: Bot, base_url: str):

    users = await get_collection("tgclick", "users")

    check_user_data = {
        "user_id": message.from_user.id,
    }

    data = {
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "is_premium": message.from_user.is_premium,
        "balance": 0,
        "clicks": 0,
        "ClicksPerhaps5min": 100,
        "OneClickMoney": 1,
        "last_click": 'None',
        'all_clicks': 0
    }

    if not await check_duplicate_data(users, check_user_data):
        user_profile_photo: UserProfilePhotos = await bot.get_user_profile_photos(message.from_user.id)
        if len(user_profile_photo.photos) > 0:
            file = await bot.get_file(user_profile_photo.photos[0][0].file_id)
            await bot.download_file(file.file_path, f"public/assets/avatars/users/{message.from_user.id}.jpg")
            data["photo_url"] = f"{message.from_user.id}.jpg"
        else:
            data["photo_url"] = 'default'
        await insert_data(users, data)

    await bot.set_chat_menu_button(
        chat_id=message.chat.id,
        menu_button=MenuButtonWebApp(text="Open Menu", web_app=WebAppInfo(url=f"{base_url}/")),
    )
    await message.answer("""Hi!\nSend me any type of message to start.\nOr just send /webview""")


@my_router.message(Command("webview"))
async def command_webview(message: Message, base_url: str):
    await message.answer(
        "Good. Now you can try to send it via Webview",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open Webview", web_app=WebAppInfo(url=f"{base_url}/")
                    )
                ]
            ]
        ),
    )