import logging
import sys
from os import getenv

from aiohttp.web import run_app
from aiohttp.web_app import Application
from handlers import my_router
from routes import (check_data_handler,
                    send_message_handler, index_handler,
                    javascript_index_handler, styles_handler,
                    coin_handler, updateCoin_handler,
                    getCoins_handler, rating_handler,
                    javascript_rating_handler, top_users_handler,
                    serve_avatar, boosts_handler,
                    javascript_boosts_handler, boost_buy_handler,
                    get_boost_lvl)

from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from db import connect_to_mongodb, get_collection, insert_data


TOKEN = ""

APP_BASE_URL = "https://dbf6-77-105-140-135.ngrok-free.app"



async def on_startup(bot: Bot, base_url: str):
    await connect_to_mongodb()
    await bot.set_webhook(f"{base_url}/webhook")
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Open Menu", web_app=WebAppInfo(url=f"{base_url}/"))
    )

def main():
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dispatcher = Dispatcher()
    dispatcher["base_url"] = APP_BASE_URL
    dispatcher.startup.register(on_startup)

    dispatcher.include_router(my_router)

    app = Application()
    app["bot"] = bot

    app.router.add_get('/', index_handler)
    app.router.add_get('/rating', rating_handler)
    app.router.add_get('/boosts', boosts_handler)
    app.router.add_get('/styles', styles_handler)
    app.router.add_get('/javascripts/index', javascript_index_handler)
    app.router.add_get('/javascripts/rating', javascript_rating_handler)
    app.router.add_get('/javascripts/boosts', javascript_boosts_handler)
    app.router.add_get('/coin', coin_handler)
    app.router.add_post("/demo/checkData", check_data_handler)
    app.router.add_post("/demo/sendMessage", send_message_handler)
    app.router.add_post("/updateCoin", updateCoin_handler)
    app.router.add_post("/getCoins", getCoins_handler)
    app.router.add_post("/topUsers", top_users_handler)
    app.router.add_route('GET', '/avatars/{filename}', serve_avatar)
    app.router.add_post('/buyBoost', boost_buy_handler)
    app.router.add_post('/getBoostLvl', get_boost_lvl)

    SimpleRequestHandler(
        dispatcher=dispatcher,
        bot=bot,
    ).register(app, path="/webhook")
    setup_application(app, dispatcher, bot=bot)

    run_app(app, port=8080)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()