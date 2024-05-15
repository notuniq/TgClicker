from pathlib import Path
import math
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_request import Request
from aiohttp.web_response import json_response
from boost_levels import check_boost_level, increase_boosts, increase_boost_price

from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InputTextMessageContent,
    WebAppInfo,
)
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from db import (connect_to_mongodb, get_collection,
                insert_data, check_duplicate_data,
                update_one_document, find_one_document,
                get_top_users)
from aiohttp import web
from datetime import datetime

async def serve_avatar(request: web.Request):
    # Получаем имя файла из запроса
    filename = request.match_info.get('filename', None)
    if not filename:
        return web.Response(status=404)

    # Формируем путь к файлу

    if filename == 'default':
        filepath = Path(__file__).parent.resolve() / f"public/assets/avatars/default.png"
    else:
        filepath = Path(__file__).parent.resolve() / f"public/assets/avatars/users/{filename}"

    # Проверяем, существует ли файл
    if not filepath.is_file():
        return web.Response(status=404)

    # Возвращаем файл как ответ
    return web.FileResponse(filepath)

async def index_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "views/index.html")

async def rating_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "views/rating.html")

async def boosts_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "views/boosts.html")

async def styles_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "public/css/styles.css")

async def javascript_index_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "public/js/index.js")

async def javascript_rating_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "public/js/rating.js")

async def javascript_boosts_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "public/js/boosts.js")

async def coin_handler(request: Request):
    return FileResponse(Path(__file__).parent.resolve() / "public/assets/coin.png")

async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    if check_webapp_signature(bot.token, data["_auth"]):
        return json_response({"ok": True})
    return json_response({"ok": False, "err": "Unauthorized"}, status=401)

async def getCoins_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        users = await get_collection("tgclick", "users")
        print(web_app_init_data)
        check_user_data = {
            "user_id": web_app_init_data.user.id,
        }

        if not await check_duplicate_data(users, check_user_data):
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
        else:
            coins = await find_one_document(users, check_user_data)

            # if coins['photo_url'] == '':
            #
            #     photo_url = {
            #         "photo_url": web_app_init_data.user.photo_url
            #     }
            #
            #     await update_one_document(users, check_user_data, photo_url)

            return json_response({"ok": True, "Coins": coins['balance']})

    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

async def updateCoin_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        users = await get_collection("tgclick", "users")

        check_user_data = {
            "user_id": web_app_init_data.user.id,
        }

        user = await find_one_document(users, check_user_data)

        if not await check_duplicate_data(users, check_user_data):
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
        else:
            current_time = datetime.now()

            if user['last_click'] == 'None':
                current_timer = datetime.now().replace(microsecond=0)
                last_click_time = datetime.strptime(str(current_timer), '%Y-%m-%d %H:%M:%S')
            else:
                last_click_time = datetime.strptime(user['last_click'], '%Y-%m-%d %H:%M:%S')

            time_difference = (current_time - last_click_time).total_seconds()

            if time_difference < 300 and user['clicks'] >= user['ClicksPerhaps5min']:
                return json_response({"ok": True, "Coins": user['balance'], "ClicksReached": f"У вас есть ограничение: вы не можете выполнить более {user['ClicksPerhaps5min']} кликов в течение 5 минут. Доступ откроется через: {math.ceil((300 - time_difference) // 60)} минут."})

            if time_difference > 300:
                update_data = {
                    "balance": user['OneClickMoney'] + int(user['balance']),
                    "clicks": 1,
                    "last_click": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "all_clicks": int(user['all_clicks']) + 1
                }
            else:
                update_data = {
                    "balance": user['OneClickMoney'] + int(user['balance']),
                    "clicks": 1 + int(user['clicks']),
                    "last_click": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "all_clicks": int(user['all_clicks']) + 1
                }


            await update_one_document(users, check_user_data, update_data)
            user_info = await find_one_document(users, check_user_data)
            return json_response({"ok": True, "Coins": user_info['balance']})

    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)


async def send_message_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

    reply_markup = None
    if data["with_webview"] == "1":
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Open",
                        web_app=WebAppInfo(url=str(request.url.with_scheme("https"))),
                    )
                ]
            ]
        )
    await bot.answer_web_app_query(
        web_app_query_id=web_app_init_data.query_id,
        result=InlineQueryResultArticle(
            id=web_app_init_data.query_id,
            title="Demo",
            input_message_content=InputTextMessageContent(
                message_text="Hello, World!",
                parse_mode=None,
            ),
            reply_markup=reply_markup,
        ),
    )
    return json_response({"ok": True})

async def top_users_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        users = await get_collection("tgclick", "users")
        top_users = await get_top_users(users)

        top_users_data = []
        for user in top_users:
            user_data = {
                "user_id": user["user_id"],
                "first_name": user["first_name"],
                "photo_url": user["photo_url"],
                "balance": user["balance"]
            }
            top_users_data.append(user_data)

        user_position = next((index + 1 for index, user in enumerate(top_users) if user["user_id"] == web_app_init_data.user.id), None)

        return json_response({"ok": True, "top_users": top_users_data, "user_position": user_position})

    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

async def boost_buy_handler(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        users = await get_collection("tgclick", "users")

        check_user_data = {
            "user_id": web_app_init_data.user.id,
        }

        if not await check_duplicate_data(users, check_user_data):
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
        else:
            user = await find_one_document(users, check_user_data)
            buyBoost = data['boostId']
            userBalance = int(user['balance'])

            get_lvl = await check_boost_level(int(user['ClicksPerhaps5min']), int(user['OneClickMoney']))

            get_new_cost_5min = await increase_boost_price(1500, int(get_lvl[0]))
            get_new_cost_clicks = await increase_boost_price(1000, int(get_lvl[1]))

            if buyBoost == '5mins':
                if userBalance < get_new_cost_5min:
                    return json_response({"ok": True, 'error': 'Не достаточно средств!'})

                newBoostLvl = await increase_boosts(int(user['ClicksPerhaps5min']), None)

                new_data = {
                    'ClicksPerhaps5min': newBoostLvl[0],
                    "balance": user['balance'] - get_new_cost_5min
                }

                await update_one_document(users, check_user_data, new_data)
            elif buyBoost == 'clicks':

                if userBalance < get_new_cost_clicks:
                    return json_response({"ok": True, 'error': 'Не достаточно средств!'})

                newBoostLvl = await increase_boosts(None, int(user['OneClickMoney']))

                new_data = {
                    'OneClickMoney': newBoostLvl[1],
                    "balance": user['balance'] - get_new_cost_clicks
                }

                await update_one_document(users, check_user_data, new_data)
            else:
                return json_response({"ok": False, "err": "Unauthorized"}, status=401)

            get_new_cost_5min = await increase_boost_price(1500, int(get_lvl[0]) + 1)
            get_new_cost_clicks = await increase_boost_price(1000, int(get_lvl[1]) + 1)

            return json_response({"ok": True, "ClicksPerhaps5minCost": get_new_cost_5min, "OneClickMoneyCost": get_new_cost_clicks, "ClicksPerhaps5min": f"{get_lvl[0]}", "OneClickMoney": f'{get_lvl[1]}'})
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)

async def get_boost_lvl(request: Request):
    bot: Bot = request.app["bot"]
    data = await request.post()
    try:
        web_app_init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
        users = await get_collection("tgclick", "users")

        check_user_data = {
            "user_id": web_app_init_data.user.id,
        }

        if not await check_duplicate_data(users, check_user_data):
            return json_response({"ok": False, "err": "Unauthorized"}, status=401)
        else:
            user = await find_one_document(users, check_user_data)

            get_lvl = await check_boost_level(int(user['ClicksPerhaps5min']), int(user['OneClickMoney']))

            get_new_cost_5min = await increase_boost_price(1500, int(get_lvl[0]))
            get_new_cost_clicks = await increase_boost_price(1000, int(get_lvl[1]))

            return json_response({"ok": True, "ClicksPerhaps5minCost": get_new_cost_5min, "OneClickMoneyCost": get_new_cost_clicks, "ClicksPerhaps5min": f"{get_lvl[0]}", "OneClickMoney": f'{get_lvl[1]}', 'UserClicks': user['clicks'], "Clicks5min": int(user['ClicksPerhaps5min']), "ClicksMoney": int(user['OneClickMoney'])})
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)