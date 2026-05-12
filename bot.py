import os
import random
import asyncio
import logging
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PROMPTS = [
    # === НОВІ КОКТЕЙЛІ ===
    {"tema": "🍹 Chili Porn Star — 169₴", "prompt": "3D render of a premium cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Elegant coupe glass with passionfruit foam top, vanilla vodka and prosecco shimmer, golden bubbles and tropical flowers flying around, liquid splash escaping the frame. Background: deep chili red to black gradient. Cinematic premium cocktail photography. Vertical 9:16 format."},
    {"tema": "🫐 Velvet — 149₴", "prompt": "3D render of a premium blueberry cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Deep blue-purple drink with coconut vodka, blue curacao glow, blueberry infusion splash, pineapple drops and coconut shavings flying around the frame. Background: deep chili red gradient. Cinematic lighting. Vertical 9:16 format."},
    {"tema": "🍑 Peach Paradise — 149₴", "prompt": "3D render of a premium peach cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Soft orange-peach drink, fresh peach slices flying, peach tincture drops and citrus zest scattered around. Background: deep chili red to dark maroon gradient. Warm cinematic lighting. Vertical 9:16 format."},
    {"tema": "🍎 Apple Jack — 189₴", "prompt": "3D render of a premium apple cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Fresh apple-green drink with prosecco bubbles exploding, apple slices and foam (albumin) flying around, golden drops escaping the frame. Background: deep chili red gradient. Premium advertising style. Vertical 9:16 format."},
    {"tema": "❄️ Arctic — 133₴", "prompt": "3D render of a premium mint cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Crystal clear icy drink with mint vodka, ice crystals and mint leaves flying around, cold steam rising dramatically. Background: deep chili red to dark gradient with icy blue accents. Cinematic lighting. Vertical 9:16 format."},
    {"tema": "🌞 Solaris — 149₴", "prompt": "3D render of a premium tropical cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Golden-orange drink with rum and brandy, mango and orange slices flying, almond and salted caramel drops escaping the frame. Background: deep chili red gradient. Warm tropical cinematic lighting. Vertical 9:16 format."},
    {"tema": "🍓 Маліка — 149₴", "prompt": "3D render of a premium raspberry cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Deep pink-red drink with raspberry vodka, strawberry liqueur glow, raspberry foam on top, berries flying around. Background: deep chili red gradient. Premium cinematic style. Vertical 9:16 format."},
    {"tema": "💜 Віолетта — 159₴", "prompt": "3D render of a premium violet cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Purple-blue drink with mint and mango vodka, prosecco bubbles, blueberry syrup drops and mango slices flying around with albumin foam. Background: deep chili red to dark gradient. Cinematic lighting. Vertical 9:16 format."},
    {"tema": "🍸 Мартін — 133₴", "prompt": "3D render of a premium martini cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Classic martini glass with vodka and white sweet vermouth, maraschino liqueur glow, olive and lemon zest flying around. Background: deep chili red gradient. Elegant cinematic cocktail photography. Vertical 9:16 format."},
    {"tema": "🥃 Марчелло — 133₴", "prompt": "3D render of a premium bourbon cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Amber bourbon in crystal rocks glass, maraschino and amaretto liqueurs, ice cubes and orange peel flying around, warm amber liquid splash. Background: deep chili red gradient. Cinematic whiskey advertising style. Vertical 9:16 format."},

    # === ICE MATCHA СЕРІЯ ===
    {"tema": "🥥 Ice Coconut Matcha — 135₴", "prompt": "3D render of a premium iced matcha drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Tall glass with coconut water and coconut milk matcha layers, coconut shavings and matcha powder flying around, ice cubes escaping. Background: deep chili red gradient. Premium health drink advertising style. Vertical 9:16 format."},
    {"tema": "🍍 Ice Pineapple Matcha — 135₴", "prompt": "3D render of a premium iced pineapple matcha drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Layered glass with green matcha, pineapple juice, blue Anchan tea creating color gradient, pineapple chunks and blue butterfly pea flowers flying around. Background: deep chili red gradient. Tropical cinematic style. Vertical 9:16 format."},
    {"tema": "🍓 Ice Strawberry Matcha — 135₴", "prompt": "3D render of a premium iced strawberry matcha drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Pink-green layered drink with strawberry coconut water, coconut foam on top, fresh strawberries and matcha powder flying around. Background: deep chili red gradient. Cinematic premium style. Vertical 9:16 format."},
    {"tema": "🍊 Ice Orange Matcha — 135₴", "prompt": "3D render of a premium iced orange matcha drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Vibrant orange-green layered drink with fresh orange juice and matcha, orange slices and green matcha swirls flying around. Background: deep chili red gradient. Fresh citrus cinematic style. Vertical 9:16 format."},
    {"tema": "🥰 Ice Raspberry Matcha — 135₴", "prompt": "3D render of a premium iced raspberry matcha drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Deep pink-red drink with coconut milk, raspberry puree and matcha layers, raspberry drops and coconut foam flying around. Background: deep chili red gradient. Premium soft drink advertising. Vertical 9:16 format."},

    # === СНІДАНКИ ===
    {"tema": "🥞 Вафля з лососем та авокадо — 265₴", "prompt": "3D render of a premium breakfast waffle dish bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Golden crispy waffle topped with salmon slices, creamy avocado, mixed greens flying around, lemon drops escaping the frame. Background: deep chili red gradient. Morning cinematic food photography. Vertical 9:16 format."},
    {"tema": "🍳 Американський сніданок — 315₴", "prompt": "3D render of a premium American breakfast plate bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Full breakfast plate with eggs, bacon, toast, fresh vegetables, steam rising dramatically, food elements flying around. Background: deep chili red gradient. Cinematic breakfast photography. Vertical 9:16 format."},
    {"tema": "🫐 Сирники з карамельною скоринкою — 219₴", "prompt": "3D render of premium Ukrainian cheese pancakes bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Golden syrnyky with caramel crust, walnut pieces and sour cream drops flying around, caramel drizzle escaping the frame. Background: deep chili red gradient. Warm cinematic food photography. Vertical 9:16 format."},
    {"tema": "🥑 Сніданок з тар-таром з лосося — 279₴", "prompt": "3D render of a premium salmon tartare breakfast bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Elegant breakfast with salmon tartare, orange butter sauce, microgreens flying around, citrus drops and fresh herbs escaping the frame. Background: deep chili red gradient. Fine dining morning photography. Vertical 9:16 format."},
    {"tema": "🥚 Скрамбл з тостами — 171₴", "prompt": "3D render of a premium scrambled eggs breakfast bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Creamy soft scrambled eggs on toasted bread, mixed salad greens flying around, butter and herb drops escaping the frame. Background: deep chili red gradient. Cozy breakfast cinematic style. Vertical 9:16 format."},
    {"tema": "🌾 Манна каша з горіхами — 175₴", "prompt": "3D render of a premium semolina porridge breakfast bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Creamy semolina porridge with walnut pieces, butter melting on top, nuts and honey drops flying around. Background: deep chili red gradient. Warm comfort food cinematic style. Vertical 9:16 format."},
    {"tema": "🌅 Атмосфера тераси CHILI", "prompt": "3D render of a cinematic summer terrace scene bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Red plastic chairs, marble tables, black metal canopy, warm evening golden light, green plants, urban Odessa atmosphere. Background: deep chili red gradient. Vertical 9:16 format."},
]

def get_message():
    p = random.choice(PROMPTS)
    return (
        f"🌶️ CHILI — Сторис на сьогодні\n\n"
        f"📌 Тема: {p['tema']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Промт для Google Flow:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{p['prompt']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Скопіюй -> встав у Google Flow -> згенеруй -> опублікуй!"
    )

async def send_prompt(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text=get_message())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌶️ CHILI Stories Bot\n\n"
        "Щодня о 10:00 надсилаю промт для сторис.\n\n"
        "📋 22 теми з реального меню:\n"
        "• 10 коктейлів (Velvet, Porn Star, Arctic...)\n"
        "• 5 Ice Matcha напоїв\n"
        "• 6 сніданків\n"
        "• Атмосфера тераси\n\n"
        "/prompt — отримати промт зараз"
    )

async def get_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_message())

async def daily_sender(app):
    while True:
        now = datetime.datetime.now(pytz.timezone("Europe/Kiev"))
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        logging.info(f"Next prompt in {wait_seconds:.0f} seconds")
        await asyncio.sleep(wait_seconds)
        await app.bot.send_message(chat_id=CHAT_ID, text=get_message())

async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prompt", get_prompt))

    async with app:
        await app.start()
        await app.updater.start_polling()
        logging.info("CHILI Bot started!")
        await daily_sender(app)

if __name__ == "__main__":
    asyncio.run(run())
