import os
import random
import datetime
import pytz
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

PROMPTS = [
    {"tema": "🍹 Коктейль Velvet", "prompt": "3D render of a premium dark-red cocktail glass bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Deep burgundy liquid with velvet texture, golden shimmer, ice cubes flying around, liquid splash particles escaping the frame. Background: deep chili red gradient. Cinematic lighting, dramatic shadows, photorealistic advertising style. Vertical 9:16 format."},
    {"tema": "🍕 Піца Yankee", "prompt": "3D render of a premium pizza slice exploding through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Golden crispy crust, melted cheese stretching out of frame, tomato sauce drops flying, fresh basil leaves scattered around. Background: deep chili red gradient with dark vignette. Cinematic food photography style. Vertical 9:16 format."},
    {"tema": "🥥 Ice Matcha Coconut Water", "prompt": "3D render of a premium iced matcha coconut drink bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Tall glass with layered green matcha and white coconut, condensation drops, ice cubes and coconut shavings flying around the frame. Background: deep chili red gradient. Premium cinematic lighting. Vertical 9:16 format."},
    {"tema": "🍔 Бургер", "prompt": "3D render of a premium gourmet burger exploding through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Juicy beef patty, melted cheese dripping, fresh vegetables, brioche bun with sesame seeds, sauce drops and crumbs flying around. Background: deep chili red gradient. Cinematic advertising photography style. Vertical 9:16 format."},
    {"tema": "🍸 Peach Paradise", "prompt": "3D render of a premium peach cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Soft orange-peach colored drink, fresh peach slices flying, liquid splash, golden particles and bubbles escaping the frame. Background: deep chili red to dark maroon gradient. Warm cinematic lighting. Vertical 9:16 format."},
    {"tema": "🥩 Антипасті", "prompt": "3D render of a premium meat antipasti board exploding through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Rustic dark board with premium cured meats, cheese chunks, olives flying around, rosemary sprigs scattered in air. Background: deep chili red gradient with cinematic shadows. Vertical 9:16 format."},
    {"tema": "🌅 Тераса", "prompt": "3D render of a cinematic summer terrace scene bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Red plastic chairs, marble tables, black metal canopy, warm evening golden light, green plants, urban Odessa atmosphere, bokeh light particles floating outside the frame. Background: deep chili red gradient. Vertical 9:16 format."},
    {"tema": "🍳 Сніданок", "prompt": "3D render of a premium breakfast dish bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Eggs benedict with poached egg cut open, golden yolk dripping, fresh herbs and microgreens flying, steam rising dramatically. Background: deep chili red to dark gradient. Cinematic morning light. Vertical 9:16 format."},
    {"tema": "🍜 Ризото", "prompt": "3D render of a premium risotto bowl exploding through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Creamy golden risotto in dark ceramic bowl, parmesan shavings flying, steam wisps curling dramatically outside the frame. Background: deep chili red gradient. Cinematic close-up food advertising style. Vertical 9:16 format."},
    {"tema": "🍹 Porn Star Martini", "prompt": "3D render of a premium cocktail bursting through a glowing Instagram post frame. The frame shows username chili_restaurant.od and Odesa Ukraine with CHILI logo. Elegant coupe glass with passionfruit foam top, gold shimmer liquid, passionfruit halves and tropical flowers flying around, liquid splash and golden drops escaping the frame. Background: deep chili red to black gradient. Vertical 9:16 format."},
]

async def send_prompt(context: ContextTypes.DEFAULT_TYPE):
    p = random.choice(PROMPTS)
    text = (
        f"🌶️ CHILI — Сторис на сьогодні\n\n"
        f"📌 Тема: {p['tema']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Промт для Google Flow:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{p['prompt']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Скопіюй -> встав у Google Flow -> згенеруй -> опублікуй!"
    )
    await context.bot.send_message(chat_id=CHAT_ID, text=text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌶️ CHILI Stories Bot запущено!\n\n"
        "Щодня о 10:00 я надсилатиму готовий промт для сторис.\n\n"
        "/prompt — отримати промт прямо зараз"
    )

async def get_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_prompt(context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prompt", get_prompt))

    kyiv_tz = pytz.timezone("Europe/Kiev")
    send_time = datetime.time(hour=7, minute=0, tzinfo=kyiv_tz)
    app.job_queue.run_daily(send_prompt, time=send_time)

    print("CHILI Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
