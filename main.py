import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import aiogram_bot, target_channel
import requests

async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    print('Bot started')


    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot, allowed_updates=["message", "inline_query", "chat_member", "chat_join_request", "callback_query"])


async def send_btc_rate(target_channel):
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,rub"
    while True:
        response = requests.get(url)
        data = response.json()
        btc_usd = data["bitcoin"]["usd"]
        btc_rub = data["bitcoin"]["rub"]
        btc_usd = '{:,.2f}'.format(btc_usd).replace(',', ' ')
        btc_rub = '{:,.2f}'.format(btc_rub).replace(',', ' ')

        msg = f'💰 <b>1 BTC</b> | 🇺🇸 <b>${btc_usd.rstrip(".00")}</b> | 🇷🇺 <b>₽{btc_rub.rstrip(".00")}</b>'
        await aiogram_bot.send_message(target_channel, msg, parse_mode='HTML')
        await asyncio.sleep(1800)

async def main():
    task1 = asyncio.create_task(start_params())
    task2 = asyncio.create_task(send_btc_rate(target_channel))
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    try:
        while True:
            asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')
    except Exception as e:
        print(e)

