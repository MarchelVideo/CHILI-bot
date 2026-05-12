import os
import random
import asyncio
import logging
import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

LOGO = "vintage red chili pepper with flame logo, bold textured serif font spelling CHILI, word RESTAURANT below in small caps"

STYLE_3D = lambda product, details: f"""3D render of {product} bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with {LOGO}. {details} Background: deep chili red to dark maroon gradient. Cinematic dramatic lighting, photorealistic advertising style. Vertical 9:16 format."""

STYLE_REAL = lambda product, details: f"""Cinematic food photography of {product}. {details} Dark ceramic plate or bowl, natural warm sunlight, shallow depth of field, marble or dark wood surface, green herbs as accent. Moody restaurant atmosphere, deep shadows, rich warm tones. {LOGO} watermark bottom left. Vertical 9:16 format. No text overlays."""

PROMPTS = [
    {"tema": "🥃 Марчелло — 133₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium bourbon cocktail glass", "Amber bourbon with maraschino and amaretto, crystal rocks glass, ice cubes and orange peel twists flying around, warm golden liquid splash escaping the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Марчелло cocktail", "Crystal rocks glass with deep amber bourbon, maraschino and amaretto, single large ice cube, orange peel garnish, dramatic side lighting casting warm shadows on marble surface.")}
    ]},
    {"tema": "🫐 Velvet — 149₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a deep purple blueberry cocktail", "Blue curacao glow, coconut vodka, blueberry infusion, pineapple drops and coconut shavings flying around the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Velvet cocktail", "Elegant wine glass with deep purple-blue blueberry and blue curacao drink, ice cubes, lime wheel garnish, natural window light creating dramatic reflections on wet glass surface.")}
    ]},
    {"tema": "🍑 Peach Paradise — 149₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium peach cocktail", "Soft orange-peach drink, fresh peach slices flying, citrus zest and golden drops escaping the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Peach Paradise cocktail", "Tall glass with layered peach and orange tones, peach slice on rim, fresh herbs, warm afternoon light streaming through the glass creating amber glow on wooden table.")}
    ]},
    {"tema": "🍹 Chili Porn Star — 169₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("an elegant passionfruit cocktail coupe", "Vanilla vodka and prosecco, passionfruit foam top, golden bubbles and tropical flowers flying around.")},
        {"style": "📸", "prompt": STYLE_REAL("Chili Porn Star cocktail", "Elegant coupe glass with passionfruit foam, golden vanilla vodka prosecco base, passionfruit half beside glass, dramatic spotlight from above on dark marble surface.")}
    ]},
    {"tema": "❄️ Arctic — 133₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a crystal clear mint vodka cocktail", "Icy clear drink, mint leaves and ice crystals flying, cold steam rising dramatically.")},
        {"style": "📸", "prompt": STYLE_REAL("Arctic cocktail", "Crystal clear mint vodka drink in tall glass, fresh mint sprig, crushed ice, condensation droplets on glass, cool blue-white natural light on dark slate surface.")}
    ]},
    {"tema": "🌞 Solaris — 149₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a tropical golden rum cocktail", "Rum and brandy base, mango and orange tones, tropical fruit slices flying.")},
        {"style": "📸", "prompt": STYLE_REAL("Solaris cocktail", "Tall glass with golden tropical rum drink, mango and orange slices, warm golden hour sunlight on wooden terrace table, bokeh green plants background.")}
    ]},
    {"tema": "🍓 Маліка — 149₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a deep pink raspberry cocktail", "Raspberry vodka, strawberry liqueur, coconut syrup, raspberry foam on top, berries flying around.")},
        {"style": "📸", "prompt": STYLE_REAL("Маліка cocktail", "Coupe glass with deep pink raspberry drink topped with airy pink foam, fresh raspberries beside glass, natural side light on marble surface.")}
    ]},
    {"tema": "🍎 Apple Jack — 189₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium apple prosecco cocktail", "Apple Jack whiskey, prosecco bubbles exploding, fresh apple slices and white albumin foam flying.")},
        {"style": "📸", "prompt": STYLE_REAL("Apple Jack cocktail", "Wine glass with apple-green sparkling drink, fresh apple slice on rim, foam top, bright natural light on light marble.")}
    ]},
    {"tema": "🥥 Ice Coconut Matcha — 135₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium layered iced matcha coconut drink", "Coconut water and milk matcha layers, coconut shavings and matcha powder flying, ice cubes escaping the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Ice Coconut Matcha drink", "Tall ribbed glass with visible layered coconut milk and matcha, ice cubes, coconut shavings on top, bright natural summer light, tropical green leaf in background.")}
    ]},
    {"tema": "🍍 Ice Pineapple Matcha — 135₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a tropical pineapple matcha layered drink", "Green matcha, pineapple juice and blue Anchan tea gradient, pineapple chunks and butterfly pea flowers flying.")},
        {"style": "📸", "prompt": STYLE_REAL("Ice Pineapple Matcha", "Tall glass with stunning green-blue-yellow layered matcha pineapple drink, pineapple wedge garnish, natural light on white marble surface.")}
    ]},
    {"tema": "🍓 Ice Strawberry Matcha — 135₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a pink strawberry matcha iced drink", "Strawberry coconut water, coconut foam on top, fresh strawberries and matcha powder flying around.")},
        {"style": "📸", "prompt": STYLE_REAL("Ice Strawberry Matcha", "Beautiful pink and green layered matcha strawberry drink in ribbed glass, thick coconut foam top, fresh strawberry beside glass, warm sunlight on marble.")}
    ]},
    {"tema": "🍊 Ice Orange Matcha — 135₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a vibrant orange matcha iced drink", "Fresh orange juice and matcha swirling, orange slices and green matcha bursting out of frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Ice Orange Matcha", "Vibrant orange-green layered drink, fresh orange wheel on rim, matcha layer visible through glass, sharp natural sunlight on white ceramic tray.")}
    ]},
    {"tema": "🍣 Запечені роли", "variants": [
        {"style": "3D", "prompt": STYLE_3D("premium baked sushi rolls on dark slate", "Salmon-topped rolls with torched surface, cream sauce drizzle, microgreens flying, ginger flower escaping the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("baked salmon sushi rolls", "Close-up of torched salmon rolls on dark slate plate, cream sauce artistically drizzled, fresh microgreens, pickled ginger beside, dramatic side sunlight highlighting the glazed surface.")}
    ]},
    {"tema": "🍱 Роли в соусі", "variants": [
        {"style": "3D", "prompt": STYLE_3D("premium sushi rolls with spicy sauce", "Crispy rolls with spicy mayo and cream sauce, sesame seeds and microgreens flying, sauce drops escaping.")},
        {"style": "📸", "prompt": STYLE_REAL("premium sushi rolls", "Dark ceramic plate with elegant sushi rolls, spicy mayo and cream sauce artfully drizzled, fresh microgreens, wasabi and pickled ginger, warm restaurant light with bokeh background.")}
    ]},
    {"tema": "🥗 Салат з креветками", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium shrimp salad bowl", "Fresh shrimp on frisee lettuce, avocado, parmesan curls and mustard seeds flying around the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("premium shrimp salad", "Dark ceramic bowl with frisee lettuce, juicy shrimp, avocado chunks, curled parmesan, natural sunlight through monstera leaves creating dramatic green shadows on marble.")}
    ]},
    {"tema": "🥞 Вафля з лососем — 265₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium breakfast waffle with salmon", "Golden crispy waffle topped with salmon slices, creamy avocado, mixed greens and lemon drops flying around.")},
        {"style": "📸", "prompt": STYLE_REAL("waffle with salmon and avocado breakfast", "Golden waffle on dark plate, generous salmon slices, ripe avocado, fresh mixed greens, morning golden light, marble surface.")}
    ]},
    {"tema": "🍳 Американський сніданок — 315₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a premium full American breakfast plate", "Eggs, bacon, toast, fresh vegetables, steam rising dramatically, food elements flying.")},
        {"style": "📸", "prompt": STYLE_REAL("full American breakfast", "Dark plate with fried eggs, crispy bacon, toast, fresh tomatoes and greens, morning soft window light with steam rising, warm wooden table surface.")}
    ]},
    {"tema": "🫐 Сирники з карамеллю — 219₴", "variants": [
        {"style": "3D", "prompt": STYLE_3D("golden Ukrainian cheese pancakes", "Caramel crust syrnyky, walnut pieces and sour cream drops flying, caramel drizzle escaping the frame.")},
        {"style": "📸", "prompt": STYLE_REAL("Ukrainian syrnyky cheese pancakes", "Stack of golden syrnyky with caramel crust, walnuts, sour cream quenelle, caramel sauce pooling, warm morning light on dark ceramic plate.")}
    ]},
    {"tema": "🌅 Тераса CHILI", "variants": [
        {"style": "3D", "prompt": STYLE_3D("a cinematic summer restaurant terrace scene", "Red plastic chairs, marble tables, black metal canopy, warm golden evening light, lush green plants, urban Odessa street atmosphere.")},
        {"style": "📸", "prompt": STYLE_REAL("restaurant summer terrace evening", "Empty red chair at marble table, golden hour light streaming through green plants, black metal canopy, bokeh street background, warm atmospheric evening mood.")}
    ]},
]

def build_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎲 Рандом промт", callback_data="mix"),
        ],
        [
            InlineKeyboardButton("🎆 3D стиль", callback_data="style_3d"),
            InlineKeyboardButton("📸 Кінематограф", callback_data="style_real"),
        ],
        [
            InlineKeyboardButton("🌶️ Всі теми", callback_data="topics"),
        ]
    ])

def format_prompt(item, variant):
    icon = "🎆 3D Instagram рамка" if variant["style"] == "3D" else "📸 Кінематографічний"
    return (
        f"🌶️ *CHILI — Сторис*\n\n"
        f"📌 Тема: {item['tema']}\n"
        f"🎨 Стиль: {icon}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Промт для Google Flow:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{variant['prompt']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Скопіюй -> Google Flow -> згенеруй!"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌶️ *CHILI Stories Bot*\n\n"
        "Щодня о 10:00 надсилаю промт для сторис\\.\n\n"
        "Натискай кнопку нижче 👇",
        parse_mode="MarkdownV2",
        reply_markup=build_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mix":
        item = random.choice(PROMPTS)
        variant = random.choice(item["variants"])
        await query.message.reply_text(
            format_prompt(item, variant),
            reply_markup=build_menu()
        )

    elif query.data == "style_3d":
        item = random.choice(PROMPTS)
        variant = next((v for v in item["variants"] if v["style"] == "3D"), item["variants"][0])
        await query.message.reply_text(
            format_prompt(item, variant),
            reply_markup=build_menu()
        )

    elif query.data == "style_real":
        item = random.choice(PROMPTS)
        variant = next((v for v in item["variants"] if v["style"] == "📸"), item["variants"][-1])
        await query.message.reply_text(
            format_prompt(item, variant),
            reply_markup=build_menu()
        )

    elif query.data == "topics":
        topics = "\n".join([f"• {p['tema']}" for p in PROMPTS])
        await query.message.reply_text(
            f"🌶️ *Всі теми в боті:*\n\n{topics}",
            parse_mode="Markdown",
            reply_markup=build_menu()
        )

async def daily_sender(app):
    while True:
        now = datetime.datetime.now(pytz.timezone("Europe/Kiev"))
        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)
        wait_seconds = (target - now).total_seconds()
        logging.info(f"Next prompt in {wait_seconds:.0f} seconds")
        await asyncio.sleep(wait_seconds)
        item = random.choice(PROMPTS)
        variant = random.choice(item["variants"])
        await app.bot.send_message(
            chat_id=CHAT_ID,
            text=format_prompt(item, variant),
            reply_markup=build_menu()
        )

async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    async with app:
        await app.start()
        await app.updater.start_polling()
        logging.info("CHILI Bot started!")
        await daily_sender(app)

if __name__ == "__main__":
    asyncio.run(run())
