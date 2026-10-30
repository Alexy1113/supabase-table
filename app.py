import html
import re
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Menüü Hinnad",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TRANSLATIONS = {
    "Русский": {
        "language": "Язык / Keel",
        "refresh": "Обновить данные",
        "title": "Menüü Hinnad",
        "subtitle": "Сравнивайте цены в ресторанах и следите за их изменениями.",
        "connection_error": "Не удалось подключиться к Supabase. Проверь Secrets приложения в настройках Streamlit.",
        "empty": "В Supabase пока нет блюд для отображения.",
        "filters": "Фильтры",
        "search": "Поиск блюда или ресторана",
        "restaurant": "Ресторан",
        "all": "Все",
        "category": "Категория",
        "sort": "Сортировка",
        "sort_low": "Сначала дешевле",
        "sort_high": "Сначала дороже",
        "sort_name": "По названию",
        "items": "Позиций",
        "restaurants": "Ресторанов",
        "changes": "Позиций с изменением цены",
        "cheapest_dish": "Самое дешёвое блюдо",
        "cheapest_drink": "Самый дешёвый напиток",
        "tab_menu": "Меню и цены",
        "tab_compare": "Сравнение",
        "tab_cheapest": "Самые дешёвые",
        "tab_map": "Карта",
        "cheapest_heading": "Самые дешёвые товары по категориям",
        "cheapest_empty": "Нет товаров для отображения.",
        "name": "Блюдо / продукт",
        "variant": "Вариант",
        "price": "Текущая цена",
        "old_price": "Предыдущая цена",
        "delta": "Изменение",
        "updated": "Обновлено",
        "no_results": "По заданным фильтрам ничего не найдено.",
        "compare_heading": "Сравнение предложений",
        "compare_hint": "Введите название или часть названия, чтобы увидеть подходящие позиции разных ресторанов. Для сравнения попробуйте общее слово, например «burger» или «kohv».",
        "compare_search": "Что сравнить?",
        "price_down": "Дешевле",
        "price_up": "Дороже",
        "same": "Без изменения",
        "read_only": "Последнее обновление базы данных: {date}",
        "last_update_unknown": "Дата последнего обновления базы данных неизвестна.",
        "showing": "Показано",
        "of": "из",
        "minimum": "Минимум",
        "maximum": "Максимум",
    },
    "Eesti": {
        "language": "Keel / Язык",
        "refresh": "Värskenda andmeid",
        "title": "Menüü Hinnad",
        "subtitle": "Võrdle restoranide hindu ja jälgi nende muutumist ajas.",
        "connection_error": "Supabase'iga ühendamine ebaõnnestus. Kontrolli Streamliti seadetes rakenduse Secrets väärtusi.",
        "empty": "Supabase'is pole praegu kuvatavaid tooteid.",
        "filters": "Filtrid",
        "search": "Otsi toodet või restorani",
        "restaurant": "Restoran",
        "all": "Kõik",
        "category": "Kategooria",
        "sort": "Sorteerimine",
        "sort_low": "Odavamad eespool",
        "sort_high": "Kallimad eespool",
        "sort_name": "Nime järgi",
        "items": "Tooteid",
        "restaurants": "Restorane",
        "changes": "Hinna muutusega tooteid",
        "cheapest_dish": "Odavaim roog",
        "cheapest_drink": "Odavaim jook",
        "tab_menu": "Menüü ja hinnad",
        "tab_compare": "Võrdlus",
        "tab_cheapest": "Odavaimad",
        "tab_map": "Kaart",
        "cheapest_heading": "Kõige odavamad tooted kategooriate kaupa",
        "cheapest_empty": "Kuvamiseks pole tooteid.",
        "name": "Toode",
        "variant": "Variant",
        "price": "Praegune hind",
        "old_price": "Eelmine hind",
        "delta": "Muutus",
        "updated": "Uuendatud",
        "no_results": "Valitud filtritega tooteid ei leitud.",
        "compare_heading": "Pakkumiste võrdlus",
        "compare_hint": "Sisesta toote nimi või osa nimest, et näha eri restoranide vasteid. Sarnaste toodete leidmiseks proovi üldist sõna, näiteks „burger” või „kohv”.",
        "compare_search": "Mida võrrelda?",
        "price_down": "Odavam",
        "price_up": "Kallim",
        "same": "Muutuseta",
        "read_only": "Andmebaasi viimati uuendatud: {date}",
        "last_update_unknown": "Andmebaasi viimase uuendamise aeg pole teada.",
        "showing": "Näidatakse",
        "of": "/",
        "minimum": "Miinimum",
        "maximum": "Maksimum",
    },
}

PRODUCT_TYPE_LABELS = {
    "Русский": {
        "burgers": "Бургеры",
        "pizzas": "Пицца",
        "tortillas": "Тортильи",
        "salads": "Салаты",
        "appetizers": "Закуски",
        "sides": "Гарниры",
        "sauces": "Соусы и добавки",
        "syrups": "Сиропы и добавки",
        "desserts": "Десерты",
        "drinks": "Напитки",
        "alcoholic_drinks": "Алкогольные напитки (18+)",
        "breakfast": "Завтраки",
        "campaigns": "Акции",
        "other": "Другое",
        "ice_cream_shakes": "Напитки",
        "sets": "Наборы и комбо",
        "dumplings": "Пельмени и дим-сам",
        "sashimi": "Сашими",
        "nigiri": "Нигири",
        "gunkan": "Гунканы",
        "inari": "Инари",
        "hosomaki": "Хосомаки",
        "tempura": "Темпура",
        "sushi_rolls": "Роллы и маки",
        "soups": "Супы",
        "bowls": "Боулы",
        "noodles": "Лапша",
        "main_courses": "Основные блюда",
    },
    "Eesti": {
        "burgers": "Burgerid",
        "pizzas": "Pitsad",
        "tortillas": "Tortillad",
        "salads": "Salatid",
        "appetizers": "Suupisted",
        "sides": "Lisandid",
        "sauces": "Kastmed ja lisandid",
        "syrups": "Siirupid ja lisandid",
        "desserts": "Magustoidud",
        "drinks": "Joogid",
        "alcoholic_drinks": "Alkohoolsed joogid (18+)",
        "breakfast": "Hommikusöök",
        "campaigns": "Kampaaniad",
        "other": "Muu",
        "ice_cream_shakes": "Joogid",
        "sets": "Komplektid",
        "dumplings": "Pelmeenid ja dim sum",
        "sashimi": "Sashimi",
        "nigiri": "Nigiri",
        "gunkan": "Gunkan",
        "inari": "Inari",
        "hosomaki": "Hosomaki",
        "tempura": "Tempura",
        "sushi_rolls": "Sushirullid ja maki",
        "soups": "Supid",
        "bowls": "Bow'id",
        "noodles": "Nuudlid",
        "main_courses": "Pearoad",
    },
}


def get_text(language):
    return TRANSLATIONS[language]


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data(ttl=30)
def load_table(table_name):
    client = get_supabase_client()
    rows = []
    page_size = 1000
    start = 0

    while True:
        response = (
            client.table(table_name)
            .select("*")
            .range(start, start + page_size - 1)
            .execute()
        )
        page = response.data or []
        rows.extend(page)
        if len(page) < page_size:
            break
        start += page_size

    return pd.DataFrame(rows)


def nonempty(value):
    if value is None or pd.isna(value):
        return None
    value = str(value).strip()
    return value or None


def first_value(row, columns, default=None):
    for column in columns:
        if column in row.index:
            value = nonempty(row[column])
            if value is not None:
                return value
    return default


def normalize_display_category(value, language):
    value = nonempty(value)
    if value is None:
        return "Muu" if language == "Eesti" else "Другое"

    if language == "Eesti" and value.casefold().startswith("hommikupala"):
        return "Hommikupala"

    return value


def categorize_drinks_like(value):
    text = nonempty(value)
    if text is None:
        return "drinks"
    lowered = text.casefold()
    drink_markers = (
        "drink", "drinks", "beverage", "joog", "jook", "kohv", "tee",
        "kokteil", "cocktail", "milkshake", "shake", "alkohol", "alcohol",
        "beer", "wine", "õlu", "vein", "vahuvein", "siider",
        "горячий напиток", "горячие напитки", "напиток", "напитки",
        "коктейл", "алкоголь", "сироп", "siirup", "syrup",
    )
    if any(marker in lowered for marker in drink_markers):
        return "drinks"
    return text


def prepare_dishes(source, language):
    df = source.copy()
    if df.empty:
        return df

    if "restaurant_name" not in df.columns:
        df["restaurant_name"] = None
    if "dish_code" not in df.columns:
        df["dish_code"] = None

    def restaurant_name(row):
        explicit = first_value(row, ["restaurant_name"])
        if explicit:
            return explicit
        code = first_value(row, ["dish_code"], "unknown")
        prefix = code.split(":", 1)[0]
        return prefix.replace("_", " ").title() if ":" in code else "Unknown"

    df["restaurant_display"] = df.apply(restaurant_name, axis=1)
    if "product_type" not in df.columns:
        df["product_type"] = None

    category_source = df[[col for col in ("category_ru", "category_et", "product_type") if col in df.columns]].fillna("").astype(str)
    drink_like_mask = category_source.apply(
        lambda row: any(
            categorize_drinks_like(cell) == "drinks" for cell in row
        ),
        axis=1,
    )
    df.loc[drink_like_mask, "product_type"] = "drinks"

    if language == "Русский":
        df["display_name"] = df.apply(
            lambda row: first_value(row, ["dish_name_ru", "dish_name", "dish_name_et"], "Без названия"),
            axis=1,
        )
    else:
        df["display_name"] = df.apply(
            lambda row: first_value(row, ["dish_name_et", "dish_name", "dish_name_ru"], "Nimetu toode"),
            axis=1,
        )

    syrup_mask = df["display_name"].fillna("").astype(str).str.contains(
        r"(siirup|syrup|siroop|сироп)",
        case=False,
        regex=True,
        na=False,
    )
    df.loc[syrup_mask, "product_type"] = "syrups"

    category_columns = [
        column for column in ("category_ru", "category_et", "product_type")
        if column in df.columns
    ]
    if category_columns:
        sauce_categories = pd.DataFrame(
            {
                column: df[column].fillna("").astype(str).str.strip().str.casefold()
                for column in category_columns
            },
            index=df.index,
        )
        sauces_mask = sauce_categories.eq("kastmed").any(axis=1) | sauce_categories.apply(
            lambda row: any(
                marker in str(row).lower() for marker in ["sauce", "соус", "kastmed", "kastme", "kaste"]
            ),
            axis=1,
        )
        df.loc[sauces_mask, "product_type"] = "sauces"
    
    hesburger_kastmed_item = (
        df["restaurant_display"].fillna("").astype(str).str.contains(
            r"hesburger", case=False, regex=True, na=False
        )
        & df["display_name"].fillna("").astype(str).str.strip().str.casefold().eq("kastmed")
    )
    df.loc[hesburger_kastmed_item, "product_type"] = "sauces"

    name_columns = [column for column in ("dish_name_ru", "dish_name_et", "dish_name") if column in df.columns]
    if name_columns:
        names_by_language = pd.DataFrame(
            {
                column: df[column].fillna("").astype(str).str.strip().str.casefold()
                for column in name_columns
            },
            index=df.index,
        )
        all_names = names_by_language.agg(" ".join, axis=1)

        nuggets_mask = all_names.str.contains(
            r"(tšilli[-\s]?juustunagitsad|chilli?[-\s]?cheese[-\s]?nuggets?|чили[^,;]*наггетс)",
            case=False,
            regex=True,
            na=False,
        )
        df.loc[nuggets_mask, "product_type"] = "appetizers"

        lisandid_mask = names_by_language.eq("lisandid").any(axis=1)
        df.loc[lisandid_mask, "product_type"] = "other"

    # Use product_type as the single canonical category across every restaurant.
    # Original category_ru/category_et values remain untouched in the source columns.
    df["display_category"] = df.apply(
        lambda row: canonical_website_category(row, language),
        axis=1,
    )

    price_source = df["current_price"] if "current_price" in df.columns else pd.Series(pd.NA, index=df.index)
    fallback_price = df["price"] if "price" in df.columns else pd.Series(pd.NA, index=df.index)
    df["display_price"] = pd.to_numeric(price_source, errors="coerce").fillna(
        pd.to_numeric(fallback_price, errors="coerce")
    )

    old_price = df["old_price"] if "old_price" in df.columns else pd.Series(pd.NA, index=df.index)
    df["display_old_price"] = pd.to_numeric(old_price, errors="coerce")

    delta = df["price_delta"] if "price_delta" in df.columns else pd.Series(pd.NA, index=df.index)
    df["display_delta"] = pd.to_numeric(delta, errors="coerce")

    if "last_updated" not in df.columns:
        df["last_updated"] = None
    if "id" not in df.columns:
        df["id"] = df.index.astype(str)
    if "product_type" not in df.columns:
        df["product_type"] = None
    if "price_variant" not in df.columns:
        df["price_variant"] = None

    return df[df["display_price"].notna() & (df["display_price"] > 0)].copy()


def localized_date(value, language):
    if value is None or pd.isna(value) or str(value).strip() == "":
        return "—"
    try:
        dt = pd.to_datetime(value, utc=True)
        return dt.tz_convert("Europe/Tallinn").strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return str(value)


def normalize_display_variant(value, language):
    value = nonempty(value)
    if value is None:
        return "—"

    key = " ".join(value.split()).casefold()
    size_match = re.fullmatch(r"(\d+)\s*tk", key)
    if size_match:
        count = size_match.group(1)
        return f"{count} шт." if language == "Русский" else f"{count} tk"

    labels = {
        "burger": {"Русский": "Только бургер", "Eesti": "Burger üksi"},
        "eine": {"Русский": "Комбо", "Eesti": "Eine"},
        "suur eine": {"Русский": "Большое комбо", "Eesti": "Suur eine"},
        "single": {"Русский": "—", "Eesti": "—"},
        "with topping": {"Русский": "С топпингом", "Eesti": "Lisandiga"},
    }
    return labels.get(key, {}).get(language, value)


def make_display_table(df, language, t):
    result = pd.DataFrame({
        t["restaurant"]: df["restaurant_display"],
        t["category"]: df["display_category"],
        t["name"]: df["display_name"],
        t["variant"]: df["price_variant"].map(lambda value: normalize_display_variant(value, language)),
        t["price"]: df["display_price"],
        t["old_price"]: df["display_old_price"],
        t["delta"]: df["display_delta"],
        t["updated"]: df["last_updated"].map(lambda value: localized_date(value, language)),
    })
    return result


def localized_product_type(value, language):
    key = nonempty(value)
    if key is None:
        key = "other"
    normalized = key.casefold()
    mapped_label = PRODUCT_TYPE_LABELS.get(language, {}).get(normalized)
    if mapped_label:
        return mapped_label
    if any(marker in normalized for marker in ["drink", "joog", "kokteil", "cocktail", "alkohol", "alcohol", "beer", "wine", "напит", "коктейл", "алкогол"]):
        return "Напитки" if language == "Русский" else "Joogid"
    return key.replace("_", " ").capitalize()


def canonical_website_category(row, language):
    """Return one website category while preserving meaningful shared subgroups."""
    product_type = (nonempty(row.get("product_type")) or "other").casefold()
    category_ru = (nonempty(row.get("category_ru")) or "").casefold()
    category_et = (nonempty(row.get("category_et")) or "").casefold()

    # Alcohol is stored under product_type="drinks", but is a separate 18+ group.
    if product_type == "drinks" and (
        "алкогол" in category_ru or "alkohool" in category_et
    ):
        return localized_product_type("alcoholic_drinks", language)

    # These product types intentionally share one public-facing category.
    if product_type == "ice_cream_shakes":
        return localized_product_type("drinks", language)
    if product_type in {"sushi_rolls", "hosomaki"}:
        return localized_product_type("sushi_rolls", language)

    # Tempura rolls are classified as product_type="tempura" by the parser,
    # but their canonical menu category is still rolls. Standalone tempura
    # remains its own category.
    if product_type == "tempura" and (
        category_ru == "роллы" or category_et == "maki"
    ):
        return localized_product_type("sushi_rolls", language)

    return localized_product_type(product_type, language)


def render_cheapest_by_category(df, language, t):
    if df.empty:
        st.info(t["cheapest_empty"])
        return

    work = df.copy()
    if "product_type" not in work.columns:
        work["product_type"] = "other"

    work["category_key"] = (
        work["display_category"]
        .fillna("Другое" if language == "Русский" else "Muu")
        .astype(str)
        .str.strip()
        .replace("", "Другое" if language == "Русский" else "Muu")
        .str.casefold()
    )
    work["name_key"] = work["display_name"].fillna("").astype(str).map(
        lambda value: re.sub(r"[^\w]", "", value.casefold(), flags=re.UNICODE)
    )
    work["restaurant_key"] = work["restaurant_display"].fillna("").astype(str).str.casefold()
    work["variant_key"] = work["price_variant"].map(
        lambda value: re.sub(r"\s+", " ", str(value or "").strip().casefold())
    )
    work["price_key"] = work["display_price"].round(2)
    work = work.drop_duplicates(
        subset=["category_key", "name_key", "restaurant_key", "variant_key", "price_key"]
    )

    category_groups = []
    for category_key, group in work.groupby("category_key", sort=False):
        label = nonempty(group["display_category"].iloc[0]) or ("Другое" if language == "Русский" else "Muu")
        category_groups.append((label, category_key, group))

    category_groups.sort(key=lambda item: (category_emoji(item[1], item[0]) == "➕", item[0].casefold()))

    st.subheader(t["cheapest_heading"])
    st.markdown(
        """
        <style>
        .cheapest-category-title {
            color: #0f766e;
            font-size: 1.25rem;
            font-weight: 750;
            letter-spacing: 0.01em;
            margin: 0.35rem 0 0.75rem 0;
        }
        .cheapest-item-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.7rem 0.85rem;
            margin: 0.35rem 0;
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 0.75rem;
            background: rgba(128, 128, 128, 0.045);
        }
        .cheapest-item-name {
            font-weight: 650;
            line-height: 1.35;
        }
        .cheapest-item-restaurant {
            font-size: 0.88rem;
            opacity: 0.78;
            margin-top: 0.2rem;
        }
        .cheapest-price {
            flex-shrink: 0;
            display: inline-block;
            padding: 0.35rem 0.75rem;
            background: #0f766e;
            color: #ffffff;
            border-radius: 999px;
            font-weight: 750;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }
        .cheapest-category-divider {
            border: 0;
            border-top: 1px solid rgba(128, 128, 128, 0.28);
            margin: 1.15rem 0 1.05rem 0;
        }
        @media (max-width: 560px) {
            .cheapest-item-row { padding: 0.65rem; gap: 0.55rem; }
            .cheapest-item-name { font-size: 0.95rem; }
            .cheapest-price { padding: 0.3rem 0.55rem; font-size: 0.92rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for category_index, (label, category_key, group) in enumerate(category_groups):
        lowest_price = round(float(group["display_price"].min()), 2)
        winners = group[group["display_price"].round(2) == lowest_price].copy()
        winners = winners.sort_values(
            ["display_name", "restaurant_display"],
            key=lambda series: series.astype(str).str.casefold(),
        )

        emoji = category_emoji(category_key, label)
        safe_label = html.escape(f"{emoji} {label}")
        st.markdown(
            f'<div class="cheapest-category-title">{safe_label}</div>',
            unsafe_allow_html=True,
        )

        for _, row in winners.iterrows():
            name = html.escape(str(row["display_name"]))
            restaurant = html.escape(str(row["restaurant_display"]))
            price_text = f"{lowest_price:.2f} €".replace(".", ",") if language == "Русский" else f"{lowest_price:.2f} €"
            safe_price = html.escape(price_text)
            st.markdown(
                f'<div class="cheapest-item-row">'
                f'<div><div class="cheapest-item-name">{name}</div>'
                f'<div class="cheapest-item-restaurant">{restaurant}</div></div>'
                f'<span class="cheapest-price">{safe_price}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        if category_index < len(category_groups) - 1:
            st.markdown(
                '<hr class="cheapest-category-divider">',
                unsafe_allow_html=True,
            )


CATEGORY_EMOJIS = {
    "burgers": "🍔", "pizzas": "🍕", "пицца": "🍕", "pitsad": "🍕", "tortillas": "🌯", "salads": "🥗", "appetizers": "🥟",
    "sides": "🍚", "sauces": "🌶️", "syrups": "🍯", "desserts": "🍰",
    "drinks": "🥤", "alcoholic_drinks": "🍷", "alcoholic drinks": "🍷",
    "alcoholic_beverages": "🍷", "alcohol": "🍷", "alkohol": "🍷",
    "breakfast": "🍳", "campaigns": "🏷️", "other": "➕", "others": "➕",
    "ice_cream_shakes": "🥤", "sets": "📦", "set": "📦", "combo": "📦",
    "dumplings": "🥟", "sashimi": "🍣", "nigiri": "🍣", "gunkan": "🍣",
    "inari": "🍣", "hosomaki": "🍣", "tempura": "🍤", "sushi_rolls": "🍣",
    "sushi rolls": "🍣", "sushirullid": "🍣", "rolls": "🍣", "soups": "🍲",
    "bowls": "🥣", "noodles": "🍜", "main_courses": "🍛",
    "бургеры": "🍔", "бургер": "🍔", "тортильи": "🌯", "салаты": "🥗",
    "закуски": "🥟", "гарниры": "🍚", "гарнир": "🍚", "соусы": "🌶️",
    "соусы и добавки": "🌶️", "сиропы и добавки": "🍯", "десерты": "🍰",
    "напитки": "🥤", "алкогольные напитки": "🍷", "алкоголь": "🍷",
    "завтраки": "🍳", "акции": "🏷️", "другое": "➕", "другие": "➕",
    "молочные коктейли": "🥤", "наборы и комбо": "📦", "наборы": "📦",
    "пельмени и дим-сам": "🥟", "сашими": "🍣", "нигири": "🍣",
    "гунканы": "🍣", "инари": "🍣", "хосомаки": "🍣", "темпура": "🍤",
    "роллы и маки": "🍣", "супы": "🍲", "боулы": "🥣", "лапша": "🍜",
    "основные блюда": "🍛",
    "burgerid": "🍔", "tortillad": "🌯", "salatid": "🥗", "suupisted": "🥟",
    "lisandid": "🍚", "kastmed": "🌶️", "kastmed ja lisandid": "🌶️",
    "siirupid ja lisandid": "🍯", "magustoidud": "🍰", "joogid": "🥤",
    "alkohoolsed joogid": "🍷", "alkohoolised joogid": "🍷", "alkoholjoogid": "🍷",
    "hommikusöök": "🍳", "hommikusöögid": "🍳", "hommikusoogid": "🍳",
    "kampaaniad": "🏷️", "muu": "➕", "muud": "➕",
    "jäätisekokteilid": "🥤", "komplektid": "📦",
    "pelmeenid ja dim sum": "🥟", "eelroad": "🥟", "sashimi": "🍣", "nigiri": "🍣",
    "gunkan": "🍣", "gunkanid": "🍣", "inari": "🍣", "hosomaki": "🍣", "tempura": "🍤",
    "sushirullid ja maki": "🍣", "supid": "🍲", "bow'id": "🥣",
    "nuudlid": "🍜", "pearoad": "🍛", "põhiroad": "🍛", "pohiroad": "🍛", "pqhiroad": "🍛",
}


def category_emoji(*values):
    keys = []
    for value in values:
        value = nonempty(value)
        if value is None:
            continue
        key = re.sub(r"[\s_-]+", " ", value.casefold()).strip()
        keys.append(key)

    if any(re.search(r"(?:алкогол|alkoh|alcohol)", key) for key in keys):
        return "🍷"
    if any(re.search(r"(?:набор|комплект|комбо|сеты?|\bsets?\b|\bcombo\b|komplekt)", key) for key in keys):
        return "📦"
    if any(re.search(r"(?:ролл|\brolls?\b|sushirull|\brullid?\b|maki)", key) for key in keys):
        return "🍣"
    if any(re.search(r"(?:соус|kastm|\bsauces?\b)", key) for key in keys):
        return "🌶️"
    if any(re.search(r"(?:суп|\bsoups?\b|supid)", key) for key in keys):
        return "🍲"
    if any(key in {"гарнир", "гарниры", "lisand", "lisandid", "side", "sides"} for key in keys):
        return "🍚"
    if any(key in {"другое", "другие", "muu", "muud", "other", "others"} for key in keys):
        return "➕"

    normalized_map = {
        re.sub(r"[\s_-]+", " ", key.casefold()).strip(): emoji
        for key, emoji in CATEGORY_EMOJIS.items()
    }
    for key in keys:
        if key in normalized_map:
            return normalized_map[key]
    return "🍽️"


def format_price(value, language):
    try:
        number = f"{float(value):.2f}"
        if language == "Русский":
            number = number.replace(".", ",")
        return f"{number} €"
    except (TypeError, ValueError):
        return "—"


def render_price_cards(df, language, t):
    if df.empty:
        st.info(t["no_results"])
        return

    st.markdown(
        """
        <style>
        .price-card-list { display: flex; flex-direction: column; gap: .55rem; }
        .price-card {
            display: grid;
            grid-template-columns: 2.6rem minmax(0, 1fr) auto auto;
            align-items: center;
            gap: .8rem;
            padding: .85rem 1rem;
            border: 1px solid rgba(128, 128, 128, .24);
            border-radius: 1rem;
            background: rgba(128, 128, 128, .045);
            color: inherit;
        }
        .price-card-icon {
            width: 2.45rem; height: 2.45rem;
            display: flex; align-items: center; justify-content: center;
            border-radius: .8rem;
            background: rgba(128, 128, 128, .12);
            font-size: 1.45rem;
        }
        .price-card-info { min-width: 0; }
        .price-card-name {
            font-weight: 650; line-height: 1.35;
            overflow-wrap: anywhere;
        }
        .price-card-restaurant {
            margin-top: .2rem; font-size: .86rem; opacity: .72;
            overflow-wrap: anywhere;
        }
        .price-card-variant {
            margin-top: .15rem; font-size: .8rem; opacity: .65;
        }
        .price-card-current {
            font-size: 1.08rem; font-weight: 800;
            white-space: nowrap; font-variant-numeric: tabular-nums;
        }
        .price-card-change { margin-left: .22rem; font-size: .95rem; font-weight: 800; }
        .price-card-up { color: #dc4545; }
        .price-card-down { color: #159957; }
        .price-card-old {
            color: inherit; opacity: .58; text-decoration: line-through;
            white-space: nowrap; font-size: .9rem; font-variant-numeric: tabular-nums;
        }
        @media (max-width: 560px) {
            .price-card {
                grid-template-columns: 2.1rem minmax(0, 1fr) auto;
                gap: .55rem; padding: .7rem .65rem; border-radius: .85rem;
            }
            .price-card-icon {
                grid-column: 1; grid-row: 1 / span 2;
                width: 2rem; height: 2rem; font-size: 1.2rem;
            }
            .price-card-info { grid-column: 2; grid-row: 1 / span 2; align-self: center; }
            .price-card-current { grid-column: 3; grid-row: 1; font-size: .98rem; align-self: end; }
            .price-card-old { grid-column: 3; grid-row: 2; justify-self: end; font-size: .8rem; align-self: start; }
            .price-card-restaurant { font-size: .8rem; }
            .price-card-variant { font-size: .75rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cards = ['<div class="price-card-list">']
    for _, row in df.iterrows():
        name = html.escape(str(row.get("display_name", "—")))
        restaurant = html.escape(str(row.get("restaurant_display", "—")))
        product_type = nonempty(row.get("product_type")) or "other"
        emoji = category_emoji(product_type, row.get("display_category"))
        variant = normalize_display_variant(row.get("price_variant"), language)
        variant_html = (
            f'<div class="price-card-variant">{html.escape(variant)}</div>'
            if variant and variant != "—" else ""
        )
        current_price = row.get("display_price")
        old_price = row.get("display_old_price")
        delta = row.get("display_delta")
        try:
            delta_value = float(delta)
            if pd.isna(delta_value):
                delta_value = 0.0
        except (TypeError, ValueError):
            delta_value = 0.0
        if delta_value == 0 and pd.notna(old_price):
            try:
                delta_value = float(current_price) - float(old_price)
            except (TypeError, ValueError):
                delta_value = 0.0

        change_html = ""
        if delta_value > 0:
            change_html = '<span class="price-card-change price-card-up" aria-label="price increased">↑</span>'
        elif delta_value < 0:
            change_html = '<span class="price-card-change price-card-down" aria-label="price decreased">↓</span>'

        old_html = ""
        if pd.notna(old_price) and float(old_price) > 0:
            old_html = f'<div class="price-card-old">{html.escape(format_price(old_price, language))}</div>'

        cards.append(
            '<div class="price-card">'
            f'<div class="price-card-icon" aria-hidden="true">{emoji}</div>'
            f'<div class="price-card-info"><div class="price-card-name">{name}</div>'
            f'<div class="price-card-restaurant">{restaurant}</div>{variant_html}</div>'
            f'<div class="price-card-current">{html.escape(format_price(current_price, language))}{change_html}</div>'
            f'{old_html}'
            '</div>'
        )
    cards.append("</div>")
    st.markdown("".join(cards), unsafe_allow_html=True)


def filter_dishes(df, t):
    st.sidebar.header(t["filters"])
    search = st.sidebar.text_input(t["search"], key="dish_search").strip().casefold()

    restaurants = [t["all"]] + sorted(df["restaurant_display"].dropna().astype(str).unique().tolist())
    selected_restaurant = st.sidebar.selectbox(t["restaurant"], restaurants)

    filtered = df.copy()
    if selected_restaurant != t["all"]:
        filtered = filtered[filtered["restaurant_display"] == selected_restaurant]

    category_values = filtered["display_category"].dropna().astype(str).unique().tolist()
    other_names = {"другое", "другие", "muu", "muud", "other", "others"}
    category_values.sort(key=lambda category: (
        category.casefold() in other_names,
        category.casefold(),
    ))
    categories = [t["all"]] + category_values
    category_options = {
        t["all"]: t["all"],
        **{
            f'{category_emoji(category)}  {category}': category
            for category in categories if category != t["all"]
        },
    }
    selected_category_label = st.sidebar.selectbox(t["category"], list(category_options))
    selected_category = category_options[selected_category_label]
    if selected_category != t["all"]:
        filtered = filtered[filtered["display_category"] == selected_category]

    if search:
        search_cols = ["display_name", "display_category", "restaurant_display", "product_type"]
        mask = pd.Series(False, index=filtered.index)
        for col in search_cols:
            mask = mask | filtered[col].fillna("").astype(str).str.casefold().str.contains(search, regex=False)
        filtered = filtered[mask]

    return filtered


def main():
    language = st.sidebar.radio(
        "🌐 " + "Язык / Keel",
        ["Русский", "Eesti"],
        horizontal=True,
        key="interface_language",
    )
    t = get_text(language)

    if st.sidebar.button(t["refresh"]):
        load_table.clear()
        st.rerun()

    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:16px; margin:0.25rem 0 0.5rem 0;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 170"
               width="92" height="92" role="img" aria-label="Menüü Hinnad Jõhvi logo"
               style="flex:0 0 92px;">
            <g transform="scale(0.92)" transform-origin="85 85">
              <circle cx="85" cy="85" r="81" fill="#ffffff"/>
              <circle cx="85" cy="85" r="82" fill="none" stroke="#000000" stroke-width="3"/>
              <circle cx="85" cy="85" r="74" fill="none" stroke="#000000" stroke-width="1"/>
              <rect x="62" y="30" width="46" height="48" rx="4" fill="none" stroke="#000000" stroke-width="2.5"/>
              <path d="M74 30 v-4 h22 v4 Z" fill="#000000"/>
              <rect x="78" y="23" width="14" height="3" rx="1" fill="#000000"/>
              <text x="82" y="63" font-family="Segoe UI, Helvetica, Arial, sans-serif"
                    font-size="24" font-weight="bold" fill="#000000" text-anchor="middle">€</text>
              <path d="M94 58 l8 8 m0 0 h-6 m6 0 v-6" fill="none" stroke="#000000"
                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="35" y1="88" x2="135" y2="88" stroke="#000000" stroke-width="2"/>
              <text x="85" y="110" font-family="Segoe UI, Helvetica, Arial, sans-serif"
                    font-size="14" font-weight="900" fill="#000000" letter-spacing="1"
                    text-anchor="middle">MENÜÜ HINNAD</text>
              <text x="85" y="130" font-family="Segoe UI, Helvetica, Arial, sans-serif"
                    font-size="14" font-weight="900" fill="#000000" letter-spacing="4"
                    text-anchor="middle">JÕHVI</text>
            </g>
          </svg>
          <h1 style="margin:0; padding:0; line-height:1.15; font-size:2.35rem; font-family:Segoe UI, Helvetica, Arial, sans-serif; text-transform:uppercase;">
            {html.escape(t["title"])}
          </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:0.95rem; line-height:1.4; margin-top:0.1rem; margin-bottom:0.9rem;">{html.escape(t["subtitle"])}</div>',
        unsafe_allow_html=True,
    )

    try:
        source = load_table("dishes")
    except Exception:
        st.error(t["connection_error"])
        st.info(
            "Streamlit → App settings → Secrets: add SUPABASE_URL and SUPABASE_KEY. SUPABASE_KEY must be the public publishable/anon key; RLS controls read access."
            if language == "Русский"
            else "Streamlit → App settings → Secrets: lisa SUPABASE_URL ja SUPABASE_KEY. SUPABASE_KEY peab olema avalik publishable/anon-võti; lugemisõigust juhib RLS."
        )
        st.stop()

    latest_update = None
    if "last_updated" in source.columns:
        update_times = pd.to_datetime(source["last_updated"], errors="coerce", utc=True)
        if update_times.notna().any():
            latest_update = update_times.max()

    if latest_update is not None and pd.notna(latest_update):
        update_text = latest_update.tz_convert("Europe/Tallinn").strftime("%d.%m.%Y %H:%M")
        st.caption(t["read_only"].format(date=update_text))
    else:
        st.caption(t["last_update_unknown"])

    if source.empty:
        st.info(t["empty"])
        st.stop()

    dishes = prepare_dishes(source, language)
    if dishes.empty:
        st.info(t["empty"])
        st.stop()

    filtered = filter_dishes(dishes, t)

    total_items = len(filtered)
    m1, m2, m3, m4, m5 = st.columns(5)
    if filtered.empty:
        m1.metric(t["items"], "0")
        m2.metric(t["restaurants"], "0")
        m3.metric(t["changes"], "0")
        m4.metric(t["cheapest_dish"], "—")
        m5.metric(t["cheapest_drink"], "—")
    else:
        total_restaurants = filtered["restaurant_display"].nunique()
        price_changes = int((filtered["display_delta"].fillna(0) != 0).sum())

        category_columns = [
            column for column in ("display_category", "category_ru", "category_et", "product_type")
            if column in filtered.columns
        ]
        category_text = (
            filtered[category_columns]
            .fillna("")
            .astype(str)
            .agg(" ".join, axis=1)
            .str.casefold()
        )

        non_dish_pattern = (
            r"друг|muu|other|напит|joogi|drink|"
            r"соус|kastmed|sauce|сироп|siirup|syrup|"
            r"алкогол|alcohol|alkohol|alkohool"
        )
        non_dish_mask = category_text.str.contains(non_dish_pattern, regex=True, na=False)
        eligible_dishes = filtered[~non_dish_mask]

        drink_pattern = (
            r"напит|joogi|drink|алкогол|alcohol|"
            r"alkohol|alkohool|kokteil|cocktail"
        )
        drink_mask = category_text.str.contains(drink_pattern, regex=True, na=False)
        eligible_drinks = filtered[drink_mask]

        m1.metric(t["items"], f"{total_items:,}".replace(",", " "))
        m2.metric(t["restaurants"], f"{total_restaurants:,}".replace(",", " "))
        m3.metric(t["changes"], f"{price_changes:,}".replace(",", " "))

        if eligible_dishes.empty:
            m4.metric(t["cheapest_dish"], "—")
        else:
            cheapest_dish = eligible_dishes.loc[eligible_dishes["display_price"].idxmin()]
            m4.metric(
                t["cheapest_dish"],
                f'{cheapest_dish["display_price"]:.2f} €',
            )
            m4.caption(
                f'{html.escape(str(cheapest_dish["display_name"]))} · '
                f'{html.escape(str(cheapest_dish["restaurant_display"]))}'
            )

        if eligible_drinks.empty:
            m5.metric(t["cheapest_drink"], "—")
        else:
            cheapest_drink = eligible_drinks.loc[eligible_drinks["display_price"].idxmin()]
            m5.metric(
                t["cheapest_drink"],
                f'{cheapest_drink["display_price"]:.2f} €',
            )
            m5.caption(
                f'{html.escape(str(cheapest_drink["display_name"]))} · '
                f'{html.escape(str(cheapest_drink["restaurant_display"]))}'
            )

    tab_menu, tab_cheapest, tab_map = st.tabs(
        [t["tab_menu"], t["tab_cheapest"], t["tab_map"]]
    )

    with tab_menu:
        if filtered.empty:
            st.info(t["no_results"])
        else:
            sort_label = st.selectbox(
                t["sort"],
                [t["sort_low"], t["sort_high"], t["sort_name"]],
                key="menu_sort",
            )
            if sort_label == t["sort_low"]:
                display_df = filtered.sort_values("display_price", ascending=True)
            elif sort_label == t["sort_high"]:
                display_df = filtered.sort_values("display_price", ascending=False)
            else:
                display_df = filtered.sort_values("display_name", key=lambda s: s.str.casefold())

            st.caption(f'{t["showing"]} {len(display_df)} {t["of"]} {len(dishes)}')
            render_price_cards(display_df, language, t)

    with tab_cheapest:
        render_cheapest_by_category(dishes, language, t)

    with tab_map:
        st.components.v1.iframe(
            "https://www.google.com/maps/d/embed?mid=1g0ENhUYBVXlcUtNfX4WKK3Fl2osnMwA&ehbc=2E312F&noprof=1",
            height=680,
            scrolling=True,
        )


if __name__ == "__main__":
    main()
