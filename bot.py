import os
import random
import asyncio
import logging
import datetime
import json
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
KYIV = pytz.timezone("Europe/Kiev")
HISTORY_FILE = "/tmp/chili_history.json"

# ============================
# БРЕНД CHILI — ТОЧНИЙ ОПИС
# ============================

LOGO = (
    "vintage distressed red chili pepper with flame logo in bottom-left corner, "
    "bold weathered serif font spelling CHILI in dark red, small caps RESTAURANT below, "
    "slightly worn texture, authentic street restaurant feel"
)

INTERIOR = (
    "CHILI restaurant Odessa: coral-red perforated plastic chairs, grey marble-veined tables, "
    "dark graphite metal canopy frame, cobblestone terrace floor, city street view of Odessa in background, "
    "lush green bushes and trees surrounding the terrace, warm summer light"
)

CHANDELIER = (
    "iconic large circular chandelier made of hundreds of dark glossy ceramic chili peppers "
    "arranged in three tiers, warm amber glow from within, hanging in center of restaurant, "
    "green vine plants cascading from black metal shelving on walls"
)

HALL = (
    "CHILI restaurant interior: warm oak wooden tables, cognac brown leather bucket chairs, "
    "geometric wire starburst pendant lights, raw concrete ceiling with exposed silver ventilation ducts, "
    "green monstera and pothos plants hanging everywhere, black metal mezzanine with rope railings above, "
    "open kitchen visible in background"
)

BAR = (
    "CHILI restaurant bar: glowing green-yellow textured panel front, dark counter top, "
    "hundreds of crystal glasses hanging upside down from rack, green decorative floor tiles, "
    "botanicals and trailing vine plants above bar, warm amber backlighting"
)

# 3D стиль — вибух з Instagram рамки
def S3D(subject, action, particles, extras=""):
    return (
        f"Hyper-realistic 3D CGI advertising render, vertical 9:16 format. "
        f"{subject} dramatically bursting through a glowing smartphone Instagram post UI frame. "
        f"The frame shows: username 'chili_restaurant.od', location 'Odesa Ukraine', {LOGO}. "
        f"Frame has gold-metallic border, UI elements (heart, comment, share icons) at bottom. "
        f"{action} "
        f"Particle explosion: {particles}. "
        f"Background: deep chili red #CE1616 to near-black #370402 radial gradient with volumetric fog. "
        f"Cinematic studio lighting — key light from upper-right, dramatic shadows, lens flare. "
        f"8K photorealistic textures, depth of field blur on background. "
        f"{extras}"
        f"Style: premium food & beverage advertising CGI, like high-end commercial photography."
    )

# Кінематографічний стиль — реалістичне фото
def SREAL(subject, setting, mood, extras=""):
    return (
        f"Cinematic food & beverage photography, vertical 9:16 format, shot on Sony A7 with 85mm f/1.4. "
        f"{subject}. "
        f"Setting: {setting}. "
        f"Lighting: {mood}. "
        f"Shallow depth of field, foreground bokeh blur, rich texture detail. "
        f"Color grade: deep warm tones, lifted blacks, chili red #CE1616 accent elements, "
        f"golden amber highlights, deep shadows with slight red tint. "
        f"{LOGO} subtly watermarked bottom-left. "
        f"{extras}"
        f"No text overlays. Style: editorial restaurant photography, Vogue-level food styling."
    )

# ============================
# ПРОМТИ
# ============================

PROMPTS = [

    # === КОКТЕЙЛІ ===

    {"tema": "🥃 Марчелло — 133₴", "category": "cocktail",
     "caption": "Бурбон, амаретто та мараскіно — три інгредієнти, один ідеальний вечір 🥃\nЧекаємо у CHILI 🌶️\n\n#chiliodessa #коктейлі #одеса #bar #bourbon",
     "refs_note": "📸 Фото готового коктейлю Марчелло\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a premium crystal rocks glass containing deep amber bourbon",
            "Warm golden bourbon liquid with maraschino and amaretto swirling, large crystal-clear ice cube center, "
            "twisted orange peel garnish draped over glass rim, condensation droplets on crystal facets. "
            "The glass SHATTERS through the Instagram frame, liquid splash arcing dramatically outside. ",
            "amber liquid droplets mid-air, spinning ice shards, orange zest curling upward, "
            "golden whiskey mist catching the light, scattered cocktail cherries",
            "Frame tilted at 15-degree angle for dynamic composition."
        )},
        {"style": "📸", "prompt": SREAL(
            "Марчелло cocktail — crystal rocks glass with deep amber bourbon, maraschino and amaretto, "
            "single oversized hand-cut ice cube, elegant twisted orange peel garnish",
            f"{BAR} — glass on dark marble bar counter",
            "Single dramatic spotlight from above-left creating long shadow, warm amber tones"
        )}
    ]},

    {"tema": "🫐 Velvet — 149₴", "category": "cocktail",
     "caption": "Не просто коктейль — це настрій 💜\nЛохина, кокосова горілка, ананас.\nVelvet у CHILI 🌶️\n\n#velvet #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Velvet\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a large wine glass filled with deep indigo-purple blueberry cocktail",
            "Electric blue curacao glow, swirling coconut vodka creating white marble patterns, "
            "pineapple juice layering at top in golden gradient, lime wheel perched on rim. "
            "Glass EXPLODES through frame with liquid wave.",
            "purple liquid droplets like gemstones, blueberries floating, pineapple fragments"
        )},
        {"style": "📸", "prompt": SREAL(
            "Velvet cocktail — large wine glass with indigo-purple blueberry and blue curacao drink, "
            "crushed ice, lime wheel garnish",
            f"{INTERIOR} terrace — on grey marble table",
            "Late afternoon golden hour sunlight, purple refractions on marble"
        )}
    ]},

    {"tema": "🍑 Peach Paradise — 149₴", "category": "cocktail",
     "caption": "Персик, цитрус і трохи магії ☀️\nЦе і є твій Peach Paradise.\nCHILI 🌶️\n\n#peachparadise #chiliodessa #літо #одеса",
     "refs_note": "📸 Фото коктейлю Peach Paradise\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall elegant highball glass with layered peach paradise cocktail",
            "Gradient from deep orange at bottom through peachy-gold to translucent top, "
            "peach juice and citrus swirling, fresh mint leaves floating. "
            "Glass PROPELS through frame in dynamic motion.",
            "peach juice streams, citrus droplets, mint leaf fragments, golden shimmer"
        )},
        {"style": "📸", "prompt": SREAL(
            "Peach Paradise cocktail — tall highball glass with peachy-orange layers, "
            "fresh mint leaves, golden liquid",
            f"{INTERIOR} — on wooden table",
            "Warm afternoon golden light, peachy tones enhanced"
        )}
    ]},

    {"tema": "🔴 Porn Star — 169₴", "category": "cocktail",
     "caption": "Глянцеві аромати, жага та розкіш 🔥\nPorn Star — коктейль без табу.\nCHILI 🌶️\n\n#pornstar #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Porn Star\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a sleek tall glass with vibrant passion fruit and champagne cocktail",
            "Golden passion fruit pulp suspended in sparkling champagne, "
            "vanilla orchid floated on surface, rim crusted with gold dust. "
            "Glass ERUPTS through frame in celebration.",
            "passion fruit pulp droplets, champagne bubbles ascending, orchid petals, gold dust spray"
        )},
        {"style": "📸", "prompt": SREAL(
            "Porn Star cocktail — tall glass with golden passion fruit liquid, vanilla orchid, "
            "champagne bubbles visible",
            f"{BAR} — glass glowing in bar light",
            "Warm amber backlighting highlighting passion fruit color"
        )}
    ]},

    {"tema": "❄️ Arctic — 133₴", "category": "cocktail",
     "caption": "Холодок, м'ята та льодяна свіжість ❄️\nArctic — для тих, хто любить контраст.\nCHILI 🌶️\n\n#arctic #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Arctic\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a chilled crystal glass with pale blue-white arctic cocktail",
            "Crystalline clear liquid with crushed ice visible throughout, fresh mint sprigs, "
            "frost coating outer glass surface creating icy elegance. "
            "Glass FREEZES and SHATTERS through frame.",
            "ice crystal shards sparkling, mint leaf fragments, frozen water droplets, cool blue light"
        )},
        {"style": "📸", "prompt": SREAL(
            "Arctic cocktail — crystal glass with pale icy liquid, crushed ice, fresh mint, "
            "frost on glass exterior",
            f"{BAR} — on iced surface",
            "Cool blue lighting with hint of frost effect"
        )}
    ]},

    {"tema": "✨ Solaris — 149₴", "category": "cocktail",
     "caption": "Сонячна енергія в коктейльному бокалі ✨\nSolaris — енергія літа.\nCHILI 🌶️\n\n#solaris #chiliodessa #літо #одеса",
     "refs_note": "📸 Фото коктейлю Solaris\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a radiant glass with golden-yellow tropical cocktail",
            "Brilliant yellow-orange liquid with tropical juices swirling, pineapple wedge garnish, "
            "hibiscus flower floating. Light seems to GLOW from within glass. "
            "Glass RADIATES through frame in sunny explosion.",
            "golden liquid rays, pineapple chunks tumbling, tropical flower petals, sun-like glow particles"
        )},
        {"style": "📸", "prompt": SREAL(
            "Solaris cocktail — glass with golden-yellow tropical liquid, pineapple wedge, "
            "hibiscus flower, glowing from within",
            f"{INTERIOR} — in bright sunlight",
            "Direct sunlight making cocktail glow golden"
        )}
    ]},

    {"tema": "💚 Маліка — 149₴", "category": "cocktail",
     "caption": "Малина, смородина та гірка напруга 💚\nМаліка — для справжніх.\nCHILI 🌶️\n\n#малика #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Маліка\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "an elegant glass with deep berry-red cocktail",
            "Rich crimson liquid with fresh raspberries and blackcurrants visible, "
            "mint leaf accent, sugar rim catching light. Glass BURSTS with berry essence.",
            "raspberry and blackcurrant fragments, sugar crystals sparkling, berry juice droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Маліка cocktail — elegant glass with deep berry-red liquid, fresh raspberries, "
            "blackcurrants, sugar rim",
            f"{INTERIOR} — on marble table",
            "Warm lighting emphasizing deep berry tones"
        )}
    ]},

    {"tema": "🍎 Apple Jack — 189₴", "category": "cocktail",
     "caption": "Яблуко, кориця та вибух смаку 🍎\nApple Jack — класика на новий лад.\nCHILI 🌶️\n\n#applejack #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Apple Jack\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall glass with amber-gold apple cocktail",
            "Clear amber liquid with apple slices visible, cinnamon stick garnish, "
            "caramel drizzle on glass interior. Glass SHATTERS with apple essence.",
            "apple slices tumbling, cinnamon dust swirling, caramel streams, amber liquid droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Apple Jack cocktail — tall glass with amber-gold apple liquid, apple slice garnish, "
            "cinnamon stick",
            f"{BAR} — warm bar lighting",
            "Warm amber tones highlighting apple and caramel"
        )}
    ]},

    {"tema": "💜 Віолетта — 159₴", "category": "cocktail",
     "caption": "Фіолетова магія, ліквер та чарівність 💜\nВіолетта — для романтичних вечорів.\nCHILI 🌶️\n\n#віолетта #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Віолетта\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "an exquisite coupe glass with violet-hued cocktail",
            "Magical violet liquid with layered purple tones, crystallized violet flowers as garnish, "
            "subtle golden shimmer catching light. Glass SHIMMERS with violet essence.",
            "violet flower petals floating, purple liquid sparkles, golden light effects"
        )},
        {"style": "📸", "prompt": SREAL(
            "Віолетта cocktail — coupe glass with violet hue, crystallized violet flowers, "
            "elegant presentation",
            f"{HALL} — on wooden table",
            "Soft warm light with subtle purple highlights"
        )}
    ]},

    # === МАТЧА ===

    {"tema": "🥥 Ice Coconut Matcha — 135₴", "category": "matcha",
     "caption": "Матча, кокос, лід — гавайський мікс ☀️\nСвіжість в кожному глотку.\nCHILI 🌶️\n\n#matcha #coconut #chiliodessa #льодо",
     "refs_note": "📸 Фото матчі з кокосом\n🔴 Логотип CHILI PNG\n🥥 Фото кокоса (референс)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall frosted glass with vibrant green matcha coconut water",
            "Brilliant jade-green matcha powder suspended in clear coconut water, "
            "crushed ice and coconut shavings visible, tropical coconut floated on top. "
            "Glass ERUPTS with tropical matcha energy.",
            "green matcha swirls, coconut shavings floating, ice shards sparkling, tropical essence"
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Coconut Matcha — tall glass with vibrant green matcha liquid, coconut water base, "
            "crushed ice, coconut flakes",
            f"{INTERIOR} — on terrace",
            "Bright tropical sunlight enhancing green matcha color"
        )}
    ]},

    {"tema": "🍍 Ice Pineapple Matcha — 135₴", "category": "matcha",
     "caption": "Матча та ананас — екзотичний дует 🍍\nЛітня свіжість.\nCHILI 🌶️\n\n#matcha #pineapple #chiliodessa #літо",
     "refs_note": "📸 Фото матчі з ананасом\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a vibrant glass with matcha pineapple blend",
            "Jade-green matcha swirled with golden pineapple juice, crushed ice, "
            "pineapple crown leaf garnish. "
            "Flavors BURST through frame in tropical explosion.",
            "matcha-pineapple swirls, pineapple chunks bouncing, ice crystals, tropical sunburst"
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Pineapple Matcha — tall glass with matcha-pineapple blend, crushed ice, "
            "pineapple garnish",
            f"{INTERIOR} — summer setting",
            "Golden tropical light bringing out both green and golden tones"
        )}
    ]},

    {"tema": "🍓 Ice Strawberry Matcha — 135₴", "category": "matcha",
     "caption": "Матча та полуниця — класичний дует 🍓\nСмак літа.\nCHILI 🌶️\n\n#matcha #strawberry #chiliodessa #літо",
     "refs_note": "📸 Фото матчі з полуницею\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a fresh glass with matcha strawberry blend",
            "Vibrant green matcha with pink strawberry layer visible, fresh strawberries floated, "
            "crushed ice, delicate presentation. "
            "Drink SPLASHES through frame with berry freshness.",
            "strawberry fragments flying, matcha swirls, ice shards, pink-green gradient spray"
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Strawberry Matcha — glass with matcha-strawberry blend, fresh strawberry slices, "
            "crushed ice",
            f"{INTERIOR} — on marble table",
            "Natural light highlighting pink and green complementary colors"
        )}
    ]},

    {"tema": "🍊 Ice Orange Matcha — 135₴", "category": "matcha",
     "caption": "Матча та апельсин — цитрусова енергія 🍊\nСвіжість від першого глотка.\nCHILI 🌶️\n\n#matcha #orange #chiliodessa #літо",
     "refs_note": "📸 Фото матчі з апельсином\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a bright glass with matcha orange fusion",
            "Luminous green matcha with golden orange juice swirled throughout, "
            "fresh orange wheel garnish, crushed ice visible. "
            "Drink RADIATES citrus energy through frame.",
            "orange slices tumbling, green-gold swirls, ice sparkles, citrus essence particles"
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Orange Matcha — glass with matcha-orange blend, orange wheel garnish, crushed ice",
            f"{INTERIOR} — bright morning setting",
            "Vibrant sunlight making orange and green pop"
        )}
    ]},

    {"tema": "🍠 Ice Raspberry Matcha — 135₴", "category": "matcha",
     "caption": "Матча та малина — ягідна магія 🍠\nСвіжість в кожному глотку.\nCHILI 🌶️\n\n#matcha #raspberry #chiliodessa #літо",
     "refs_note": "📸 Фото матчі з малиною\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a luminous glass with matcha raspberry creation",
            "Vibrant green matcha with deep rose-raspberry juice creating marble effect, "
            "fresh raspberries floated on surface, crushed ice, delicate crown of berries. "
            "Drink EXPLODES with berry essence through frame.",
            "raspberry fragments cascading, matcha-berry swirls, ice shards sparkling, berry dust"
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Raspberry Matcha — glass with matcha-raspberry blend, fresh raspberries, crushed ice",
            f"{INTERIOR} — elegant table setting",
            "Soft warm light emphasizing berry and green tones"
        )}
    ]},

    # === ЗАКУСКИ ===

    {"tema": "🧀 Сирне Антіпасті — 449₴", "category": "appetizer",
     "caption": "Селекція сирів від всього світу 🧀\nДля справжніх гурманів.\nCHILI 🌶️\n\n#антипасти #сир #chiliodessa #одеса",
     "refs_note": "📸 Фото сирної тарелки\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a luxurious cheese board with multiple varieties",
            "Artisan cheeses of different textures and colors — creamy whites, aged amber, blue veins, "
            "fresh nuts scattered, dried fruits placed artfully, honey drizzle. "
            "Board EXPANDS through frame in gourmet abundance.",
            "cheese fragments flying, walnut pieces, dried fruit scattered, honey streams"
        )},
        {"style": "📸", "prompt": SREAL(
            "Cheese Antipasti — wooden board with artisan selection, aged varieties, fresh nuts, "
            "dried fruits, honey",
            f"{HALL} — on rustic wooden table",
            "Warm overhead light highlighting cheese textures and colors"
        )}
    ]},

    {"tema": "🥩 М'ясне Антіпасті — 449₴", "category": "appetizer",
     "caption": "Селекція копченостей та деліцій 🥩\nДля шанувальників мяса.\nCHILI 🌶️\n\n#антипасти #мясо #chiliodessa #одеса",
     "refs_note": "📸 Фото м'ясної тарелки\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a gourmet meat platter with premium selections",
            "Thinly sliced prosciutto, spicy salami varieties, smoked sausages, "
            "pâté spreads, olives, pickles, fresh herbs. "
            "Platter UNFURLS through frame with cured excellence.",
            "meat slices flowing, olive rolling, herb particles, rich amber and red tones"
        )},
        {"style": "📸", "prompt": SREAL(
            "Meat Antipasti — slate board with cured meats selection, prosciutto, salami, "
            "olives, pickles",
            f"{HALL} — intimate dining setting",
            "Dramatic side-lighting bringing out meat colors and textures"
        )}
    ]},

    {"tema": "🐟 Тар-тар з лосося — 335₴", "category": "appetizer",
     "caption": "Сирий лосось, авокадо, в'ялені томати 🐟\nСвіжість в кожному шматку.\nCHILI 🌶️\n\n#тартар #лосось #chiliodessa #одеса",
     "refs_note": "📸 Фото тар-тару\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a plated tartare with pristine salmon",
            "Finely diced raw salmon in vibrant coral, creamy avocado green, dried tomato red, "
            "microgreens garnish, citrus oil glistening. "
            "Plate EMERGES through frame with raw elegance.",
            "salmon dice floating, avocado green swirls, tomato fragments, citrus oil droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Salmon Tartare — white plate with finely diced salmon, avocado, dried tomatoes, "
            "microgreens",
            f"{HALL} — elegant plating",
            "Cool neutral light enhancing salmon coral and avocado green"
        )}
    ]},

    # === БІЛЬШЕ КАТЕГОРІЙ МОЖНА ДОДАТИ АНАЛОГІЧНО ===

    # === САЛАТИ (вибір топ позицій) ===

    {"tema": "🦐 Салат з креветками — 329₴", "category": "salad",
     "caption": "Король креветок, авокадо, в'ялені томати 🦐\nСвіжість морського бризу.\nCHILI 🌶️\n\n#салат #креветки #chiliodessa #одеса",
     "refs_note": "📸 Фото салату з креветками\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a gorgeous shrimp salad composition",
            "Plump pink shrimp arranged on fresh greens, creamy avocado slices, dried tomato accents, "
            "microgreens scattered. Salad BURSTS through frame with oceanic freshness.",
            "shrimp tumbling, avocado slices, greens floating, citrus droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Shrimp Salad — white plate with fresh greens, plump shrimp, avocado, dried tomatoes",
            f"{INTERIOR} — bright table setting",
            "Natural light enhancing shrimp pink and greens"
        )}
    ]},

    # === СУПИ (вибір) ===

    {"tema": "🍲 Борщ — від 81₴", "category": "soup",
     "caption": "Класичний борщ з сирною маслинкою 🍲\nВкус 'вдома'.\nCHILI 🌶️\n\n#борщ #суп #chiliodessa #одеса",
     "refs_note": "📸 Фото борщу\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a steaming bowl of beet borscht",
            "Deep crimson soup with creamy sour cream swirl, beet chunks visible, dill garnish. "
            "Bowl RADIATES warmth through frame with comfort essence.",
            "steam wisps rising, sour cream spirals, beet pieces, dill leaf floating"
        )},
        {"style": "📸", "prompt": SREAL(
            "Borscht — ceramic bowl with deep crimson soup, sour cream swirl, fresh dill",
            f"{HALL} — warm table setting",
            "Soft warm light creating cozy atmosphere"
        )}
    ]},

    # === ПАСТА ===

    {"tema": "🍤 Паста з креветками — 249₴", "category": "pasta",
     "caption": "Крем-соус, креветки, в'ялені томати 🍤\nІтальянська класика.\nCHILI 🌶️\n\n#паста #креветки #chiliodessa #одеса",
     "refs_note": "📸 Фото пасти\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a luxurious pasta dish with shrimp",
            "Al dente pasta coated in creamy sauce, plump shrimp arranged on top, "
            "dried tomato accents, fresh basil. Plate TWIRLS through frame with Italian elegance.",
            "pasta strands swirling, shrimp tumbling, basil leaves floating, creamy droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Pasta with Shrimp — white plate with al dente pasta, creamy sauce, shrimp, "
            "dried tomatoes, fresh basil",
            f"{HALL} — elegant pasta setting",
            "Warm lighting bringing out shrimp pink and tomato red"
        )}
    ]},

    # === ЛАВАШІ ===

    {"tema": "🌯 Лаваш з креветкою — 275₴", "category": "lavash",
     "caption": "Креветка, авокадо, в'ялені томати в тонкому лавашу 🌯\nСвіжість у кожному шарі.\nCHILI 🌶️\n\n#лаваш #креветка #chiliodessa #одеса",
     "refs_note": "📸 Фото лавашу\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a fresh lavash wrap with shrimp filling",
            "Thin golden flatbread wrapped around fresh shrimp, creamy avocado, dried tomatoes, "
            "fresh herbs, sides visible. Wrap UNFURLS through frame.",
            "lavash strands separating, shrimp visible, avocado green, herb particles"
        )},
        {"style": "📸", "prompt": SREAL(
            "Shrimp Lavash — flatbread wrap with shrimp filling, avocado, dried tomatoes, herbs",
            f"{INTERIOR} — casual dining",
            "Bright light highlighting golden flatbread"
        )}
    ]},

    # === ОСНОВНІ СТРАВИ (додати ключові) ===

    {"tema": "🥩 Пеппер Стейк — 495₴", "category": "food",
     "caption": "Стейк з грибним соусом і картоплею фрі 🥩\nДля справжніх любителів м'яса.\nCHILI 🌶️\n\n#стейк #мясо #chiliodessa #одеса",
     "refs_note": "📸 Фото стейку\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a prime pepper steak with sauce",
            "Perfectly cooked steak with peppercorn crust, rich brown mushroom sauce pooling, "
            "golden crispy fries arranged, fresh herbs. Sauce POURS through frame dramatically.",
            "sauce rivers flowing, peppercorns sparkling, fries golden, steam rising"
        )},
        {"style": "📸", "prompt": SREAL(
            "Pepper Steak — plated steak with mushroom sauce, crispy fries, fresh herbs",
            f"{HALL} — premium dining",
            "Dramatic lighting creating elegant steak presentation"
        )}
    ]},

    {"tema": "🐟 Лосось з пюре — 373₴", "category": "food",
     "caption": "Свіжий лосось, пармезанове пюре 🐟\nДелікатність на тарілці.\nCHILI 🌶️\n\n#лосось #риба #chiliodessa #одеса",
     "refs_note": "📸 Фото лосося\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a fresh salmon fillet with parmesan puree",
            "Perfectly seared salmon with golden crust, creamy parmesan puree base, "
            "microgreens garnish, lemon wedge. Salmon GLIDES through frame with finesse.",
            "salmon crust sparkling, puree swirls, microgreens floating, lemon droplets"
        )},
        {"style": "📸", "prompt": SREAL(
            "Salmon with Parmesan Puree — seared salmon fillet, creamy puree, microgreens",
            f"{HALL} — elegant plating",
            "Soft warm light highlighting salmon color"
        )}
    ]},

    # === АТМОСФЕРА ===

    {"tema": "🌅 Тераса CHILI", "category": "vibe",
     "caption": "Одеса, літо, тераса 🌿\nДзвони — забронюємо.\n📞 +380 66 440 16 88\nCHILI 🌶️\n\n#тераса #chiliodessa #літоодеса #одеса",
     "refs_note": "📸 Фото тераси CHILI (3-5 ракурсів)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "CHILI restaurant summer terrace scene",
            "Coral-tomato-red chairs around grey marble tables, dark canopy with warm lights, "
            "lush greenery. Scene ZOOMS toward viewer as terrace EXPANDS through frame.",
            "chair fragments spinning, marble pieces, green leaf confetti, light flares"
        )},
        {"style": "📸", "prompt": SREAL(
            "CHILI terrace — coral-red chairs, marble tables, dark canopy, green foliage",
            f"CHILI terrace {INTERIOR}",
            "Golden late afternoon sunlight creating dramatic shadow play"
        )}
    ]},

    {"tema": "💡 Люстра з перців", "category": "vibe",
     "caption": "Наша люстра — не просто світло 🌶️\nЦе характер CHILI.\n\n#chiliodessa #інтер'єр #design #одеса",
     "refs_note": "📸 Фото люстри з перців CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "the iconic CHILI restaurant chili pepper chandelier",
            "Hundreds of dark glossy ceramic chili peppers in three tiers, warm amber glow, "
            "green trailing vines cascading. PEPPERS RAIN DOWN through frame.",
            "ceramic peppers tumbling, amber light, green vine fragments"
        )},
        {"style": "📸", "prompt": SREAL(
            "Pepper Chandelier — hundreds of burgundy ceramic peppers, amber backlighting, "
            "green vines",
            f"{HALL} — looking straight up",
            "Warm amber backlight creating dramatic silhouettes"
        )}
    ]},
]

# ============================
# ДЕНЬ ТИЖНЯ
# ============================
DAY_CATEGORIES = {
    0: ["food", "appetizer"],
    1: ["matcha", "salad"],
    2: ["cocktail", "soup"],
    3: ["food", "lavash"],
    4: ["cocktail", "pasta"],
    5: ["cocktail", "vibe", "food"],
    6: ["vibe", "breakfast"] if any(p["category"] == "breakfast" for p in PROMPTS) else ["vibe", "food"],
}
DAY_NAMES_UK = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

# ============================
# ІСТОРІЯ
# ============================
def load_history():
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"sent": [], "weekly_stats": {}}

def save_history(h):
    with open(HISTORY_FILE, "w") as f:
        json.dump(h, f)

def record_sent(tema):
    h = load_history()
    h["sent"].append({"tema": tema, "time": datetime.datetime.now(KYIV).isoformat()})
    h["sent"] = h["sent"][-50:]
    wk = datetime.datetime.now(KYIV).strftime("%Y-W%U")
    if wk not in h["weekly_stats"]:
        h["weekly_stats"][wk] = []
    h["weekly_stats"][wk].append(tema)
    save_history(h)

def get_sent_this_week():
    h = load_history()
    wk = datetime.datetime.now(KYIV).strftime("%Y-W%U")
    return h["weekly_stats"].get(wk, [])

def get_item_for_today():
    wd = datetime.datetime.now(KYIV).weekday()
    cats = DAY_CATEGORIES.get(wd, ["cocktail", "food"])
    cat = random.choice(cats)
    pool = [p for p in PROMPTS if p["category"] == cat]
    if not pool:
        pool = PROMPTS
    sent = get_sent_this_week()
    fresh = [p for p in pool if p["tema"] not in sent]
    if fresh:
        pool = fresh
    return random.choice(pool)

# ============================
# КЛАВІАТУРА
# ============================
def build_menu(idx=None):
    btns = [
        [InlineKeyboardButton("🎲 Рандом промт", callback_data="mix")],
        [
            InlineKeyboardButton("🎆 3D стиль", callback_data="style_3d"),
            InlineKeyboardButton("📸 Кінематограф", callback_data="style_real"),
        ],
    ]
    if idx is not None:
        btns.append([InlineKeyboardButton("🔄 Інший стиль цієї теми", callback_data=f"flip_{idx}")])
    btns.append([
        InlineKeyboardButton("🌶️ Теми", callback_data="topics"),
        InlineKeyboardButton("📊 Статистика", callback_data="stats"),
    ])
    return InlineKeyboardMarkup(btns)

# ============================
# ФОРМАТ
# ============================
def format_prompt(item, variant):
    icon = "🎆 3D Instagram рамка" if variant["style"] == "3D" else "📸 Кінематографічний"
    idx = PROMPTS.index(item)
    return (
        f"🌶️ CHILI — Сторис\n\n"
        f"📌 {item['tema']}\n"
        f"🎨 {icon}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 Промт для Google Flow:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{variant['prompt']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✍️ Підпис до поста:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{item['caption']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🖼️ Референси для Flow:\n"
        f"{item['refs_note']}\n\n"
        f"✅ Додай референси → вставляй → генеруй!"
    ), idx

# ============================
# ХЕНДЛЕРИ
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌶️ CHILI Stories Bot\n\n"
        "Щодня о 10:00 — промт під настрій дня.\n"
        "Деталізовані промти під реальний візуал CHILI.\n\n"
        "Натискай 👇",
        reply_markup=build_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    d = query.data

    if d == "mix":
        item = get_item_for_today()
        variant = random.choice(item["variants"])
        text, idx = format_prompt(item, variant)
        record_sent(item["tema"])
        await query.message.reply_text(text, reply_markup=build_menu(idx))

    elif d == "style_3d":
        item = get_item_for_today()
        variant = next((v for v in item["variants"] if v["style"] == "3D"), item["variants"][0])
        text, idx = format_prompt(item, variant)
        record_sent(item["tema"])
        await query.message.reply_text(text, reply_markup=build_menu(idx))

    elif d == "style_real":
        item = get_item_for_today()
        variant = next((v for v in item["variants"] if v["style"] == "📸"), item["variants"][-1])
        text, idx = format_prompt(item, variant)
        record_sent(item["tema"])
        await query.message.reply_text(text, reply_markup=build_menu(idx))

    elif d.startswith("flip_"):
        idx = int(d.split("_")[1])
        item = PROMPTS[idx]
        curr = query.message.text or ""
        if "3D Instagram" in curr:
            variant = next((v for v in item["variants"] if v["style"] == "📸"), item["variants"][-1])
        else:
            variant = next((v for v in item["variants"] if v["style"] == "3D"), item["variants"][0])
        text, idx = format_prompt(item, variant)
        await query.message.reply_text(text, reply_markup=build_menu(idx))

    elif d == "topics":
        wd = datetime.datetime.now(KYIV).weekday()
        today_cats = DAY_CATEGORIES.get(wd, [])
        sent = get_sent_this_week()
        lines = [
            f"{'⭐' if p['category'] in today_cats else '•'} {p['tema']}{'  ✓' if p['tema'] in sent else ''}"
            for p in PROMPTS
        ]
        await query.message.reply_text(
            f"🌶️ Всі теми ({len(PROMPTS)}):\n⭐ = сьогодні · ✓ = вже цього тижня\n\n" + "\n".join(lines),
            reply_markup=build_menu()
        )

    elif d == "stats":
        h = load_history()
        sent_week = get_sent_this_week()
        total = len(h.get("sent", []))
        cats = {}
        for rec in h.get("sent", []):
            for p in PROMPTS:
                if p["tema"] == rec["tema"]:
                    cats[p["category"]] = cats.get(p["category"], 0) + 1
        labels = {"cocktail": "🍹 Коктейлі", "matcha": "🍵 Матча", "food": "🍣 Їжа",
                  "appetizer": "🥗 Закуски", "salad": "🥗 Салати", "soup": "🍲 Супи",
                  "pasta": "🍝 Паста", "lavash": "🌯 Лаваш", "vibe": "🌅 Атмосфера"}
        cats_text = "\n".join([f"  {labels.get(k,k)}: {v}" for k, v in cats.items() if v > 0]) or "  Поки немає"
        week_text = "\n".join([f"  • {t}" for t in sent_week]) or "  Ще не було сторис"
        await query.message.reply_text(
            f"📊 Статистика CHILI Bot\n\n"
            f"📅 Цього тижня ({len(sent_week)}):\n{week_text}\n\n"
            f"📈 Всього: {total}\n\n"
            f"🗂️ По категоріях:\n{cats_text}",
            reply_markup=build_menu()
        )

async def daily_sender(app):
    last_weekly = None
    while True:
        now = datetime.datetime.now(KYIV)
        if now.weekday() == 6 and now.hour == 20 and last_weekly != now.date():
            last_weekly = now.date()
            sent_week = get_sent_this_week()
            if sent_week:
                report = (
                    f"📊 Підсумок тижня CHILI\n\n"
                    f"Цього тижня {len(sent_week)} сторис:\n"
                    + "\n".join([f"  • {t}" for t in sent_week])
                    + "\n\nНовий тиждень — нові теми! 🌶️"
                )
                await app.bot.send_message(chat_id=CHAT_ID, text=report, reply_markup=build_menu())

        target = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now >= target:
            target += datetime.timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())

        item = get_item_for_today()
        variant = random.choice(item["variants"])
        text, idx = format_prompt(item, variant)
        record_sent(item["tema"])
        await app.bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=build_menu(idx))

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    asyncio.create_task(daily_sender(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
