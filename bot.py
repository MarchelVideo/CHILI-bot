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
     "refs_note": "📸 Фото готового коктейлю Марчелло\n🔴 Логотип CHILI PNG\n🪨 Фото мармурового столу (текстура)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a premium crystal rocks glass containing deep amber bourbon",
            "Warm golden bourbon liquid with maraschino and amaretto swirling, large crystal-clear ice cube center, "
            "twisted orange peel garnish draped over glass rim, condensation droplets on crystal facets. "
            "The glass SHATTERS through the Instagram frame, liquid splash arcing dramatically outside. ",
            "amber liquid droplets mid-air, spinning ice shards, orange zest curling upward, "
            "golden whiskey mist catching the light, scattered cocktail cherries",
            "Frame tilted at 15-degree angle for dynamic composition. Close-up hero shot."
        )},
        {"style": "📸", "prompt": SREAL(
            "Марчелло cocktail — crystal rocks glass with deep amber bourbon, maraschino and amaretto, "
            "single oversized hand-cut ice cube, elegant twisted orange peel garnish, "
            "tiny condensation beads on glass surface",
            f"{BAR} — glass placed directly on dark marble bar counter, "
            "blurred green bottle silhouettes and hanging crystal glasses in background bokeh",
            "Single dramatic spotlight from above-left creating long shadow, "
            "warm amber tones matching the bourbon color, deep shadows in corners, "
            "golden rim light on glass edge catching bar neon",
            "Shot from 45-degree angle, glass fills lower two-thirds of frame."
        )}
    ]},

    {"tema": "🫐 Velvet — 149₴", "category": "cocktail",
     "caption": "Не просто коктейль — це настрій 💜\nЛохина, кокосова горілка, ананас.\nVelvet у CHILI 🌶️\n\n#velvet #chiliodessa #коктейлі #одеса #cocktail",
     "refs_note": "📸 Фото коктейлю Velvet (фіолетовий у винному бокалі)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a large wine glass filled with deep indigo-purple blueberry cocktail",
            "Electric blue curacao glow deep in the liquid, swirling coconut vodka creating white marble patterns, "
            "pineapple juice layering at top in golden gradient, single lime wheel perched on rim, "
            "crushed ice visible through glass walls. Glass EXPLODES through frame with liquid wave. ",
            "purple liquid droplets like gemstones, blueberries floating mid-air, "
            "pineapple chunk fragments, coconut shavings spinning, blue curacao mist",
            "Blue-to-purple color temperature gradient on lighting. Ultra-saturated jewel tones."
        )},
        {"style": "📸", "prompt": SREAL(
            "Velvet cocktail — large elegant wine glass with deep indigo-purple blueberry and blue curacao drink, "
            "crushed ice visible through glass, lime wheel garnish, "
            "cold condensation on outer glass surface creating mist",
            f"{INTERIOR} terrace — glass on grey marble table, "
            "coral-red chairs blurred in background bokeh, green foliage framing sides",
            "Late afternoon golden hour sunlight hitting glass from side, "
            "creating purple refractions on marble table surface, "
            "deep contrast between purple drink and warm amber outdoor light",
            "Low angle looking slightly up at glass, city of Odessa softly blurred behind."
        )}
    ]},

    {"tema": "🍑 Peach Paradise — 149₴", "category": "cocktail",
     "caption": "Персик, цитрус і трохи магії ☀️\nЦе і є твій Peach Paradise.\nCHILI 🌶️\n\n#peachparadise #chiliodessa #літо #одеса",
     "refs_note": "📸 Фото коктейлю Peach Paradise\n🔴 Логотип CHILI PNG\n🍑 Фото свіжого персику (референс кольору)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall elegant highball glass with layered peach paradise cocktail",
            "Gradient from deep orange at bottom through peachy-gold to translucent top, "
            "peach tincture swirling creating sunset marble patterns, citrus liqueur foam forming on surface, "
            "fresh half-peach slice balanced on rim showing juicy orange flesh. "
            "Liquid cascades out of frame in slow-motion wave. ",
            "peach slice fragments mid-flight, citrus peel spirals, golden liquid droplets, "
            "peach syrup threads like ribbons in air, citrus zest mist",
            "Warm sunset color temperature — orange and gold dominate. Summery and energetic composition."
        )},
        {"style": "📸", "prompt": SREAL(
            "Peach Paradise cocktail — tall glass with beautiful peach-orange gradient drink, "
            "fresh peach slice garnish on rim showing warm flesh tones, "
            "peach syrup pooling at base creating warm amber depth, "
            "condensation rivulets running down cold glass",
            f"CHILI restaurant terrace — placed on grey marble table, "
            "coral-red chair partially visible at edge, Odessa street greenery soft bokeh background",
            "Golden morning light at 10am hitting glass directly, "
            "orange and gold light refracting through liquid onto marble surface, "
            "peach tones in drink echoing the warm ambient light",
            "Portrait orientation with peach halves artfully arranged beside glass as props."
        )}
    ]},

    {"tema": "🍹 Chili Porn Star — 169₴", "category": "cocktail",
     "caption": "Класика в нашому баченні 🍾\nЛікер маракуйї, ванільна горілка, просеко.\nChili Porn Star у CHILI 🌶️\n\n#pornstar #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Porn Star (купе бокал з піною)\n🔴 Логотип CHILI PNG\n✨ Фото бару CHILI (фон)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a stunning coupe glass with Chili Porn Star cocktail",
            "Champagne-gold vanilla vodka base shimmering with prosecco bubbles rising, "
            "thick luxurious passionfruit foam crown on top with slight golden shimmer, "
            "halved fresh passionfruit resting on foam showing jewel-like seeds. "
            "Prosecco bubbles stream upward through liquid. Glass tilts as it CRASHES through frame. ",
            "prosecco bubbles floating like pearls, passionfruit seeds mid-air, "
            "golden foam wisps, champagne mist, tiny star-shaped light flares",
            "Premium champagne bar aesthetic. Gold and cream color palette. Celebration energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "Chili Porn Star cocktail — elegant wide coupe glass, "
            "champagne-gold prosecco base with tiny rising bubbles, "
            "thick airy passionfruit foam crown, "
            "fresh passionfruit half placed beside glass showing yellow seeds",
            f"{BAR} — placed on dark glossy bar surface, "
            "green bar front panels glowing amber in background, "
            "crystal glasses hanging in blurred bokeh above",
            "Narrow spotlight from directly above creating halo effect on foam, "
            "gold reflections in dark bar surface like mirror, "
            "deep moody shadows contrasting with bright foam highlight",
            "Tightly cropped, foam and glass fill most of frame. Intimate luxury feeling."
        )}
    ]},

    {"tema": "❄️ Arctic — 133₴", "category": "cocktail",
     "caption": "Холодний. Чистий. Освіжаючий ❄️\nМ'ятна горілка та крига.\nArctic у CHILI 🌶️\n\n#arctic #chiliodessa #коктейлі #літо",
     "refs_note": "📸 Фото коктейлю Arctic (прозорий, свіжа м'ята)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a crystal-clear tall glass filled with Arctic mint cocktail",
            "Perfectly transparent mint vodka with zero color, large hand-cut crystal ice cubes stacked, "
            "fresh mint sprig erupting from top like a fountain of green, "
            "heavy condensation fog rolling off the ice-cold glass. "
            "Frozen ice crystals EXPLODE outward through Instagram frame like arctic blast. ",
            "ice crystals shattering like glass, mint leaves spinning in cold mist, "
            "frozen water droplets, condensation vapor cloud, "
            "tiny snowflake-like ice particles catching light",
            "Cool blue-white color temperature. Clean, sharp, minimal color palette. Arctic energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "Arctic cocktail — tall pristine glass, water-clear mint vodka with sugar syrup, "
            "three large hand-cut ice cubes stacked with perfect clarity, "
            "fresh mint sprig as garnish, heavy cold fog forming around glass base, "
            "extreme condensation on glass exterior",
            f"CHILI restaurant — placed on grey marble table near window, "
            "morning clean white light streaming in, coral-red chair softly blurred at edge",
            "Clean bright natural morning light — cool temperature white balance, "
            "condensation droplets catching light like diamonds, "
            "green mint reflecting in glass surface, "
            "pure whites and crystal clarity dominate",
            "Crisp sharp focus on ice and mint. Supremely clean and refreshing visual."
        )}
    ]},

    {"tema": "🌞 Solaris — 149₴", "category": "cocktail",
     "caption": "Ром, бренді, манго та апельсин ☀️\nСмак одеського сонця.\nSolaris у CHILI 🌶️\n\n#solaris #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Solaris (золотисто-жовтогарячий)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall hurricane glass filled with golden tropical Solaris cocktail",
            "Deep golden rum and brandy base, vibrant mango juice creating sunset gradient, "
            "orange juice bright layer on top, almond syrup threads like caramel ribbons, "
            "salted caramel rim sparkling, fresh orange wheel garnish. "
            "Liquid SURGES through frame like a tropical wave. ",
            "mango chunks mid-air, orange wheel spinning, golden liquid arcs, "
            "caramel syrup threads, tropical fruit pulp particles, "
            "sun-like light flares in gold tones",
            "Tropical golden hour palette — deep oranges, golds, warm ambers. Summer celebration."
        )},
        {"style": "📸", "prompt": SREAL(
            "Solaris cocktail — tall glass with stunning golden-to-orange gradient, "
            "rum and brandy depth at base darkening to bright orange-mango top, "
            "fresh orange wheel garnish on rim showing vivid citrus segments, "
            "tiny gold rim detail catching light",
            f"{INTERIOR} terrace — placed on marble table, "
            "late afternoon golden sunlight streaming from right side, "
            "Odessa green trees blurred in background",
            "Warm golden hour direct sunlight hitting glass from the side, "
            "drink glowing like stained glass window, "
            "deep amber and orange tones suffusing entire frame, "
            "lens flare kissing upper corner",
            "Glass glowing against moody dark background — sunburst effect."
        )}
    ]},

    {"tema": "🍓 Маліка — 149₴", "category": "cocktail",
     "caption": "Малинова горілка, полунична піна 🍓\nНіжно. Яскраво. Маліка.\nCHILI 🌶️\n\n#malika #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Маліка (рожевий купе)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "an elegant coupe glass with Маліка raspberry cocktail",
            "Deep crimson-pink raspberry vodka base with strawberry liqueur depth, "
            "coconut syrup creating pearl-white swirls through deep pink, "
            "thick airy strawberry-pink foam crown with tiny air bubbles catching light, "
            "fresh raspberry cluster balanced on foam surface. "
            "Foam OVERFLOWS through frame edge in dreamy cascade. ",
            "raspberries and strawberry halves mid-air, pink foam wisps floating, "
            "crimson liquid droplets like jewels, "
            "soft pink mist, berry leaves spinning gently",
            "Romantic deep rose and crimson palette. Feminine luxury energy. Soft diffused glow."
        )},
        {"style": "📸", "prompt": SREAL(
            "Маліка cocktail — coupe glass with deep crimson-pink raspberry drink, "
            "beautiful strawberry foam crown with natural pink tones, "
            "three fresh raspberries on cocktail pick resting on foam, "
            "coconut syrup creating marbled white patterns through red base",
            f"{BAR} — on marble counter with two additional glasses blurred behind, "
            "warm bar neon reflecting in glossy counter surface as soft pink glow",
            "Warm romantic side-light from bar backlighting, "
            "pink and red tones blooming softly, "
            "foam catching highlight creating luminous crown effect, "
            "deep moody bar atmosphere contrasting with bright pink drink",
            "Glass centered in lower third. Lush berry styling around base."
        )}
    ]},

    {"tema": "🍎 Apple Jack — 189₴", "category": "cocktail",
     "caption": "Яблуко, просеко і трохи магії 🍎\nApple Jack — для тих хто любить несподіванки.\nCHILI 🌶️\n\n#applejack #chiliodessa #коктейлі #одеса",
     "refs_note": "📸 Фото коктейлю Apple Jack (зелено-золотий з піною)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a large wine glass with Apple Jack cocktail",
            "Pale apple-green champagne base from Apple Jack whiskey, "
            "prosecco bubbles rising continuously in streams, "
            "white albumin foam crown with crisp apple-green tint, "
            "thin apple fan garnish on rim showing translucent green flesh. "
            "PROSECCO BUBBLES ERUPT through frame like champagne pop. ",
            "prosecco bubbles in streams, thin apple slices orbiting glass, "
            "white foam fragments floating like snow, "
            "apple seed and stem details, green apple mist",
            "Fresh apple-green and champagne gold palette. Celebratory and crisp energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "Apple Jack cocktail — large wine glass with pale apple-green sparkling base, "
            "continuous prosecco bubbles streaming upward, "
            "white albumin foam with fresh apple fragrance, "
            "thin transparent apple fan garnish on rim, "
            "glass stem catching and refracting light into spectrum",
            f"{INTERIOR} — placed near window, "
            "diffused bright daylight from large CHILI windows with plants visible outside, "
            "oak wooden table surface providing warm contrast",
            "Bright clean diffused window light from left, "
            "bubbles and foam catching highlights, "
            "fresh apple-green tones against warm wood table, "
            "airy and refreshing color temperature",
            "Wide enough to see full glass with apple prop beside it on wooden table."
        )}
    ]},

    # === ICE MATCHA ===

    {"tema": "🥥 Ice Coconut Matcha — 135₴", "category": "matcha",
     "caption": "Кокосова вода, молоко та матча 🥥\nПочни день правильно.\nCHILI 🌶️\n\n#matcha #icematcha #coconut #chiliodessa #одеса",
     "refs_note": "📸 Фото Ice Coconut Matcha (шари у склянці)\n🔴 Логотип CHILI PNG\n🌴 Тропічне листя (референс атмосфери)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall ribbed glass cylinder with Ice Coconut Matcha drink",
            "Three distinct visible layers — coconut water base (clear with slight blue), "
            "vivid emerald matcha middle layer, "
            "thick white coconut milk foam crown with matcha dusting on top, "
            "large clear ice cubes stacked inside. "
            "Glass TILTS and layers SEPARATE as it bursts through frame. ",
            "coconut shavings spiraling outward, matcha powder cloud in emerald green, "
            "ice cubes mid-air showing perfect clarity, "
            "coconut milk droplets, tropical leaf fragments",
            "Clean tropical aesthetic — emerald green, white, and coconut cream palette."
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Coconut Matcha — tall ribbed cylindrical glass showing three perfect layers: "
            "bottom coconut water layer, vivid green matcha center, "
            "thick white coconut milk foam top with matcha powder dusting, "
            "large clear ice cubes creating translucent towers inside glass",
            f"{INTERIOR} terrace — placed on marble table, "
            "large tropical monstera leaf partially framing right side of shot, "
            "Odessa summer light and street greenery in soft background",
            "Bright direct summer sunlight creating sharp graphic shadows from glass onto marble, "
            "emerald green layer glowing like backlit stained glass, "
            "clean white foam top luminous against warm background",
            "Overhead 45-degree angle showing layer beauty. Coconut halves as props beside glass."
        )}
    ]},

    {"tema": "🍍 Ice Pineapple Matcha — 135₴", "category": "matcha",
     "caption": "Матча, ананас та синій чай Анчан 🍍\nТри шари — один смак.\nCHILI 🌶️\n\n#matcha #pineapple #icematcha #chiliodessa",
     "refs_note": "📸 Фото Ice Pineapple Matcha (синьо-зелено-жовтий градієнт)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall glass with Ice Pineapple Matcha — the most colorful drink",
            "Stunning three-color gradient: pineapple juice gold at base, "
            "violet-blue butterfly pea Anchan tea in middle creating electric color shift, "
            "vivid emerald matcha top layer, passionfruit cordial creating purple-to-green gradient effect. "
            "LIQUID RAINBOW cascades out of frame in arcing streams. ",
            "pineapple chunks tumbling mid-air, butterfly pea flowers floating like purple stars, "
            "matcha powder cloud in neon green, yellow pineapple juice droplets, "
            "blue-to-green gradient mist",
            "Maximum color saturation — electric blue, neon green, sunshine yellow. Vibrant summer energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Pineapple Matcha — extraordinary layered drink: "
            "sunshine yellow pineapple base, electric violet-blue Anchan middle layer, "
            "vivid emerald matcha crown, "
            "the color transition from yellow through purple to green creating sunset gradient effect, "
            "pineapple wedge garnish on rim",
            f"{INTERIOR} terrace marble table, "
            "bright Odessa summer sky visible beyond terrace canopy, "
            "coral-red chair as blurred color accent in background",
            "Strong direct midday sunlight from above-right, "
            "colors in glass saturated to maximum — electric blue glowing, "
            "green matcha vivid against bright background, "
            "graphic shadow pattern on white marble from condensation ring",
            "Low side angle to show the spectacular gradient column inside glass."
        )}
    ]},

    {"tema": "🍓 Ice Strawberry Matcha — 135₴", "category": "matcha",
     "caption": "Полунична кокосова вода і матча 🍓\nСвіжість у кожному ковтку.\nCHILI 🌶️\n\n#strawberrymatcha #chiliodessa #одеса #matcha",
     "refs_note": "📸 Фото Ice Strawberry Matcha (рожево-зелений)\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a ribbed tall glass with Ice Strawberry Matcha",
            "Deep strawberry-pink base from strawberry-infused coconut water, "
            "bright emerald matcha layer in middle creating pink-to-green contrast, "
            "thick coconut cream foam top with matcha powder heart design, "
            "fresh whole strawberry pierced on glass rim. "
            "PINK AND GREEN LIQUID SPIRAL outward through frame. ",
            "whole strawberries and cut halves orbiting glass, "
            "matcha powder explosion in green, "
            "pink coconut water droplets like rose petals, "
            "white foam ribbons, strawberry seeds catching light",
            "Romantic pink and fresh green color story. Sweet summer berry energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Strawberry Matcha — ribbed glass with beautiful pink-green contrast: "
            "strawberry pink coconut water base glowing warm, "
            "vivid green matcha layer above creating graphic color divide, "
            "thick white coconut foam top, "
            "fresh halved strawberry on rim showing ruby-red flesh and seeds",
            f"{INTERIOR} terrace, marble table with coral-red chairs creating pink-red tones in background bokeh, "
            "soft natural light with warm summer feel",
            "Soft warm afternoon light from left side, "
            "strawberry pink tones warmed by golden ambient light, "
            "green matcha bright and vivid, "
            "foam crown softly glowing, "
            "overall dreamy warm summer palette",
            "Fresh cut strawberries scattered on marble as styling props beside glass."
        )}
    ]},

    {"tema": "🍊 Ice Orange Matcha — 135₴", "category": "matcha",
     "caption": "Апельсиновий фреш і матча 🍊\nПросто. Смачно. Свіжо.\nCHILI 🌶️\n\n#orangematcha #chiliodessa #одеса #matcha",
     "refs_note": "📸 Фото Ice Orange Matcha\n🔴 Логотип CHILI PNG\n🍊 Свіжий апельсин (props)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "a tall glass with Ice Orange Matcha drink",
            "Vivid fresh-squeezed orange juice base with deep orange color and visible pulp texture, "
            "bright emerald matcha layer sitting on top creating hard orange-green color boundary, "
            "the boundary between layers creating a graphic line of color. "
            "LAYERS POUR OUT of frame as FRESH ORANGE SPLASH erupts. ",
            "orange juice splash with visible pulp droplets, "
            "matcha powder green cloud, orange segments mid-flight, "
            "ice cubes with orange tones, citrus zest spirals",
            "Bold graphic orange and green contrast — maximum citrus energy. Morning freshness."
        )},
        {"style": "📸", "prompt": SREAL(
            "Ice Orange Matcha — graphic two-tone drink: "
            "deep vibrant orange fresh-squeezed juice base with visible pulp, "
            "bright emerald matcha sitting on top creating striking color divide, "
            "large clear ice cubes, "
            "half orange wheel garnish on rim showing vivid orange flesh",
            f"{INTERIOR} terrace — bright morning light, "
            "placed on white marble with sharp morning shadows, "
            "street greenery creating natural green tones in distant bokeh",
            "Sharp bright morning light from directly above-right, "
            "orange juice glowing like fire from backlighting, "
            "clean graphic composition with hard color divisions, "
            "fresh squeezed orange half beside glass on marble",
            "High contrast, graphic, punchy. Fresh orange beside glass as prop."
        )}
    ]},

    # === РОЛИ ===

    {"tema": "🍣 Запечені роли", "category": "food",
     "caption": "Лосось. Соус. Ідеально 🍣\nЗапечені роли у CHILI.\n\n#роли #суші #chiliodessa #одеса #sushi",
     "refs_note": "📸 Фото запечених ролів з меню CHILI\n🔴 Логотип CHILI PNG\n🍱 Темна керамічна тарілка (props)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium baked salmon sushi rolls on dark slate ceramic serving plate",
            "Six perfectly formed rolls topped with torched salmon — char marks visible, "
            "cream cheese and spicy mayo sauce artfully drizzled in thin lines, "
            "fresh microgreens sprouting from between rolls like a garden, "
            "pink pickled ginger rose beside rolls, wasabi green quenelle. "
            "Plate TILTS dramatically with rolls TUMBLING through frame. ",
            "individual rice grains mid-air, salmon pieces spiraling outward, "
            "sauce droplets in thin arcing threads, "
            "microgreens leaves floating like confetti, "
            "sesame seeds in small constellation patterns",
            "Warm amber Japanese restaurant aesthetic meets Ukrainian casual dining."
        )},
        {"style": "📸", "prompt": SREAL(
            "baked salmon rolls — six perfectly formed maki on dark grey stone slate plate, "
            "torched salmon topping with beautiful char marks and translucent edges, "
            "cream cheese peeking from cut face showing layers, "
            "spicy mayo drizzled in thin elegant lines across tops, "
            "fresh pea shoot microgreens sprouting between rolls, "
            "pickled ginger rose and wasabi quenelle in corner",
            f"{INTERIOR} — dark oak table, morning sunlight from CHILI large windows, "
            "blurred leather chairs and hanging plants in background bokeh",
            "Hard natural window light from upper-left creating dramatic cross-shadows on slate, "
            "torched salmon edges catching light with beautiful caramelized highlight, "
            "dark slate plate absorbing light creating deep contrast, "
            "steam wisps rising from warm rolls",
            "Close-up overhead at 60 degrees showing roll cross-section. "
            "Chopsticks resting on plate edge as styling detail."
        )}
    ]},

    {"tema": "🍱 Роли в спайсі", "category": "food",
     "caption": "Спайсі соус, кунжут і хрустка скоринка 🔥\nРоли у CHILI — це серйозно.\n\n#роли #chiliodessa #суші #одеса",
     "refs_note": "📸 Фото ролів у спайсі соусі\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "crispy deep-fried sushi rolls with spicy sauce on dark ceramic",
            "Golden crispy tempura-battered rolls with visible crunchy texture, "
            "fiery orange-red spicy mayo generously drizzled creating glossy pools, "
            "white cream sauce in contrasting threads, "
            "sesame seeds scattered like stars, "
            "fresh microgreens bursting from top. "
            "SAUCE DRIPS off frame edge in long glossy threads. ",
            "sesame seeds orbiting in loose constellation, "
            "orange sauce droplets mid-air, "
            "microgreen leaves catching air, "
            "golden crispy fragments, steam and heat shimmer",
            "Hot and spicy energy — deep reds, oranges, golden browns. Bold and appetizing."
        )},
        {"style": "📸", "prompt": SREAL(
            "crispy maki rolls — golden tempura-fried exterior with visible crisp texture, "
            "generous spicy mayo in vivid orange-red drizzled with artistic abandon, "
            "contrasting white unagi sauce threads creating pattern, "
            "sesame seeds coating top surfaces, "
            "fresh microgreens and thinly sliced spring onion garnish, "
            "wasabi and ginger on dark slate beside rolls",
            f"{INTERIOR} dark oak table near bar area, "
            f"{BAR} blurred in background with green glow, "
            "warm amber interior lighting",
            "Single warm focused spotlight from above creating dramatic shadows, "
            "spicy orange sauce catching highlight and glowing, "
            "crispy texture emphasized by raking side light, "
            "deep moody shadows in lower third of frame",
            "Low angle shot showing height of rolls. Sauce drip off plate edge visible."
        )}
    ]},

    # === БУРГЕРИ ===

    {"tema": "🍔 Бургер з кисло-солодкою куркою — 235₴", "category": "food",
     "caption": "Кисло-солодка курка у паніровці, чедер та айсберг 🍔\nСерйозний бургер для серйозного апетиту.\nCHILI 🌶️\n\n#бургер #chiliodessa #одеса #burger",
     "refs_note": "📸 Фото бургера з меню CHILI\n🔴 Логотип CHILI PNG\n🍔 Фото булочки бріош крупно",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium burger with sweet-and-sour crispy chicken on brioche bun",
            "Golden brioche bun crown with sesame seeds, glossy glazed sweet-sour chicken fillet "
            "showing crispy panko coating with caramelized edges, melted cheddar draped over chicken, "
            "pickled onion rings, crisp iceberg lettuce leaves, cheeseburger sauce oozing dramatically. "
            "Burger EXPLODES apart through frame — each layer separating mid-air. ",
            "sesame seeds orbiting like satellites, brioche bun crumbs tumbling, "
            "cheddar cheese threads stretching and snapping, "
            "pickled onion rings spinning, iceberg leaf fragments, "
            "sauce droplets in golden threads",
            "Warm burger-gold and amber palette. Bold appetite-forward energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "sweet-and-sour chicken burger — golden sesame brioche bun, "
            "thick crispy panko chicken fillet with sweet-sour glaze catching light, "
            "melted cheddar flowing down sides, pickled red onion rings, "
            "crisp iceberg lettuce, cheeseburger sauce visible at edges, "
            "burger skewer holding tower together",
            f"{INTERIOR} dark oak table, "
            "geometric pendant light creating circular highlight on bun crown, "
            "leather chair and monstera plant softly blurred behind",
            "Single dramatic overhead spotlight on bun crown, "
            "cheese glistening, crispy chicken texture in sharp relief, "
            "deep shadows under burger suggesting height and drama",
            "Side-on hero shot at table level. Fries blurred beside burger as prop."
        )}
    ]},

    {"tema": "🍔 Чізбургер — 289₴", "category": "food",
     "caption": "Яловича котлета, бекон, чедер і соус барбекю 🔥\nКласика яка ніколи не підводить.\nCHILI 🌶️\n\n#чізбургер #chiliodessa #одеса #cheeseburger",
     "refs_note": "📸 Фото чізбургера з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "classic cheeseburger with beef patty and bacon on brioche bun",
            "Perfectly seared beef patty with crust showing grill marks, "
            "double cheddar slices melting over patty edges, crispy bacon rashers with caramelized tips, "
            "pickle coins, iceberg lettuce, cheeseburger sauce and BBQ sauce pooling dramatically. "
            "BURGER CROSS-SECTION REVEALED as it shatters through frame. ",
            "beef juices droplets mid-air like amber spheres, "
            "bacon strip curling in heat, cheddar thread spinning outward, "
            "sesame seeds from bun in constellation, "
            "BBQ sauce ribbon arcing across frame",
            "Deep meaty browns and caramel golds. Primal burger energy — bold and unapologetic."
        )},
        {"style": "📸", "prompt": SREAL(
            "classic cheeseburger — toasted brioche bun with seeds, "
            "thick beef patty with dark char crust and juicy pink center visible, "
            "two cheddar slices melted to flowing over sides, "
            "thick-cut crispy bacon with caramelized edges, "
            "dill pickle coins, crisp iceberg, BBQ and cheeseburger sauce dripping",
            f"{HALL} interior — on dark oak table, "
            "warm ambient restaurant lighting with geometric pendant above, "
            "blurred background showing restaurant buzz",
            "Warm amber restaurant spotlight from above-right, "
            "cheddar glowing golden, char marks on patty high contrast, "
            "bacon catching highlight showing caramelized texture, "
            "dramatic shadow under stacked burger",
            "Classic side-on shot at table height. Beer glass blurred at edge as lifestyle prop."
        )}
    ]},

    {"tema": "🍔 Бургер з сирним соусом та карамелізованим беконом — 345₴", "category": "food",
     "caption": "Карамелізований бекон, сирний соус і пармезан 👑\nКоли звичайний бургер — замало.\nCHILI 🌶️\n\n#бургер #chiliodessa #одеса #burger #bacon",
     "refs_note": "📸 Фото бургера з карамелізованим беконом\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium burger with caramelized bacon and cheese sauce on oversized brioche",
            "Tall golden brioche bun crown, thick beef patty, "
            "caramelized bacon lattice with amber glaze catching light like candy, "
            "cascading cheese sauce in thick golden rivers over everything, "
            "shaved parmesan snow on top, BBQ sauce dark and glossy beneath. "
            "CHEESE SAUCE WATERFALL pours through frame continuously. ",
            "caramelized bacon shards tumbling like amber glass, "
            "cheese sauce threads in long golden arcs, "
            "parmesan shavings floating like snowflakes, "
            "beef juices mid-air, "
            "BBQ sauce droplets deep brown",
            "Rich amber and gold palette — indulgent, premium, show-stopping."
        )},
        {"style": "📸", "prompt": SREAL(
            "caramelized bacon cheese sauce burger — "
            "tall brioche bun, thick beef patty, "
            "intricately caramelized bacon showing amber candy glaze with beautiful texture, "
            "thick cheese sauce flowing over sides in glossy rivers, "
            "shaved parmesan curls on crown, "
            "BBQ sauce dark and glossy, tomato slice, iceberg lettuce",
            f"{HALL} — on dark oak table under warm pendant spotlight, "
            "rest of restaurant softly glowing behind in amber tones",
            "Focused warm spotlight making cheese sauce gleam like gold, "
            "caramelized bacon texture extremely detailed in raking light, "
            "parmesan catching highlight individually, "
            "deep dramatic shadows making burger look monumental",
            "Low hero angle making burger look towering. "
            "Extra cheese sauce jar beside plate as prop."
        )}
    ]},

    # === ОСНОВНІ СТРАВИ ===

    {"tema": "🥩 Біфштекс з грибним соусом та пюре — 269₴", "category": "food",
     "caption": "Яловичий біфштекс, грибний соус і картопляне пюре 🥩\nСолідно. Смачно. CHILI.\n\n#біфштекс #chiliodessa #одеса #steak",
     "refs_note": "📸 Фото біфштексу з меню CHILI\n🔴 Логотип CHILI PNG\n🍄 Фото грибів (референс соусу)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "beef bifsteak with mushroom sauce and mashed potato on dark ceramic plate",
            "Perfectly seared beef steak with beautiful crust and grill cross-marks, "
            "rich dark brown mushroom sauce pooling and cascading over steak, "
            "silky smooth mashed potato quenelle beside it, "
            "wilted spinach with garlic oil, shaved parmesan, pickled cucumber fan. "
            "SAUCE ERUPTS through frame in dark glossy wave. ",
            "mushroom slices mid-air, dark sauce droplets orbiting, "
            "mashed potato wisps like clouds, beef juices in amber drops, "
            "parmesan shavings catching light, spinach leaves floating",
            "Rich dark browns and golden ambers — hearty Eastern European comfort with premium finish."
        )},
        {"style": "📸", "prompt": SREAL(
            "beef bifsteak plate — beautifully seared rectangular beef steak, "
            "deep brown mushroom cream sauce generously ladled over and pooling on plate, "
            "silky mashed potato quenelle with butter well, "
            "wilted spinach in garlic oil alongside, "
            "shaved parmesan, pickled cucumber fan as garnish",
            f"{HALL} interior — dark ceramic plate on warm oak table, "
            "pendant light creating circular spotlight on plate surface",
            "Focused warm spotlight from directly above, "
            "steak crust texture razor-sharp, "
            "mushroom sauce glossy and steaming, "
            "mashed potato surface catching light with silky sheen",
            "Hero overhead at 45 degrees. Pepper grinder and bread as lifestyle props beside."
        )}
    ]},

    {"tema": "🍽 Полента з пармезаном — від 219₴", "category": "food",
     "caption": "Ніжна полента, пармезан і начинка на твій вибір 🧀\nЛосось, курка або креветка — вирішуй сам.\nCHILI 🌶️\n\n#полента #chiliodessa #одеса #polenta",
     "refs_note": "📸 Фото поленти з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "creamy parmesan polenta with salmon topping on elegant dark plate",
            "Thick creamy yellow polenta base swirled artfully, "
            "pan-seared salmon fillet on top with golden crust, "
            "fresh cucumber ribbons, sliced tomatoes, spinach leaves, "
            "rucola scattered, cherry tomatoes halved showing vivid red interior, "
            "parmesan snow dusted over everything. "
            "POLENTA RISES from plate in slow golden wave. ",
            "parmesan snowflakes mid-air, cherry tomato halves tumbling showing jewel interior, "
            "salmon flakes orbiting, rucola leaves spinning, "
            "golden polenta droplets, spinach ribbon fragments",
            "Mediterranean summer palette — golden yellow, coral salmon, vivid greens."
        )},
        {"style": "📸", "prompt": SREAL(
            "polenta with parmesan — generous creamy golden polenta base with artful swirl marks, "
            "pan-seared salmon fillet centered on top with crispy golden skin, "
            "fresh cucumber slices and tomato wedges arranged alongside, "
            "baby spinach and rucola leaves, "
            "halved cherry tomatoes showing ruby interior, "
            "parmesan generously shaved over entire dish",
            f"{INTERIOR} terrace — marble table, morning daylight, "
            "green plants framing sides of shot naturally",
            "Bright clean daylight from terrace creating fresh vibrant colors, "
            "golden polenta glowing warmly, salmon skin catching crisp highlight, "
            "vegetables vivid and fresh-looking",
            "Top-down overhead shot showing the full composition beauty. "
            "Second smaller plate with topping options blurred beside."
        )}
    ]},

    {"tema": "🍝 Ньокі з креветками та базиліковим соусом — 297₴", "category": "food",
     "caption": "Ньокі, креветки, базиліковий соус і трохи халапеньо 🌶️\nГостро. Ароматно. Addictive.\nCHILI 🌶️\n\n#ньокі #chiliodessa #одеса #gnocchi #shrimp",
     "refs_note": "📸 Фото ньоків з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "gnocchi with shrimp and basil sauce in dark ceramic deep plate",
            "Pillowy golden-seared gnocchi pieces in vibrant green basil-tomato sauce, "
            "large pink tiger shrimp perched on top showing perfect curve and cook color, "
            "sliced dried tomatoes adding deep burgundy pops, "
            "fresh spinach wilted through sauce, jalapeno rings adding green heat, "
            "parmesan freshly grated snow on top. "
            "GNOCCHI AND SAUCE ERUPT upward through frame. ",
            "gnocchi pieces tumbling showing pillowy texture, "
            "shrimp mid-flight in perfect arc, "
            "basil sauce droplets deep green, dried tomato slivers, "
            "parmesan threads mid-air, jalapeno rings orbiting",
            "Vibrant Italian herb-green with coral shrimp. Bold Mediterranean energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "gnocchi with shrimp — dark ceramic bowl, "
            "golden pan-seared gnocchi in rich basil and tomato cream sauce, "
            "three large tiger shrimp arranged crown on top showing pink-orange cook color, "
            "dried tomatoes, wilted spinach, jalapeno rings visible through sauce, "
            "parmesan generously grated over top",
            f"{HALL} interior — warm oak table, "
            "pendant light above creating warm focused glow on bowl contents",
            "Warm single overhead light making sauce glisten and shrimp glow coral, "
            "steam rising from hot bowl, "
            "basil green sauce vibrant under warm light, "
            "deep shadows at bowl edges creating depth",
            "Low angle 30 degrees showing bowl depth and shrimp height. "
            "Fresh basil sprig as prop beside bowl."
        )}
    ]},

    {"tema": "🍝 Ньокі з куркою та грибами — 219₴", "category": "food",
     "caption": "Ньокі, курка, печериці і мексиканський соус 🌶️\nКомфортна їжа з характером.\nCHILI 🌶️\n\n#ньокі #chiliodessa #одеса #gnocchi",
     "refs_note": "📸 Фото ньоків з куркою з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "gnocchi with chicken and mushrooms in tomato cream sauce",
            "Soft pillowy gnocchi in rich tomato-cream Mexican sauce, "
            "diced chicken breast pieces golden from pan, "
            "sliced champignon mushrooms sautéed to golden brown, "
            "cherry tomatoes halved in sauce, fresh spinach wilted in, "
            "parmesan grated over top, Mexican sauce swirl visible. "
            "Bowl TIPS with contents CASCADING outward. ",
            "gnocchi pieces at various angles mid-air, "
            "mushroom slice fragments, cherry tomato halves showing seeds, "
            "cream sauce droplets orange-red, spinach leaf ribbons, "
            "parmesan shaving clusters",
            "Warm Italian-Mexican fusion palette — tomato reds, cream whites, golden browns."
        )},
        {"style": "📸", "prompt": SREAL(
            "chicken mushroom gnocchi — wide ceramic bowl, "
            "pillowy gnocchi in creamy tomato-spice sauce, "
            "chunky chicken breast pieces with golden sear, "
            "thickly sliced golden mushrooms, cherry tomato halves, "
            "wilted spinach, parmesan melting into sauce surface",
            f"{HALL} — on warm oak table, restaurant interior warm and busy behind in bokeh",
            "Warm restaurant ambient light with focused pendant spot on bowl, "
            "sauce surface catching warm reflection, "
            "steam suggesting fresh-cooked warmth, "
            "golden mushrooms and chicken textured under raking light",
            "Overhead 45 degrees. Sprinkle of fresh chili flakes and basil leaf on top as garnish."
        )}
    ]},

    {"tema": "🍝 Ньокі з соусом Болоньєзе — 219₴", "category": "food",
     "caption": "Болоньєзе з яловичини та свинини, томатний соус і пармезан 🥩\nІталія у серці Одеси.\nCHILI 🌶️\n\n#болоньєзе #chiliodessa #одеса #bolognese",
     "refs_note": "📸 Фото ньоків болоньєзе з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "gnocchi bolognese — pillowy potato gnocchi with rich meat sauce",
            "Rustic deep red bolognese sauce with visible ground beef and pork chunks, "
            "gnocchi nestled throughout sauce, "
            "San Marzano tomato base deep and glossy, "
            "generous fresh parmesan mountain on top, "
            "fresh basil leaves as vivid green crown. "
            "BOLOGNESE SAUCE ERUPTS through frame like lava. ",
            "meat sauce droplets deep burgundy-red, gnocchi pieces tumbling, "
            "parmesan shavings in dense cloud, "
            "basil leaves spinning, tomato chunk fragments, "
            "red sauce mist",
            "Classic Italian deep reds and warm ambers. Rustic comfort food prestige."
        )},
        {"style": "📸", "prompt": SREAL(
            "gnocchi bolognese — deep ceramic bowl, "
            "rustic rich bolognese sauce with visible beef and pork, "
            "pillowy gnocchi throughout, "
            "thick San Marzano tomato base deeply colored, "
            "large parmesan mountain freshly grated at table, "
            "fresh basil leaves on top, "
            "sauce glistening with natural meat fats",
            f"{HALL} interior — warm oak table, "
            "Italian restaurant warm lighting, "
            "candle light adding amber warmth in background bokeh",
            "Warm single candle-like light source creating intimate dinner atmosphere, "
            "sauce surface deeply glossy, "
            "parmesan catching warm highlight at edges, "
            "steam suggesting fresh preparation",
            "Close overhead 50 degrees. Fresh parmesan wedge and grater as prop beside bowl."
        )}
    ]},

    {"tema": "🍚 Ризото з беконом та курячим філе — 191₴", "category": "food",
     "caption": "Рис арборіо, бекон, куряче філе і пармезан 🧀\nРізото яке гріє зсередини.\nCHILI 🌶️\n\n#різото #chiliodessa #одеса #risotto",
     "refs_note": "📸 Фото різото з беконом з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "creamy bacon and chicken risotto in wide flat ceramic bowl",
            "Glossy creamy arborio rice spread in wide flat circle, "
            "crispy bacon lardons scattered throughout catching light, "
            "golden chicken breast slices fanned on top, "
            "bacon chip crisps standing vertical as dramatic garnish, "
            "parmesan melted through and freshly grated on top, "
            "egg yolk swirl creating golden center. "
            "RISOTTO SPREADS outward through frame in creamy wave. ",
            "arborio rice grains mid-air showing round shape, "
            "bacon lardons tumbling in amber clusters, "
            "chicken slices in flat arc, bacon crisp fragments, "
            "parmesan cloud, egg yolk sphere intact mid-air",
            "Rich cream and amber palette. Sophisticated Italian comfort food."
        )},
        {"style": "📸", "prompt": SREAL(
            "bacon chicken risotto — wide shallow ceramic bowl, "
            "perfectly cooked creamy arborio risotto with all'onda wave pattern, "
            "crispy bacon pieces throughout with one large bacon chip standing vertical, "
            "sliced golden chicken breast fanned elegantly, "
            "parmesan snow covering surface, "
            "egg yolk swirl at center creating golden sun pattern",
            f"{HALL} — wide ceramic bowl on warm oak table, "
            "restaurant interior with pendant lights creating warm glow",
            "Top-down overhead light creating even illumination on risotto surface, "
            "cream risotto catching warm golden tones, "
            "bacon crisps and parmesan casting tiny shadows, "
            "egg yolk deep golden glowing from warmth",
            "Overhead shot showing wave pattern of risotto. "
            "Parmesan wedge beside bowl as Italian styling detail."
        )}
    ]},

    {"tema": "🦐 Ризото з креветками — 245₴", "category": "food",
     "caption": "Арборіо, креветки, вʼялені томати та базиліковий соус 🍤\nРізото на рівні ресторану — у CHILI.\nCHILI 🌶️\n\n#різото #chiliodessa #одеса #risotto #shrimp",
     "refs_note": "📸 Фото різото з креветками з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "shrimp risotto with dried tomatoes and basil sauce in elegant white ceramic",
            "Silky cream risotto base with arborio rice visible, "
            "large pink tiger shrimp arranged in crown pattern on top, "
            "dried tomato slivers adding burgundy color pops, "
            "champignon mushrooms golden from sauté, "
            "fresh basil sauce swirl deep green, "
            "parmesan grated over everything. "
            "SHRIMP LEAP from bowl through frame in synchronized arc. ",
            "shrimp mid-flight in perfect pink curves, "
            "dried tomato sliver ribbons, mushroom slice fragments, "
            "basil sauce drops deep green, "
            "parmesan threads, arborio rice grains",
            "Elegant pink and cream palette with Mediterranean herb green. Premium seafood energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "shrimp risotto — elegant wide white bowl, "
            "creamy arborio risotto with natural ripple surface, "
            "four large tiger shrimp arranged symmetrically showing beautiful cook color, "
            "sun-dried tomato pieces adding color contrast, "
            "golden sautéed mushrooms, "
            "basil pesto swirl in vivid green, "
            "parmesan generously grated and beginning to melt",
            f"{INTERIOR} terrace — white bowl on marble table, "
            "afternoon Mediterranean light creating clean bright image",
            "Clean bright natural light showing vivid colors authentically, "
            "shrimp coral-pink glowing, basil sauce electric green, "
            "risotto cream and warm, "
            "tomatoes deep burgundy popping against white bowl",
            "Slightly elevated angle at 30 degrees. Fresh lemon wedge and basil sprig as props."
        )}
    ]},

    {"tema": "🥩 Бефстроганов з картопляним пюре — 355₴", "category": "food",
     "caption": "Телятина, вершки, солоні огірки та картопляне пюре 🥩\nКласика яка повертає додому.\nCHILI 🌶️\n\n#бефстроганов #chiliodessa #одеса #beef",
     "refs_note": "📸 Фото бефстроганова з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "beef stroganoff with mashed potato on dark oval ceramic plate",
            "Tender veal strips in silky sour cream sauce with mushrooms, "
            "sauce rich and creamy showing depth of color, "
            "smooth mashed potato mountain beside with butter melting down sides, "
            "pickled cucumber fan as bright green accent, "
            "fresh herbs scattered on top. "
            "CREAM SAUCE CASCADES through frame in white river. ",
            "veal strip pieces mid-air showing seared edges, "
            "cream sauce droplets white and ivory, "
            "mushroom slices orbiting, mashed potato wisps, "
            "pickle slices like green discs, herb sprigs",
            "Classic Russian-Ukrainian comfort food palette — cream whites, rich browns, fresh greens."
        )},
        {"style": "📸", "prompt": SREAL(
            "beef stroganoff — dark oval plate, "
            "tender veal strips in glossy rich sour cream and mushroom sauce, "
            "sauce deep ivory with visible spice flecks, "
            "silky mashed potato peak beside with melted butter pool, "
            "pickled cucumber fan showing bright green color and translucent slices, "
            "fresh dill sprig on mashed potato summit",
            f"{HALL} interior — dark oval plate on warm oak table, "
            "warm amber restaurant lighting creating intimate dinner feel",
            "Warm focused pendant light from above, "
            "cream sauce catching warm ivory-gold tones, "
            "mashed potato surface silky and smooth, "
            "veal pieces glistening from sauce coating",
            "45-degree angle hero shot showing both stroganoff and mashed potato. "
            "Dark bread slice as traditional prop beside plate."
        )}
    ]},

    {"tema": "🥩 Пеппер стейк з картоплею фрі — 495₴", "category": "food",
     "caption": "Вирізка з яловичини, перцевий соус і картопля фрі 🔥\nСтейк який говорить сам за себе.\nCHILI 🌶️\n\n#стейк #chiliodessa #одеса #steak #beef",
     "refs_note": "📸 Фото пеппер стейку з меню CHILI\n🔴 Логотип CHILI PNG\n🥩 Фото мармурування м'яса (референс)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium pepper steak with fries on dark slate board",
            "Thick beef tenderloin steak with dark pepper crust showing perfect grill marks, "
            "cross-cut revealing pink-red medium-rare interior, "
            "dramatic pepper cream sauce poured dramatically over steak, "
            "golden crispy fries piled beside, "
            "wilted spinach with garlic oil, shaved parmesan, chili pepper garnish. "
            "STEAK RISES from board through frame like monument. ",
            "black peppercorns orbiting in slow constellation, "
            "beef juice droplets deep amber-red, "
            "pepper sauce pour mid-stream, "
            "fry sticks mid-flight golden, "
            "spinach leaves as dark green ribbon",
            "Dark and dramatic — charcoal blacks, deep reds, golden fries. Power and premium energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "pepper steak — thick beef tenderloin with dark pepper crust, "
            "perfect grill crosshatch visible on surface, "
            "sliced to reveal vivid pink-red medium-rare interior, "
            "rich pepper cream sauce drizzled over and pooling, "
            "golden crispy fries in tall pile, "
            "wilted spinach, shaved parmesan, red chili garnish",
            f"{HALL} — on dark slate board on oak table, "
            "dramatic restaurant lighting creating intense spotlight effect",
            "Hard single focused spotlight from directly above, "
            "pepper crust texture extreme detail in raking light, "
            "steak cross-section glowing pink-red from internal warmth, "
            "pepper sauce catching glossy highlight, "
            "fries golden with deep shadow valleys",
            "45-degree hero angle showing steak cut face. "
            "Pepper grinder and steak knife as premium props."
        )}
    ]},

    {"tema": "🍗 Курячий шніцель з картоплею та вершковим песто — 251₴", "category": "food",
     "caption": "Хрусткий шніцель, смажена картопля та вершкове песто 🍗\nПросто і бездоганно.\nCHILI 🌶️\n\n#шніцель #chiliodessa #одеса #schnitzel",
     "refs_note": "📸 Фото курячого шніцеля з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "crispy chicken schnitzel with garlic potatoes and basil pesto on dark plate",
            "Golden crispy panko-breaded chicken schnitzel lying flat, "
            "crust texture beautifully visible with deep golden color and crispy ridges, "
            "buttery pan-fried garlic potatoes scattered beside showing golden sear marks, "
            "seasonal cabbage salad adding fresh green-white texture, "
            "cream basil pesto sauce swirled elegantly over schnitzel. "
            "SCHNITZEL RISES and SHATTERS through frame showing crispy interior. ",
            "panko breadcrumb particles mid-air in golden cloud, "
            "potato chunk tumbling showing sear, "
            "basil pesto drops deep green, "
            "cabbage leaf ribbons white-green, "
            "butter foam wisps",
            "Golden and green — crispy summer energy with fresh herb contrast."
        )},
        {"style": "📸", "prompt": SREAL(
            "chicken schnitzel plate — large golden panko-breaded schnitzel filling most of plate, "
            "crust texture extremely crispy and detailed with deep golden-amber color, "
            "buttery fried garlic potatoes with visible herb coating beside, "
            "fresh seasonal cabbage salad in small mound, "
            "cream basil pesto sauce in elegant swirl over schnitzel",
            f"{INTERIOR} terrace — bright daylight plate on marble table, "
            "green terrace plants framing shot naturally",
            "Bright natural daylight emphasizing golden crispy texture, "
            "raking afternoon light making every breadcrumb cast tiny shadow, "
            "pesto sauce vivid green, "
            "potato skins catching golden highlight",
            "Side angle at table level showing schnitzel thickness. "
            "Lemon wedge as classic schnitzel styling prop."
        )}
    ]},

    {"tema": "🍗 Курячий стейк з солодкою кукурудзою та сирним соусом — 299₴", "category": "food",
     "caption": "Курячий стейк, солодка кукурудза і сирний соус 🌽\nЯскраво. Соковито. Смачно.\nCHILI 🌶️\n\n#курка #chiliodessa #одеса #chicken",
     "refs_note": "📸 Фото курячого стейку з кукурудзою з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "chicken steak with sweet corn and cheese sauce on dark ceramic plate",
            "Golden-seared chicken breast steak with beautiful char marks, "
            "sweet corn kernels in pools of golden butter — some still on the cob, "
            "thick cheese sauce cascading over chicken and corn in golden rivers, "
            "rucola leaves and cherry tomato halves adding color contrast, "
            "shaved parmesan over everything. "
            "CORN KERNELS EXPLODE through frame in golden shower. ",
            "corn kernels mid-air in dense golden cluster, "
            "cheese sauce threads golden-yellow, "
            "chicken piece mid-turn showing sear, "
            "cherry tomato halves tumbling jewel-red, "
            "rucola leaves scattered",
            "Vibrant summer golden yellow and green palette. Bright appetite-forward energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "chicken steak with corn — dark ceramic plate, "
            "thick chicken breast steak with golden char marks and juicy surface, "
            "sweet corn off the cob in rich butter and cheese sauce, "
            "thick cheese sauce draping over chicken showing glossy pull, "
            "fresh rucola leaves and halved cherry tomatoes, "
            "parmesan generously shaved",
            f"{INTERIOR} terrace — marble table in afternoon sunlight, "
            "golden summer light creating warm energetic atmosphere",
            "Direct warm afternoon sunlight creating golden glow, "
            "corn kernels individually lit glowing yellow, "
            "cheese sauce gleaming, "
            "chicken char marks crisp in raking light",
            "Overhead 45-degree angle. Grilled corn half as dramatic hero prop beside plate."
        )}
    ]},

    {"tema": "🌾 Булгур з курячим фрікасе — 173₴", "category": "food",
     "caption": "Булгур, куряче філе, кабачок і карі 🌾\nКорисно. Ароматно. Задоволення без докорів.\nCHILI 🌶️\n\n#булгур #chiliodessa #одеса #bulgur",
     "refs_note": "📸 Фото булгуру з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "bulgur wheat fricassee with chicken and vegetables in ceramic bowl",
            "Nutty golden bulgur wheat as base with visible grain texture, "
            "tender chicken fricassee pieces in light cream-curry sauce, "
            "zucchini chunks, bell pepper strips in yellow-orange, "
            "red onion slivers, golden champignon mushrooms, "
            "curry-infused cream sauce binding everything, "
            "fresh parsley and green onion scattered on top. "
            "BULGUR AND VEGETABLES SWIRL upward through frame. ",
            "bulgur grains mid-air in golden dust cloud, "
            "chicken pieces tumbling, vegetable chunk fragments in color, "
            "curry sauce drops deep golden-orange, "
            "green onion ribbons spinning",
            "Warm golden spice palette — turmeric yellows, curry oranges, fresh herb greens."
        )},
        {"style": "📸", "prompt": SREAL(
            "bulgur fricassee — ceramic bowl, "
            "fluffy bulgur wheat base with defined individual grains, "
            "chicken fricassee pieces with light golden curry cream sauce, "
            "colorful bell pepper and zucchini pieces, "
            "golden mushrooms, red onion slivers, "
            "fresh parsley and green onion garnish on top",
            f"{INTERIOR} — on warm oak table, "
            "natural daylight making healthy colors vivid and fresh",
            "Clean natural daylight showing true colors, "
            "bulgur grains individually visible in raking light, "
            "curry sauce warm golden tone, "
            "vegetables bright and fresh-looking",
            "Overhead shot showing colorful bowl composition. "
            "Fresh parsley bunch beside as prop."
        )}
    ]},

    {"tema": "🍗 Курячі биточки з пюре та фетовим мусом — 225₴", "category": "food",
     "caption": "Битки з курячого філе, пюре, мус з фети та вершкове песто 🧀\nНіжно. По-домашньому. Смачно.\nCHILI 🌶️\n\n#курка #chiliodessa #одеса #chicken",
     "refs_note": "📸 Фото курячих биточків з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "chicken rissoles with mashed potato and feta mousse on dark plate",
            "Three golden pan-fried chicken rissoles arranged in triangle, "
            "silky mashed potato quenelle with butter lake on top, "
            "ethereally light feta mousse clouds white and airy, "
            "cream basil pesto sauce swirled elegantly, "
            "cherry tomatoes halved showing vivid interior, "
            "fresh cucumber slices, "
            "parsley leaf garnish. "
            "FETA MOUSSE CLOUDS FLOAT through frame like white puffs. ",
            "feta mousse wisps drifting upward, "
            "chicken rissole pieces mid-air showing golden crust, "
            "mashed potato wisps like soft clouds, "
            "cherry tomato halves in jewel-red arc, "
            "pesto drops deep green",
            "Soft cream and gold palette with vivid green and red accents. Comforting home-cooking prestige."
        )},
        {"style": "📸", "prompt": SREAL(
            "chicken rissoles plate — dark ceramic plate, "
            "three perfectly formed golden-fried chicken rissoles, "
            "silky mashed potato with melted butter, "
            "whipped feta mousse in soft white clouds beside, "
            "cream pesto sauce swirled, "
            "halved cherry tomatoes, sliced cucumber, "
            "fresh parsley sprig garnish",
            f"{HALL} — on warm oak table, "
            "warm focused pendant lamp creating intimate glow on plate",
            "Warm focused overhead light, "
            "feta mousse catching soft highlight with ethereal glow, "
            "rissole golden crust detailed in warm light, "
            "mashed potato silk catching butter highlight",
            "Hero angle at 30 degrees showing height of mousse. "
            "Vintage ceramic butter dish as prop beside."
        )}
    ]},

    {"tema": "🥩 Свинина BBQ з картоплею — 319₴", "category": "food",
     "caption": "Свинина, соус BBQ і картопля по-ірландські 🔥\nПросто. По-чоловічому. CHILI.\nCHILI 🌶️\n\n#свинина #bbq #chiliodessa #одеса",
     "refs_note": "📸 Фото свинини BBQ з меню CHILI\n🔴 Логотип CHILI PNG\n🔥 Фото вогню/гриля (референс атмосфери)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "BBQ pork with Irish-style potatoes on dark cast iron serving board",
            "Thick pork steak slices with dark caramelized BBQ glaze, "
            "grill marks creating perfect crosshatch on glossy surface, "
            "rich dark BBQ sauce pooling and dripping dramatically, "
            "Irish-style quartered pan-roasted potatoes golden and crispy, "
            "coriander sauce Kinza bright green as contrast. "
            "BBQ SAUCE POURS through frame in dark glossy waterfall. ",
            "BBQ sauce droplets deep mahogany-brown mid-air, "
            "pork slice fragments showing glaze, "
            "potato wedge tumbling golden, "
            "green cilantro leaves spinning, "
            "smoke wisps from grill marks",
            "Dark caramel and charcoal palette — masculine, bold, primal grill energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "BBQ pork plate — dark cast iron board, "
            "thick-sliced pork with deep dark BBQ glaze, "
            "grill crosshatch marks showing caramelization depth, "
            "BBQ sauce pooling around edges in dark glossy rivers, "
            "Irish-style quartered roasted potatoes with crispy skin and golden flesh, "
            "fresh coriander sauce in small ramekin",
            f"{HALL} — dark board on oak table, "
            "dramatic restaurant lighting creating intense spotlight on meat",
            "Hard dramatic spotlight from above-right, "
            "BBQ glaze reflecting like lacquer in intense light, "
            "grill marks at maximum contrast, "
            "smoke effect from smoked oil addition, "
            "deep dramatic shadows all around",
            "Low dramatic angle making meat look monumental. "
            "Extra BBQ sauce ramekin and cast iron pan visible at edge."
        )}
    ]},

    {"tema": "🥩🐟 Мʼясний Сет — 1145₴", "category": "food",
     "caption": "4 стейки + картопля + соуси + салат 🔥\nМʼясний Сет CHILI — для компанії яка розуміється.\nCHILI 🌶️\n\n#мʼясо #set #chiliodessa #одеса #steak",
     "refs_note": "📸 Фото мʼясного сету з меню CHILI (загальний план)\n🔴 Логотип CHILI PNG\n🍽️ Фото великої дошки з подачею",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "spectacular meat set platter on large dark wooden board for sharing",
            "Four different steaks arranged on board — beef tenderloin, chicken thigh, "
            "chicken breast, pork — each with different char and color, "
            "garlic herb potatoes in generous pile, "
            "cabbage salad in small bowl, feta mousse quenelle, "
            "two sauce ramekins — spicy garlic and honey mustard — gleaming. "
            "ENTIRE BOARD EXPLODES UPWARD through frame with all components separating. ",
            "multiple steak pieces mid-air at different heights, "
            "potato wedges tumbling, "
            "sauce droplets from both ramekins in contrasting streams, "
            "feta mousse wisp, cabbage leaf fragments, "
            "herb sprigs spinning in abundance",
            "Feast and abundance energy — dark wood board, multiple meat varieties, sharing celebration."
        )},
        {"style": "📸", "prompt": SREAL(
            "meat set platter — large dark wooden sharing board, "
            "four steak types arranged with space: beef tenderloin sliced to show pink, "
            "chicken thigh with char, chicken breast fillet, pork steak, "
            "each showing distinct cooking and color, "
            "garlic potato wedges in generous center pile, "
            "small bowl of cabbage salad, "
            "feta mousse quenelle, two sauce ramekins symmetrically placed",
            f"{HALL} interior — on large oak table with multiple chairs visible, "
            "warm restaurant atmosphere suggesting celebration and company",
            "Wide soft overhead lighting showing entire board evenly, "
            "each meat type catching individual highlights, "
            "dark board making all items pop visually, "
            "steam suggesting fresh from kitchen",
            "Wide overhead shot showing entire platter. "
            "Wine glasses and company hands visible at edges for lifestyle storytelling."
        )}
    ]},

    {"tema": "🐟 Хрумкі котлетки з лосося та тунця — 293₴", "category": "food",
     "caption": "Котлетки з тунця та лосося у панко, картопляне пюре і соус голандез 🐟\nМорська душа CHILI.\nCHILI 🌶️\n\n#лосось #тунець #chiliodessa #одеса #fish",
     "refs_note": "📸 Фото рибних котлеток з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "crispy salmon and tuna fish cakes with hollandaise sauce on dark plate",
            "Three golden panko-crusted fish cakes showing crispy texture, "
            "silky mashed potato alongside with butter well, "
            "hollandaise sauce in glossy yellow pour over fish cakes, "
            "basil sauce swirl deep green, "
            "pickled cucumber fan, "
            "feta crumbles white, sun-dried tomato slivers, "
            "parmesan shaved over top. "
            "HOLLANDAISE POURS through frame in golden cascade. ",
            "panko crust particles golden mid-air, "
            "hollandaise sauce stream catching light, "
            "fish flake fragments showing pink salmon and ivory tuna, "
            "cucumber slices in translucent arc, "
            "parmesan snow",
            "Golden Mediterranean sea palette — panko gold, hollandaise yellow, green basil, salmon pink."
        )},
        {"style": "📸", "prompt": SREAL(
            "fish cake plate — dark ceramic plate, "
            "three golden panko-crusted salmon-tuna fish cakes with crispy exterior, "
            "smooth mashed potato, "
            "bright yellow hollandaise sauce generously drizzled, "
            "fresh green basil sauce swirl, "
            "pickled cucumber fan, white feta crumbles, "
            "sun-dried tomato pieces, parmesan shavings",
            f"{INTERIOR} terrace — marble table, "
            "Mediterranean daylight making colors vibrant and fresh",
            "Bright Mediterranean daylight, "
            "hollandaise sauce glowing golden, "
            "fish cake crust texture sharp in raking light, "
            "green basil sauce vivid, "
            "overall fresh and light coastal feeling",
            "45-degree elevated angle. Fresh dill sprig and lemon wedge as sea-food styling props."
        )}
    ]},

    {"tema": "🐟 Лосось з пармезановим пюре — 373₴", "category": "food",
     "caption": "Стейк з лосося, пюре з пармезаном і соус Голандез 🐟\nМʼякий, ніжний, ідеальний.\nCHILI 🌶️\n\n#лосось #salmon #chiliodessa #одеса",
     "refs_note": "📸 Фото лосося з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium salmon steak with parmesan mashed potato on elegant dark plate",
            "Pan-seared salmon fillet with golden-crispy skin side up, "
            "flesh showing orange-pink gradient from cooked edge to tender center, "
            "creamy parmesan mashed potato swirled beside with butter lake, "
            "hollandaise sauce cascading over salmon in glossy yellow waterfall, "
            "masago caviar orange dots scattered on sauce, "
            "wilted spinach with garlic oil. "
            "SALMON RISES through frame with HOLLANDAISE WATERFALL following. ",
            "salmon flakes mid-air showing vivid orange-pink color, "
            "hollandaise sauce stream in golden arc, "
            "masago caviar beads like tiny orange planets, "
            "spinach leaf ribbons, mashed potato wisp, "
            "parmesan snow",
            "Premium coastal orange and gold palette. Sophisticated dinner energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "salmon with parmesan mash — elegant dark oval plate, "
            "thick salmon steak with perfectly crisped golden skin, "
            "flesh showing beautiful orange-pink gradient and flaky texture at edge, "
            "silky parmesan mashed potato quenelle with golden butter pool, "
            "rich hollandaise sauce draped and pooling, "
            "masago orange caviar dots on sauce surface like jewels, "
            "wilted baby spinach with garlic oil",
            f"{HALL} interior — dark plate on warm oak table, "
            "focused restaurant ambient light creating intimate dinner feel",
            "Single warm focused spotlight, "
            "salmon skin golden and crisped, "
            "flesh catching warm orange glow from internal pigment and light, "
            "hollandaise glossy reflecting light, "
            "masago each catching individual highlight dot",
            "Low 30-degree angle hero shot showing salmon steak height. "
            "White wine glass blurred at edge as dining prop."
        )}
    ]},

    {"tema": "🐟 Стейк з тунця з бататом — 365₴", "category": "food",
     "caption": "Тунець, батат і вершково-сирний соус 🐟\nНесподівано гарне поєднання.\nCHILI 🌶️\n\n#тунець #tuna #chiliodessa #одеса",
     "refs_note": "📸 Фото стейку з тунця з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium tuna steak with sweet potato and cream cheese sauce",
            "Thick seared tuna steak with dark char crust on exterior, "
            "cross-cut revealing vivid pink-red raw-medium interior, "
            "roasted sweet potato wedges in deep orange beside, "
            "cream cheese sauce white and silky draping over everything, "
            "wilted spinach with garlic oil, "
            "parmesan shaved generously over top. "
            "TUNA CROSS-SECTION REVEALED as it RISES through frame. ",
            "tuna slice pieces mid-air showing vivid pink interior, "
            "sweet potato wedge tumbling showing orange flesh, "
            "cream sauce droplets white and silky, "
            "spinach leaf ribbons, parmesan snow, "
            "garlic oil drops golden",
            "Bold contrast palette — vivid tuna pink vs sweet potato orange vs white sauce."
        )},
        {"style": "📸", "prompt": SREAL(
            "tuna steak with sweet potato — dark ceramic plate, "
            "thick seared tuna steak sliced to reveal brilliant pink-red interior, "
            "char crust creating dramatic dark exterior contrast, "
            "roasted sweet potato wedges showing deep orange caramelized flesh, "
            "cream cheese sauce generously draped, "
            "baby spinach with garlic oil, "
            "parmesan shavings",
            f"{HALL} interior — dark plate on oak table, "
            "dramatic restaurant lighting enhancing color contrasts",
            "Hard dramatic spotlight from above, "
            "tuna interior pink-red glowing vividly, "
            "sweet potato orange deep and caramelized, "
            "cream sauce bright white against dark plate, "
            "extreme color contrast composition",
            "45-degree angle showing tuna cross-section cut face prominently. "
            "Fresh lime wedge and chili as oceanic-spicy styling props."
        )}
    ]},

    # === САЛАТИ ===

    {"tema": "🥗 Салат з креветками", "category": "food",
     "caption": "Фризе, авокадо, креветки і пармезан 🦐\nСалат який хочеться їсти очима.\nCHILI 🌶️\n\n#салат #chiliodessa #одеса #shrimp",
     "refs_note": "📸 Фото салату з креветками з меню CHILI\n🔴 Логотип CHILI PNG\n🌿 Фото монстери CHILI (для фону)",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium shrimp salad in dark grey ceramic low bowl",
            "Frisee lettuce creating airy green cloud base, "
            "large pink tiger shrimp scattered throughout and on top showing perfect cook color, "
            "avocado chunks in creamy green, "
            "curled wide parmesan ribbons like elegant scrolls, "
            "dijon mustard seeds adding texture, "
            "light lemon dressing glistening on leaves. "
            "BOWL TIPS and salad EXPLODES upward through frame. ",
            "individual shrimp mid-flight showing pink curve, "
            "parmesan ribbons unrolling in air, "
            "frisee lettuce leaves like green feathers, "
            "avocado pieces tumbling, "
            "mustard seeds in tiny constellation",
            "Fresh vibrant greens and coral pink shrimp palette. Light elegant energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "premium shrimp salad — dark graphite ceramic bowl with "
            "frisee lettuce cloud, six large pink tiger shrimp arranged crown-like on top, "
            "ripe avocado quarter showing green-yellow flesh, "
            "hand-shaved parmesan curls catching light, "
            "micro mustard seed garnish, "
            "light citrus dressing creating sheen on leaves",
            f"{INTERIOR} terrace — marble table surface, "
            "large glossy monstera leaf framing left side of shot naturally, "
            "second monstera leaf creating right-side frame, "
            "Odessa morning light streaming from upper right through terrace",
            "Dappled natural light through monstera leaves creating botanical shadow patterns "
            "on marble table and salad surface, "
            "shrimp catching direct highlight to show perfect pink color, "
            "fresh and vibrant daytime color temperature",
            "Overhead 45-degree angle with monstera leaves framing sides. "
            "Slice of lemon as prop. Shot for appetite appeal."
        )}
    ]},

    # === СНІДАНКИ ===

    {"tema": "🥞 Вафля з лососем — 265₴", "category": "breakfast",
     "caption": "Вафля, лосось і авокадо 🥑\nСніданок який варто прокинутися.\nCHILI щодня 10:00–14:00 🌶️\n\n#сніданок #waffle #chiliodessa #одеса",
     "refs_note": "📸 Фото вафлі з лососем з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "premium Belgian waffle topped with salmon and avocado on dark plate",
            "Golden crispy waffle with deep grid pattern showing caramelized edges, "
            "generous smoked salmon slices draped over waffle in coral-pink ribbons, "
            "creamy ripe avocado slices fanned artfully, "
            "fresh mixed greens and microgreens piled high, "
            "lemon wedge and crème fraîche quenelle. "
            "WAFFLE RISES through frame with toppings CASCADING. ",
            "waffle grid squares tumbling at angles, "
            "salmon ribbons flowing like fabric, "
            "avocado slices in formation, "
            "microgreens leaves spinning like propellers, "
            "lemon juice droplets in tiny sphere shapes",
            "Sophisticated morning colors — salmon coral, avocado green, golden waffle. Brunch energy."
        )},
        {"style": "📸", "prompt": SREAL(
            "waffle with salmon breakfast — dark ceramic rectangular plate, "
            "Belgian waffle with pronounced deep grid, beautifully golden-brown caramelized edges, "
            "generous cold-smoked salmon rose arrangement, "
            "ripe Hass avocado quarter showing gradient from green skin to pale flesh, "
            "fresh mixed salad leaves and pea shoots, "
            "crème fraîche quenelle with dill, "
            "lemon wedge alongside",
            f"{INTERIOR} — placed on oak wooden table, "
            "morning golden hour sunlight from CHILI large windows streaming at low angle, "
            "geometric wire pendant lamp blurred in background bokeh above",
            "Low angle morning golden hour light raking across waffle grid creating deep shadows "
            "in each square for texture emphasis, "
            "salmon catching warm pink highlight from morning light, "
            "avocado glowing green-gold, "
            "overall warm golden morning palette",
            "Landscape-leaning composition at 45-degree angle. "
            "Coffee cup blurred in upper corner as lifestyle prop."
        )}
    ]},

    {"tema": "🍳 Американський сніданок — 315₴", "category": "breakfast",
     "caption": "Яйця, бекон, тости і все що треба 🍳\nАмериканський сніданок у CHILI.\nЩодня 10:00–14:00 🌶️\n\n#сніданок #breakfast #chiliodessa #одеса",
     "refs_note": "📸 Фото американського сніданку з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "full American breakfast spread on dark oval plate",
            "Two perfectly fried eggs sunny-side-up with bright orange yolks, "
            "crispy bacon rashers curled at edges showing caramelization, "
            "sourdough toast triangles with golden edges, "
            "fresh tomato halves showing juicy seed chambers, "
            "sautéed mushrooms and baked beans. "
            "Steam RISES dramatically as plate LIFTS through frame. ",
            "bacon strips curling mid-air, "
            "egg yolk sphere floating perfectly intact, "
            "toast crumbs orbiting in loose cluster, "
            "fresh tomato droplets, "
            "steam wisps caught in light",
            "Warm morning feast colors — egg yellow, bacon brown, tomato red. Hearty satisfaction."
        )},
        {"style": "📸", "prompt": SREAL(
            "American breakfast on dark oval ceramic plate: "
            "two perfectly cooked eggs sunny-side-up, yolks intact and vibrant orange-yellow, "
            "three crispy bacon rashers with dark caramelized edges, "
            "two sourdough toast triangles buttered and golden, "
            "halved vine tomatoes, sautéed wild mushrooms, "
            "hash brown cakes with crispy surface",
            f"{INTERIOR} — on CHILI oak wooden table, "
            "morning golden sunlight streaming from large windows at golden hour angle, "
            "leather chair back visible at plate edge, "
            "hanging plants creating green bokeh backdrop",
            "Warm golden hour morning light from window at low angle, "
            "egg yolks glowing like small suns, "
            "bacon texture razor-sharp in raking light, "
            "steam wisps rising from hot elements, "
            "wood grain of table adding organic warmth",
            "Overhead shot with morning coffee, newspaper as lifestyle styling. "
            "Full plate fills frame."
        )}
    ]},

    {"tema": "🫐 Сирники з карамеллю — 219₴", "category": "breakfast",
     "caption": "Карамельна скоринка, горіхи, сметана 🫐\nСирники як вдома — тільки краще.\nCHILI 10:00–14:00 🌶️\n\n#сирники #сніданок #chiliodessa #одеса",
     "refs_note": "📸 Фото сирників з меню CHILI\n🔴 Логотип CHILI PNG",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "golden Ukrainian syrnyky cheese pancakes stacked on dark plate",
            "Three golden-brown cheese pancakes stacked with caramelized crust visible on each, "
            "liquid caramel sauce pouring over stack and pooling at base in glossy amber rivers, "
            "walnut halves placed on top and around base, "
            "sour cream quenelle with beautiful soft fold texture, "
            "fresh blueberries scattered. "
            "CARAMEL POURS through frame in continuous amber waterfall. ",
            "caramel threads in long arcing streams, "
            "walnut halves tumbling at different angles, "
            "blueberries bouncing with juice drops, "
            "sour cream wisps, "
            "golden breadcrumb texture particles",
            "Warm amber caramel palette against dark — Ukrainian comfort food with premium presentation."
        )},
        {"style": "📸", "prompt": SREAL(
            "Ukrainian syrnyky — three golden cheese pancakes stacked, "
            "each with visible caramelized crust in deep amber, "
            "warm caramel sauce drizzling down sides creating glossy rivulets, "
            "walnut halves arranged on top cluster, "
            "white sour cream quenelle with elegant fold beside stack, "
            "fresh blueberries and mint leaf garnish",
            f"{INTERIOR} — on CHILI wooden table, "
            "morning soft window light, "
            "geometric pendant lamp creating circular shadow pattern on table surface",
            "Warm morning soft-box light from above-right, "
            "caramel sauce glowing amber catching highlight, "
            "golden caramelized crust texture rendered in sharp detail, "
            "steam rising gently suggesting warmth and freshness",
            "Hero close-up at 45 degrees to show stack height and caramel flow. "
            "Small jar of caramel sauce as prop beside plate."
        )}
    ]},

    # === ТЕРАСА / АТМОСФЕРА ===

    {"tema": "🌅 Тераса CHILI", "category": "vibe",
     "caption": "Одеса, літо, тераса 🌿\nДзвони — забронюємо.\n📞 +380 66 440 16 88\nCHILI 🌶️\n\n#тераса #chiliodessa #літоодеса #одеса",
     "refs_note": "📸 Фото тераси CHILI (3-5 ракурсів)\n🔴 Логотип CHILI PNG\n🪑 Фото червоних стільців крупно",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "CHILI restaurant summer terrace scene",
            "Coral-tomato-red perforated plastic chairs around grey marble-veined tables, "
            "dark graphite metal canopy frame overhead with warm Edison string lights, "
            "lush green bushes and trees creating natural walls around terrace perimeter, "
            "cobblestone floor pattern visible, "
            "Odessa city architecture softly visible beyond green foliage. "
            "Scene ZOOMS toward viewer as terrace EXPANDS through frame. ",
            "coral chair fragments spinning outward, "
            "marble table surface pieces, "
            "green leaf confetti from terrace plants, "
            "Edison bulb light flares, "
            "cobblestone pieces",
            "Warm golden summer evening palette. Coral-red chairs as hero color against greenery."
        )},
        {"style": "📸", "prompt": SREAL(
            "CHILI restaurant terrace — establishing atmosphere shot, "
            "coral-red perforated chairs pulled back from marble tables creating empty invitation, "
            "dark metal canopy casting graphic shadow patterns on cobblestone floor, "
            "natural green bushes and trees framing terrace borders, "
            "warm afternoon Odessa light creating dramatic shadow play across entire scene",
            f"CHILI terrace exterior {INTERIOR} — "
            "Odessa residential and commercial buildings visible at distance through green, "
            "sky visible above canopy edge with soft clouds",
            "Golden late afternoon sunlight at 30-degree angle to terrace, "
            "coral-red chairs glowing warm in direct sun, "
            "deep shadow pools between chairs and under canopy, "
            "green foliage backlit and glowing emerald, "
            "overall cinematic golden hour quality",
            "Wide establishing shot from corner of terrace. "
            "One chair at different angle suggesting recent use and life. "
            "Storytelling composition showing the full CHILI terrace identity."
        )}
    ]},

    {"tema": "💡 Люстра з перців", "category": "vibe",
     "caption": "Наша люстра — не просто світло 🌶️\nЦе характер CHILI.\n\n#chiliodessa #інтер'єр #design #одеса",
     "refs_note": "📸 Фото люстри з перців CHILI (з низу вгору)\n🔴 Логотип CHILI PNG\n🌿 Фото зелених рослин на стінах",
     "variants": [
        {"style": "3D", "prompt": S3D(
            "the iconic CHILI restaurant chili pepper chandelier",
            "Massive three-tier circular chandelier made entirely of hundreds of dark glossy ceramic chili peppers, "
            "each pepper individually sculpted in deep burgundy-red ceramic glaze, "
            "warm amber light glowing from within tiers like embers, "
            "green trailing vine plants cascading from black metal wall shelving on both sides, "
            "exposed silver ventilation ducts and concrete ceiling adding industrial context. "
            "PEPPERS RAIN DOWN through frame as chandelier ROTATES. ",
            "individual ceramic pepper shapes tumbling at all angles, "
            "amber glow spots mid-air, "
            "green vine leaf fragments, "
            "metal chain links, "
            "warm light particles like embers",
            "Dark atmospheric interior palette — burgundy peppers, amber glow, deep shadows."
        )},
        {"style": "📸", "prompt": SREAL(
            "CHILI restaurant signature pepper chandelier — "
            "shot from directly below looking straight up, "
            "hundreds of dark glossy burgundy ceramic chili peppers arranged in three concentric rings, "
            "warm amber Edison bulbs glowing from within creating halo through pepper silhouettes, "
            "green vine plants trailing down from black metal shelving on left and right edges of frame, "
            "exposed industrial ceiling with silver ducts visible in upper corners",
            f"{HALL} — shot from central floor position looking directly up, "
            "restaurant activity at edges suggesting a full house",
            "The chandelier itself is the light source — warm amber backlight creating "
            "dramatic silhouette of each pepper shape, "
            "deep shadows between peppers creating texture, "
            "green vines catching amber highlight at edges, "
            "overall dramatic chiaroscuro — warm amber center, deep shadows surrounding",
            "Pure upward shot — chandelier fills entire frame. "
            "Long exposure to capture amber glow. "
            "This is the most unique CHILI signature image."
        )}
    ]},
]

# ============================
# ДЕНЬ ТИЖНЯ
# ============================
DAY_CATEGORIES = {
    0: ["food", "matcha"],           # Понеділок — основні страви + матча
    1: ["food", "matcha"],           # Вівторок
    2: ["cocktail", "matcha"],       # Середа — коктейлі
    3: ["food", "breakfast"],        # Четвер — їжа + сніданки
    4: ["cocktail", "food"],         # П'ятниця — коктейлі + страви
    5: ["cocktail", "vibe", "food"], # Субота — все
    6: ["breakfast", "vibe"],        # Неділя — сніданки + атмосфера
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
            f"🌶️ Всі теми:\n⭐ = сьогодні · ✓ = вже цього тижня\n\n" + "\n".join(lines),
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
                  "breakfast": "🍳 Сніданки", "vibe": "🌅 Атмосфера"}
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
