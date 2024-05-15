async def increase_boosts(clicks_per_5min=None, money_per_click=None):
    new_clicks_per_5min = None
    new_money_per_click = None

    if clicks_per_5min is not None:
        new_clicks_per_5min = int(clicks_per_5min) + 100

    if money_per_click is not None:
        new_money_per_click = int(money_per_click) + 10

    return new_clicks_per_5min, new_money_per_click

async def check_boost_level(clicks_per_5min=None, money_per_click=None):
    click_boost_level = None
    money_boost_level = None

    if clicks_per_5min is not None:
        click_boost_level = clicks_per_5min // 100

    if money_per_click is not None:
        money_boost_level = money_per_click // 10

    return click_boost_level, money_boost_level

async def increase_boost_price(base_price=100, player_level=1):
    new_price = base_price + (player_level * 10)
    return new_price