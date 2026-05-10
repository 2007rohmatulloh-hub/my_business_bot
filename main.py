import asyncio
import sqlite3
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message


API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# ONLY YOU CAN USE BOT
ALLOWED_USERS = [5798769777]


# DATABASE
conn = sqlite3.connect("shop.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    buy_price INTEGER,
    sell_price INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity INTEGER,
    sold_price INTEGER,
    profit INTEGER
)
""")

conn.commit()


# CHECK USER
async def check_user(message: Message):

    if message.from_user.id not in ALLOWED_USERS:
        await message.answer("❌ Siz bu botdan foydalana olmaysiz")
        return False

    return True


# START
@dp.message(Command("start"))
async def start(message: Message):

    if not await check_user(message):
        return

    text = """
🛍 Private Cosmetics Bot

Commands:

/add
/sell
/products
/stats
/colst
/cost
/budget
/profit
"""

    await message.answer(text)


# ADD PRODUCT
@dp.message(Command("add"))
async def add_product(message: Message):

    if not await check_user(message):
        return

    try:

        lines = message.text.split("\n")

        name = lines[1]
        quantity = int(lines[2])
        buy_price = int(lines[3])
        sell_price = int(lines[4])

        cur.execute(
            "INSERT INTO products(name, quantity, buy_price, sell_price) VALUES(?,?,?,?)",
            (name, quantity, buy_price, sell_price)
        )

        conn.commit()

        await message.answer("✅ Mahsulot qo'shildi")

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/add
Sariq penka
2
121000
170000
"""
        )


# PRODUCTS
@dp.message(Command("products"))
async def products(message: Message):

    if not await check_user(message):
        return

    cur.execute("SELECT * FROM products")

    products = cur.fetchall()

    if not products:
        await message.answer("❌ Mahsulot yo'q")
        return

    text = "📦 Products:\n\n"

    for product in products:

        text += (
            f"ID: {product[0]}\n"
            f"Name: {product[1]}\n"
            f"Quantity: {product[2]}\n"
            f"Buy: {product[3]}\n"
            f"Sell: {product[4]}\n\n"
        )

    await message.answer(text)


# SELL PRODUCT
@dp.message(Command("sell"))
async def sell_product(message: Message):

    if not await check_user(message):
        return

    try:

        lines = message.text.split("\n")

        product_id = int(lines[1])
        quantity_sold = int(lines[2])
        sold_price = int(lines[3])

        cur.execute(
            "SELECT quantity, buy_price FROM products WHERE id=?",
            (product_id,)
        )

        product = cur.fetchone()

        if not product:
            await message.answer("❌ Product topilmadi")
            return

        current_quantity = product[0]
        buy_price = product[1]

        if quantity_sold > current_quantity:
            await message.answer("❌ Yetarli mahsulot yo'q")
            return

        new_quantity = current_quantity - quantity_sold

        cur.execute(
            "UPDATE products SET quantity=? WHERE id=?",
            (new_quantity, product_id)
        )

        profit = sold_price - (buy_price * quantity_sold)

        cur.execute(
            "INSERT INTO sales(product_id, quantity, sold_price, profit) VALUES(?,?,?,?)",
            (product_id, quantity_sold, sold_price, profit)
        )

        conn.commit()

        await message.answer(
            f"✅ Sotildi\n\n💰 Profit: {profit} so'm"
        )

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/sell
1
1
170000
"""
        )


# STATS
@dp.message(Command("stats"))
async def stats(message: Message):

    if not await check_user(message):
        return

    cur.execute("SELECT COUNT(*) FROM products")
    products_count = cur.fetchone()[0]

    cur.execute("SELECT SUM(quantity) FROM products")
    total_quantity = cur.fetchone()[0]

    cur.execute("SELECT SUM(sold_price) FROM sales")
    total_sales = cur.fetchone()[0]

    cur.execute("SELECT SUM(profit) FROM sales")
    total_profit = cur.fetchone()[0]

    total_quantity = total_quantity or 0
    total_sales = total_sales or 0
    total_profit = total_profit or 0

    text = f"""
📊 Statistics

📦 Products: {products_count}
🛍 Total quantity: {total_quantity}
💰 Sold money: {total_sales}
📈 Profit: {total_profit}
"""

    await message.answer(text)


# HOW MUCH PRODUCTS COST YOU
@dp.message(Command("colst"))
async def colst(message: Message):

    if not await check_user(message):
        return

    cur.execute(
        "SELECT SUM(quantity * buy_price) FROM products"
    )

    total = cur.fetchone()[0]

    total = total or 0

    await message.answer(
        f"📦 Sizning mahsulotlaringiz tannarxi: {total} so'm"
    )


# HOW MUCH YOU CAN SELL ALL PRODUCTS
@dp.message(Command("cost"))
async def cost(message: Message):

    if not await check_user(message):
        return

    cur.execute(
        "SELECT SUM(quantity * sell_price) FROM products"
    )

    total = cur.fetchone()[0]

    total = total or 0

    await message.answer(
        f"💰 Hamma mahsulot sotilsa: {total} so'm"
    )


# TOTAL SOLD MONEY
@dp.message(Command("budget"))
async def budget(message: Message):

    if not await check_user(message):
        return

    cur.execute(
        "SELECT SUM(sold_price) FROM sales"
    )

    total = cur.fetchone()[0]

    total = total or 0

    await message.answer(
        f"💵 Umumiy sotuv: {total} so'm"
    )


# CLEAN PROFIT
@dp.message(Command("profit"))
async def profit(message: Message):

    if not await check_user(message):
        return

    cur.execute(
        "SELECT SUM(profit) FROM sales"
    )

    total = cur.fetchone()[0]

    total = total or 0

    await message.answer(
        f"📈 Sof foyda: {total} so'm"
    )


# MAIN
async def main():

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# HOW TO USE

## /add

# ```text
# /add
# Sariq penka
2
121000
170000
# ````````````

## /sell

# /sell
1
1
170000

