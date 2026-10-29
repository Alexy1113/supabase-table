import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Menuu Hinnad",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

TRANSLATIONS = {
    "Русский": {
        "language": "Язык / Keel",
        "title": "Menuu Hinnad",
        "subtitle": "Сравнивайте цены в ресторанах и следите за их изменениями.",
        "connection_error": "Не удалось подключиться к Supabase. Проверь Secrets приложения в настройках Streamlit.",
        "empty": "В Supabase пока нет блюд для отображения.",
        "filters": "Фильтры",
        "search": "Поиск блюда или ресторана",
        "restaurant": "Ресторан",
        "all": "Все",
        "category": "Категория",
        "type": "Тип продукта",
        "sort": "Сортировка",
        "sort_low": "Сначала дешевле",
        "sort_high": "Сначала дороже",
        "sort_name": "По названию",
        "items": "Позиций",
        "restaurants": "Ресторанов",
        "changes": "Позиций с изменением цены",
        "cheapest": "Самая низкая цена в выборке",
        "tab_menu": "Меню и цены",
        "tab_compare": "Сравнение",
        "tab_history": "История цены",
        "name": "Блюдо / продукт",
        "variant": "Вариант",
        "price": "Текущая цена",
        "old_price": "Предыдущая цена",
        "delta": "Изменение",
        "updated": "Обновлено",
        "no_results": "По заданным фильтрам ничего не найдено.",
        "compare_heading": "Сравнение предложений",
        "compare_hint": "Введите название или часть названия, чтобы увидеть подходящие позиции разных ресторанов. Для сравнения похожих товаров попробуйте общее слово, например «burger» или «kohv».",
        "compare_search": "Что сравнить?",
        "history_heading": "История изменения цены",
        "choose_item": "Выберите позицию",
        "history_missing": "Таблица истории ещё не настроена или недоступна. Сначала выполни SQL из файла supabase_price_history.sql в Supabase, затем добавим запись истории в парсер.",
        "history_empty": "Для этой позиции пока нет записей истории. После настройки парсера здесь будут сохраняться начальная цена и каждое обнаруженное изменение.",
        "history_chart": "Изменение цены во времени",
        "history_table": "Записи истории",
        "date": "Дата и время",
        "history_price": "Цена",
        "current": "Сейчас",
        "previous": "До этого",
        "price_down": "Дешевле",
        "price_up": "Дороже",
        "same": "Без изменения",
        "read_only": "Сайт работает в режиме просмотра: посетители могут читать меню, но не изменять цены.",
        "all_types": "Все типы",
        "showing": "Показано",
        "of": "из",
        "minimum": "Минимум",
        "maximum": "Максимум",
    },
    "Eesti": {
        "language": "Keel / Язык",
        "title": "Menuu Hinnad",
        "subtitle": "Võrdle restoranide hindu ja jälgi nende muutumist ajas.",
        "connection_error": "Supabase'iga ühendamine ebaõnnestus. Kontrolli Streamliti seadetes rakenduse Secrets väärtusi.",
        "empty": "Supabase'is pole praegu kuvatavaid tooteid.",
        "filters": "Filtrid",
        "search": "Otsi toodet või restorani",
        "restaurant": "Restoran",
        "all": "Kõik",
        "category": "Kategooria",
        "type": "Toote tüüp",
        "sort": "Sorteerimine",
        "sort_low": "Odavamad eespool",
        "sort_high": "Kallimad eespool",
        "sort_name": "Nime järgi",
        "items": "Tooteid",
        "restaurants": "Restorane",
        "changes": "Hinna muutusega tooteid",
        "cheapest": "Valiku madalaim hind",
        "tab_menu": "Menüü ja hinnad",
        "tab_compare": "Võrdlus",
        "tab_history": "Hinna ajalugu",
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
        "history_heading": "Hinna muutumise ajalugu",
        "choose_item": "Vali toode",
        "history_missing": "Hinnaajaloo tabel pole veel seadistatud või pole saadaval. Käivita Supabase'is failis supabase_price_history.sql olev SQL; seejärel lisame ajaloo salvestamise parserisse.",
        "history_empty": "Selle toote kohta pole veel ajaloosissekandeid. Pärast parseri seadistamist salvestatakse algne hind ja iga tuvastatud hinnamuutus.",
        "history_chart": "Hinna muutumine ajas",
        "history_table": "Ajalookirjed",
        "date": "Kuupäev ja kellaaeg",
        "history_price": "Hind",
        "current": "Praegu",
        "previous": "Varem",
        "price_down": "Odavam",
        "price_up": "Kallim",
        "same": "Muutuseta",
        "read_only": "Veebileht on vaaterežiimis: külastajad saavad menüüd lugeda, kuid ei saa hindu muuta.",
        "all_types": "Kõik tüübid",
        "showing": "Näidatakse",
        "of": "/",
        "minimum": "Miinimum",
        "maximum": "Maksimum",
    },
}


def get_text(language):
    return TRANSLATIONS[language]


@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]  # Use the public publishable/anon key, never a secret key here.
    return create_client(url, key)


@st.cache_data(ttl=120)
def load_table(table_name):
    """Read rows in pages so menus larger than the API default limit are included."""
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


def prepare_dishes(source, language):
    df = source.copy()
    if df.empty:
        return df

    # Use the actual restaurant_name column. dish_code is an item identifier,
    # not a reliable restaurant identifier (Ocean Sushi codes may be numeric).
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

    if language == "Русский":
        df["display_name"] = df.apply(
            lambda row: first_value(row, ["dish_name_ru", "dish_name", "dish_name_et"], "Без названия"),
            axis=1,
        )
        df["display_category"] = df.apply(
            lambda row: first_value(row, ["category_ru", "product_type"], "Другое"),
            axis=1,
        )
    else:
        df["display_name"] = df.apply(
            lambda row: first_value(row, ["dish_name_et", "dish_name", "dish_name_ru"], "Nimetu toode"),
            axis=1,
        )
        df["display_category"] = df.apply(
            lambda row: first_value(row, ["category_et", "product_type"], "Muu"),
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


def make_display_table(df, language, t):
    result = pd.DataFrame({
        t["restaurant"]: df["restaurant_display"],
        t["category"]: df["display_category"],
        t["name"]: df["display_name"],
        t["variant"]: df["price_variant"].fillna("—").astype(str),
        t["price"]: df["display_price"],
        t["old_price"]: df["display_old_price"],
        t["delta"]: df["display_delta"],
        t["updated"]: df["last_updated"].map(lambda value: localized_date(value, language)),
    })
    return result


def filter_dishes(df, t):
    st.sidebar.header(t["filters"])
    search = st.sidebar.text_input(t["search"], key="dish_search").strip().casefold()

    restaurants = [t["all"]] + sorted(df["restaurant_display"].dropna().astype(str).unique().tolist())
    selected_restaurant = st.sidebar.selectbox(t["restaurant"], restaurants)

    filtered = df.copy()
    if selected_restaurant != t["all"]:
        filtered = filtered[filtered["restaurant_display"] == selected_restaurant]

    categories = [t["all"]] + sorted(filtered["display_category"].dropna().astype(str).unique().tolist())
    selected_category = st.sidebar.selectbox(t["category"], categories)
    if selected_category != t["all"]:
        filtered = filtered[filtered["display_category"] == selected_category]

    product_types = [t["all_types"]] + sorted(
        filtered["product_type"].dropna().astype(str).unique().tolist()
    )
    selected_type = st.sidebar.selectbox(t["type"], product_types)
    if selected_type != t["all_types"]:
        filtered = filtered[filtered["product_type"].astype(str) == selected_type]

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

    st.title("🍽️ " + t["title"])
    st.caption(t["subtitle"])
    st.caption(t["read_only"])

    try:
        source = load_table("dishes")
    except Exception:
        st.error(t["connection_error"])
        st.info(
            "Streamlit → App settings → Secrets: add SUPABASE_URL and SUPABASE_KEY. "
            "SUPABASE_KEY must be the public publishable/anon key; RLS controls read access."
            if language == "Русский"
            else "Streamlit → App settings → Secrets: lisa SUPABASE_URL ja SUPABASE_KEY. "
                 "SUPABASE_KEY peab olema avalik publishable/anon-võti; lugemisõigust juhib RLS."
        )
        st.stop()

    if source.empty:
        st.info(t["empty"])
        st.stop()

    dishes = prepare_dishes(source, language)
    if dishes.empty:
        st.info(t["empty"])
        st.stop()

    filtered = filter_dishes(dishes, t)

    total_items = len(filtered)
    m1, m2, m3, m4 = st.columns(4)
    if filtered.empty:
        m1.metric(t["items"], "0")
        m2.metric(t["restaurants"], "0")
        m3.metric(t["changes"], "0")
        m4.metric(t["cheapest"], "—")
    else:
        total_restaurants = filtered["restaurant_display"].nunique()
        price_changes = int((filtered["display_delta"].fillna(0) != 0).sum())
        cheapest = filtered.loc[filtered["display_price"].idxmin()]
        m1.metric(t["items"], f"{total_items:,}".replace(",", " "))
        m2.metric(t["restaurants"], f"{total_restaurants:,}".replace(",", " "))
        m3.metric(t["changes"], f"{price_changes:,}".replace(",", " "))
        m4.metric(
            t["cheapest"],
            f'{cheapest["display_price"]:.2f} €',
            help=f'{cheapest["display_name"]} — {cheapest["restaurant_display"]}',
        )

    tab_menu, tab_compare, tab_history = st.tabs(
        [t["tab_menu"], t["tab_compare"], t["tab_history"]]
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

            table = make_display_table(display_df, language, t)
            st.caption(f'{t["showing"]} {len(table)} {t["of"]} {len(dishes)}')
            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    t["price"]: st.column_config.NumberColumn(t["price"], format="€ %.2f"),
                    t["old_price"]: st.column_config.NumberColumn(t["old_price"], format="€ %.2f"),
                    t["delta"]: st.column_config.NumberColumn(t["delta"], format="€ %+.2f"),
                },
            )

    with tab_compare:
        st.subheader(t["compare_heading"])
        st.write(t["compare_hint"])
        query = st.text_input(t["compare_search"], key="compare_search").strip().casefold()
        compare_df = dishes.copy()
        if query:
            compare_df = compare_df[
                compare_df["display_name"].fillna("").astype(str).str.casefold().str.contains(query, regex=False)
            ]
        if compare_df.empty:
            st.info(t["no_results"])
        else:
            compare_df = compare_df.sort_values("display_price", ascending=True)
            table = make_display_table(compare_df, language, t)
            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    t["price"]: st.column_config.NumberColumn(t["price"], format="€ %.2f"),
                    t["old_price"]: st.column_config.NumberColumn(t["old_price"], format="€ %.2f"),
                    t["delta"]: st.column_config.NumberColumn(t["delta"], format="€ %+.2f"),
                },
            )
            cheapest_price = compare_df["display_price"].min()
            lowest = compare_df[compare_df["display_price"] == cheapest_price]
            lowest_names = ", ".join(
                f'{row["display_name"]} ({row["restaurant_display"]})'
                for _, row in lowest.head(3).iterrows()
            )
            st.success(
                (f'Низшая найденная цена: {cheapest_price:.2f} € — {lowest_names}'
                 if language == "Русский"
                 else f'Leitud madalaim hind: {cheapest_price:.2f} € — {lowest_names}')
            )

    with tab_history:
        st.subheader(t["history_heading"])
        selected_index = st.selectbox(
            t["choose_item"],
            options=dishes.index.tolist(),
            format_func=lambda idx: (
                f'{dishes.loc[idx, "display_name"]} — '
                f'{dishes.loc[idx, "restaurant_display"]} '
                f'({dishes.loc[idx, "display_price"]:.2f} €)'
            ),
            key="history_item",
        )
        selected = dishes.loc[selected_index]

        price_col1, price_col2, price_col3 = st.columns(3)
        price_col1.metric(t["current"], f'{selected["display_price"]:.2f} €')
        if pd.notna(selected["display_old_price"]):
            price_col2.metric(
                t["previous"],
                f'{selected["display_old_price"]:.2f} €',
                delta=(
                    f'{selected["display_delta"]:+.2f} €'
                    if pd.notna(selected["display_delta"]) else None
                ),
            )
        else:
            price_col2.metric(t["previous"], "—")
        price_col3.metric(
            t["updated"],
            localized_date(selected.get("last_updated"), language),
        )

        try:
            history = load_table("price_history")
            history_error = None
        except Exception as exc:
            history = pd.DataFrame()
            history_error = str(exc)

        if history_error:
            st.warning(t["history_missing"])
        elif history.empty:
            st.info(t["history_empty"])
        else:
            selected_id = str(selected.get("id", ""))
            selected_code = str(selected.get("dish_code", ""))
            match = pd.Series(False, index=history.index)

            if "dish_id" in history.columns and selected_id:
                match = match | (history["dish_id"].astype(str) == selected_id)
            if "dish_code" in history.columns and selected_code and selected_code != "None":
                match = match | (history["dish_code"].astype(str) == selected_code)
            if "restaurant_name" in history.columns:
                match = match & (
                    history["restaurant_name"].astype(str)
                    == str(selected["restaurant_display"])
                )

            item_history = history[match].copy()
            if not item_history.empty and {"recorded_at", "price"}.issubset(item_history.columns):
                item_history["recorded_at"] = pd.to_datetime(
                    item_history["recorded_at"], errors="coerce", utc=True
                )
                item_history["price"] = pd.to_numeric(item_history["price"], errors="coerce")
                item_history = item_history.dropna(subset=["recorded_at", "price"]).sort_values("recorded_at")

            if item_history.empty:
                st.info(t["history_empty"])
            else:
                st.markdown(f"**{t['history_chart']}**")
                chart_data = item_history.set_index("recorded_at")[["price"]].rename(
                    columns={"price": t["history_price"]}
                )
                st.line_chart(chart_data, y=t["history_price"], use_container_width=True)
                history_table = item_history[["recorded_at", "price"]].copy()
                history_table["recorded_at"] = history_table["recorded_at"].map(
                    lambda value: localized_date(value, language)
                )
                history_table.columns = [t["date"], t["history_price"]]
                st.markdown(f"**{t['history_table']}**")
                st.dataframe(
                    history_table.sort_values(t["date"], ascending=False),
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        t["history_price"]: st.column_config.NumberColumn(
                            t["history_price"], format="€ %.2f"
                        )
                    },
                )


if __name__ == "__main__":
    main()
