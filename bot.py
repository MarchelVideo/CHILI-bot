import os
import asyncio
import random
from datetime import time
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ============================
# НАЛАШТУВАННЯ
# ============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SEND_HOUR = 10   # година відправки (за Київським часом UTC+3)
SEND_MINUTE = 0  # хвилина відправки

# ============================
# ПРОМТИ ДЛЯ СТОРИС CHILI
# ============================
PROMPTS = [
    {
        "tema": "🍹 Коктейль Velvet",
        "prompt": """3D render of a premium dark-red cocktail glass bursting through a glowing Instagram post frame. 
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo. 
Deep burgundy liquid with velvet texture, golden shimmer, ice cubes flying around, 
liquid splash particles escaping the frame. 
Background: deep chili red gradient. Cinematic lighting, dramatic shadows, 
photorealistic advertising style. Vertical 9:16 format."""
    },
    {
        "tema": "🍕 Піца Yankee",
        "prompt": """3D render of a premium pizza slice exploding through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Golden crispy crust, melted cheese stretching out of frame, tomato sauce drops flying,
fresh basil leaves scattered around. 
Background: deep chili red gradient with dark vignette. 
Cinematic food photography style, dramatic lighting. Vertical 9:16 format."""
    },
    {
        "tema": "🥥 Ice Matcha & Coconut Water",
        "prompt": """3D render of a premium iced matcha coconut drink bursting through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Tall glass with layered green matcha and white coconut, condensation drops, 
ice cubes and coconut shavings flying around the frame.
Background: deep chili red gradient. Premium cinematic lighting, 
realistic textures, photorealistic advertising style. Vertical 9:16 format."""
    },
    {
        "tema": "🍔 Бургер",
        "prompt": """3D render of a premium gourmet burger exploding through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Juicy beef patty, melted cheese dripping, fresh vegetables, brioche bun with sesame seeds,
sauce drops and crumbs flying around. Red accent lighting.
Background: deep chili red gradient with dark atmosphere.
Cinematic advertising photography style. Vertical 9:16 format."""
    },
    {
        "tema": "🍸 Коктейль Peach Paradise",
        "prompt": """3D render of a premium peach cocktail bursting through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Soft orange-peach colored drink, fresh peach slices flying, liquid splash,
golden particles and bubbles escaping the frame.
Background: deep chili red to dark maroon gradient. 
Warm cinematic lighting, premium advertising style. Vertical 9:16 format."""
    },
    {
        "tema": "🥩 М'ясне антипасті",
        "prompt": """3D render of a premium meat antipasti board exploding through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Rustic dark board with premium cured meats, cheese chunks, olives flying around,
rosemary sprigs and crumbs scattered in air.
Background: deep chili red gradient with cinematic shadows.
Photorealistic food advertising style, dramatic lighting. Vertical 9:16 format."""
    },
    {
        "tema": "🌅 Атмосфера тераси",
        "prompt": """3D render of a cinematic summer terrace scene bursting through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Red plastic chairs, marble tables, black metal frame canopy, 
warm evening golden light, green plants, urban Odessa atmosphere,
bokeh light particles floating outside the frame.
Background: deep chili red gradient. Cinematic wide mood shot. Vertical 9:16 format."""
    },
    {
        "tema": "🍳 Сніданок",
        "prompt": """3D render of a premium breakfast dish bursting through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Eggs benedict or avocado toast with poached egg cut open, golden yolk dripping,
fresh herbs and microgreens flying, steam rising dramatically.
Background: deep chili red to dark gradient.
Cinematic morning light, premium food photography style. Vertical 9:16 format."""
    },
    {
        "tema": "🍜 Ризото",
        "prompt": """3D render of a premium risotto bowl exploding through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Creamy golden risotto in dark ceramic bowl, parmesan shavings flying,
truffle slices, steam wisps curling dramatically outside the frame.
Background: deep chili red gradient with atmospheric darkness.
Cinematic close-up food advertising style. Vertical 9:16 format."""
    },
    {
        "tema": "🍹 Chili Porn Star коктейль",
        "prompt": """3D render of a premium cocktail bursting through a glowing Instagram post frame.
The frame shows username 'chili_restaurant.od' and 'Odesa Ukraine' with CHILI logo.
Elegant coupe glass with passionfruit foam top, gold shimmer liquid,
passionfruit halves and tropical flowers flying around,
liquid splash particles and golden drops escaping the frame.
Background: deep chili red to black gradient. 
Premium cinematic cocktail photography. Vertical 9:16 format."""
    },
]

# ============================
# ФУНКЦІЯ ВІДПРАВКИ
# ============================
async def send_daily_prompt(bot: Bot):
    prompt_data = random.choice(PROMPTS)
    
    message = f"""🌶️ *CHILI — Сторис на сьогодні*

📌 *Тема:* {prompt_data['tema']}

━━━━━━━━━━━━━━━━━━━━
📋 *Промт для Google Flow:*
━━━━━━━━━━━━━━━━━━━━

`{prompt_data['prompt']}`

━━━━━━━━━━━━━━━━━━━━
✅ Скопіюй промт → встав у Google Flow → згенеруй → опублікуй!
"""
    
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode="Markdown"
    )

# ============================
# КОМАНДА /start
# ============================
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌶️ *CHILI Stories Bot запущено!*\n\n"
        "Щодня о 10:00 я надсилатиму тобі готовий промт для сторис.\n\n"
        "Команди:\n"
        "/prompt — отримати промт прямо зараз\n"
        "/start — перезапустити бота",
        parse_mode="Markdown"
    )

# ============================
# КОМАНДА /prompt
# ============================
async def get_prompt(update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    await send_daily_prompt(bot)

# ============================
# ЗАПУСК
# ============================
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prompt", get_prompt))
    
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(
        send_daily_prompt,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
        args=[app.bot]
    )
    scheduler.start()
    
    print("✅ CHILI Bot запущено!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
