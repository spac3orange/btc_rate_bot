import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import aiogram_bot, target_channel  # Убедитесь, что эти переменные инициализированы корректно
import requests
from fake_useragent import UserAgent

previous_btc_usd = 0

# Прокси (по желанию)
USE_PROXY = True  # Установите False, если не хотите использовать прокси
PROXY_URL = "http://L8LsnN:cFBuKT@168.80.82.36:8000"


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    print('Bot started')

    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot, allowed_updates=["message", "inline_query", "chat_member", "chat_join_request", "callback_query"])


async def try_get_rate():
    global previous_btc_usd  # Сделаем переменную глобальной
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,rub"
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    proxies = {
        'http': PROXY_URL,
        'https': PROXY_URL
    } if USE_PROXY else None

    response = requests.get(url, headers=headers, proxies=proxies)
    data = response.json()
    print(data)
    btc_usd = data["bitcoin"]["usd"]
    btc_rub = data["bitcoin"]["rub"]
    btc_usd = '{:,.2f}'.format(btc_usd).replace(',', ' ')
    btc_rub = '{:,.2f}'.format(btc_rub).replace(',', ' ')
    btc_usd, btc_rub = btc_usd[:6].rstrip('.'), btc_rub[:9].rstrip('.')
    print(btc_usd, btc_rub)
    print(previous_btc_usd)

    if previous_btc_usd:
        percent_change_usd = ((int(btc_usd.replace(' ', '')) - previous_btc_usd) / previous_btc_usd) * 100

        percent_change_usd_str = f"🔺{abs(percent_change_usd):.2f}%" if percent_change_usd > 0 else f"🔻{abs(percent_change_usd):.2f}%"
        msg = f'💰 <b>1 BTC</b> | 🇺🇸 <b>${btc_usd[:6]}</b> | 🇷🇺 <b>₽{btc_rub[:9]}</b> | {percent_change_usd_str}'
    else:
        msg = f'💰 <b>1 BTC</b> | 🇺🇸 <b>${btc_usd[:6]}</b> | 🇷🇺 <b>₽{btc_rub[:9]}</b>'
    print(msg)

    await aiogram_bot.send_message(target_channel, msg, parse_mode='HTML')
    await asyncio.sleep(1)
    await aiogram_bot.send_message(-1002009132328, msg, parse_mode='HTML')

    previous_btc_usd = int(btc_usd.replace(' ', ''))
    await asyncio.sleep(1)


async def send_btc_rate(stop_event):
    while not stop_event.is_set():
        try:
            await asyncio.wait_for(try_get_rate(), timeout=60)
        except asyncio.TimeoutError as e:
            print(f'Timeout error: {e}')
        except Exception as e:
            print(f'Error: {e}')
        await asyncio.sleep(3600)


async def main():
    stop_event = asyncio.Event()

    # Создаем задачу для запуска бота
    task1 = asyncio.create_task(start_params())
    # Создаем задачу для периодической отправки курса BTC
    task2 = asyncio.create_task(send_btc_rate(stop_event))

    try:
        await asyncio.gather(task1, task2)
    except KeyboardInterrupt:
        print('Bot stopped')
        stop_event.set()
        await task2  # Ждем завершения send_btc_rate


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stopped')
    except Exception as e:
        print(e)
