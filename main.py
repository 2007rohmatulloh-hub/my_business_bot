import asyncio
import sqlite3
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# ONLY YOU CAN USE BOT
ALLOWED_USERS = [5798769777]


# MENU
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add"), KeyboardButton(text="/sell")],
        [KeyboardButton(text="/products"), KeyboardButton(text="/stats")],
        [KeyboardButton(text="/edit"), KeyboardButton(text="/delete")],
        [KeyboardButton(text="/search")]
    ],
    resize_keyboard=True
)


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

        await message.answer(
            "❌ Siz bu botdan foydalana olmaysiz"
        )

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
/edit
/delete
/search
"""

    await message.answer(
        text,
        reply_markup=menu
    )


# ADD PRODUCT
@dp.message(Command("add"))
async def add_product(message: Message):

    if not await check_user(message):
        return

    if message.text.strip() == "/add":

        await message.answer(
            """
Example:

/add
Sariq penka
2
121000
170000
""",
            reply_markup=menu
        )

        return

    try:

        lines = message.text.split("\n")

        name = lines[1]
        quantity = int(lines[2])
        buy_price = int(lines[3])
        sell_price = int(lines[4])

        cur.execute(
            """
            INSERT INTO products(
                name,
                quantity,
                buy_price,
                sell_price
            )
            VALUES(?,?,?,?)
            """,
            (
                name,
                quantity,
                buy_price,
                sell_price
            )
        )

        conn.commit()

        await message.answer(
            "✅ Mahsulot qo'shildi",
            reply_markup=menu
        )

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
""",
            reply_markup=menu
        )

# PRODUCTS
@dp.message(Command("products"))
async def products(message: Message):

    if not await check_user(message):
        return

    cur.execute("SELECT * FROM products")

    products = cur.fetchall()

    if not products:

        await message.answer(
            "❌ Mahsulot yo'q",
            reply_markup=menu
        )

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

    await message.answer(
        text,
        reply_markup=menu
    )


# SELL PRODUCT
# SELL PRODUCT
@dp.message(Command("sell"))
async def sell_product(message: Message):

    if not await check_user(message):
        return

    if message.text.strip() == "/sell":

        await message.answer(
            """
Example:

/sell
1
3
150000

1 = product ID
3 = quantity
150000 = 1 ta narxi
""",
            reply_markup=menu
        )

        return

    try:

        lines = message.text.split("\n")

        product_id = int(lines[1])
        quantity_sold = int(lines[2])
        sold_price = int(lines[3])

        cur.execute(
            """
            SELECT quantity, buy_price
            FROM products
            WHERE id=?
            """,
            (product_id,)
        )

        product = cur.fetchone()

        if not product:

            await message.answer(
                "❌ Product topilmadi",
                reply_markup=menu
            )

            return

        current_quantity = product[0]
        buy_price = product[1]

        if quantity_sold > current_quantity:

            await message.answer(
                "❌ Yetarli mahsulot yo'q",
                reply_markup=menu
            )

            return

        new_quantity = current_quantity - quantity_sold

        cur.execute(
            """
            UPDATE products
            SET quantity=?
            WHERE id=?
            """,
            (
                new_quantity,
                product_id
            )
        )

        total_sale = sold_price * quantity_sold

        profit = total_sale - (
            buy_price * quantity_sold
        )

        cur.execute(
            """
            INSERT INTO sales(
                product_id,
                quantity,
                sold_price,
                profit
            )
            VALUES(?,?,?,?)
            """,
            (
                product_id,
                quantity_sold,
                total_sale,
                profit
            )
        )

        conn.commit()

        await message.answer(
            f"""
✅ Sotildi

💵 Sotuv: {total_sale} so'm
💰 Profit: {profit} so'm
""",
            reply_markup=menu
        )

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/sell
1
3
150000

1 = product ID
3 = quantity
150000 = 1 ta narxi
""",
            reply_markup=menu
        )

# STATS
@dp.message(Command("stats"))
async def stats(message: Message):

    if not await check_user(message):
        return

    cur.execute(
        "SELECT COUNT(*) FROM products"
    )

    products_count = cur.fetchone()[0]

    cur.execute(
        "SELECT SUM(quantity) FROM products"
    )

    total_quantity = cur.fetchone()[0]

    cur.execute(
        "SELECT SUM(sold_price) FROM sales"
    )

    total_sales = cur.fetchone()[0]

    cur.execute(
        "SELECT SUM(profit) FROM sales"
    )

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

    await message.answer(
        text,
        reply_markup=menu
    )


# EDIT PRODUCT
# EDIT PRODUCT
@dp.message(Command("edit"))
async def edit_product(message: Message):

    if not await check_user(message):
        return

    if message.text.strip() == "/edit":

        await message.answer(
            """
Example:

/edit
1
Ruz mari
5
84000
150000
""",
            reply_markup=menu
        )

        return

    try:

        lines = message.text.split("\n")

        product_id = int(lines[1])
        name = lines[2]
        quantity = int(lines[3])
        buy_price = int(lines[4])
        sell_price = int(lines[5])

        cur.execute(
            """
            UPDATE products
            SET
                name=?,
                quantity=?,
                buy_price=?,
                sell_price=?
            WHERE id=?
            """,
            (
                name,
                quantity,
                buy_price,
                sell_price,
                product_id
            )
        )

        conn.commit()

        await message.answer(
            "✅ Mahsulot yangilandi",
            reply_markup=menu
        )

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/edit
1
Ruz mari
5
84000
150000
""",
            reply_markup=menu
        )

# DELETE PRODUCT
# DELETE PRODUCT
@dp.message(Command("delete"))
async def delete_product(message: Message):

    if not await check_user(message):
        return

    if message.text.strip() == "/delete":

        await message.answer(
            """
Example:

/delete
1
""",
            reply_markup=menu
        )

        return

    try:

        lines = message.text.split("\n")

        product_id = int(lines[1])

        cur.execute(
            """
            DELETE FROM products
            WHERE id=?
            """,
            (product_id,)
        )

        conn.commit()

        await message.answer(
            "🗑 Mahsulot o'chirildi",
            reply_markup=menu
        )

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/delete
1
""",
            reply_markup=menu
        )
# SEARCH
@dp.message(Command("search"))
async def search_product(message: Message):

    if not await check_user(message):
        return

    try:

        lines = message.text.split("\n")

        query = lines[1]

        if query.isdigit():

            cur.execute(
                """
                SELECT *
                FROM products
                WHERE id=?
                """,
                (int(query),)
            )

        else:

            cur.execute(
                """
                SELECT *
                FROM products
                WHERE name LIKE ?
                """,
                (f"%{query}%",)
            )

        products = cur.fetchall()

        if not products:

            await message.answer(
                "❌ Mahsulot topilmadi",
                reply_markup=menu
            )

            return

        text = "🔍 Search results:\n\n"

        for product in products:

            text += (
                f"ID: {product[0]}\n"
                f"Name: {product[1]}\n"
                f"Quantity: {product[2]}\n"
                f"Buy: {product[3]}\n"
                f"Sell: {product[4]}\n\n"
            )

        await message.answer(
            text,
            reply_markup=menu
        )

    except:

        await message.answer(
            """
❌ Format noto'g'ri

Example:

/search
Ruz

yoki

/search
1
""",
            reply_markup=menu
        )


# MAIN
async def main():

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())