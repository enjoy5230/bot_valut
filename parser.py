import aiohttp
import asyncio
from datetime import datetime

async def fetch_currency_rate():
    """Парсит курс USD и EUR с сайта ЦБ РФ"""
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            
            usd_rate = data["Valute"]["USD"]["Value"]
            eur_rate = data["Valute"]["EUR"]["Value"]
            
            return {
                "USD": round(usd_rate, 2),
                "EUR": round(eur_rate, 2),
                "updated_at": datetime.now().strftime("%d.%m.%Y %H:%M")
            }

# Тест
if __name__ == "__main__":
    import asyncio
    rates = asyncio.run(fetch_currency_rate())
    print(rates)
