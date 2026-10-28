import streamlit as st
import pandas as pd
from supabase import create_client

# Настройка страницы
st.set_page_config(page_title="Menu Monitor", layout="wide", page_icon="📊")

# Инициализация подключения к Supabase
@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Загрузка данных с кэшированием на 5 минут
@st.cache_data(ttl=300)
def load_data():
    supabase = get_supabase_client()
    response = supabase.table("dishes").select("*").execute()
    df = pd.DataFrame(response.data)
    
    # Извлекаем название ресторана из dish_code (берем текст до первого двоеточия)
    if 'dish_code' in df.columns:
        df['restaurant'] = df['dish_code'].apply(lambda x: str(x).split(':')[0].capitalize() if pd.notna(x) else "Unknown")
    else:
        df['restaurant'] = "Hesburger"
        
    return df

try:
    base_df = load_data()

    # --- ИНТЕРФЕЙС: ВЫБОР ЯЗЫКА ---
    lang = st.radio("🌐 Язык интерфейса / Keel:", ["Русский", "Eesti"], horizontal=True)

    # --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ЯЗЫКОВЫХ КОЛОНОК ---
    working_df = base_df.copy()

    if lang == "Русский":
        # Название блюда: dish_name_ru -> если пусто -> dish_name_et
        name_col = 'dish_name_ru' if 'dish_name_ru' in working_df.columns else 'dish_name_et'
        working_df['display_name'] = working_df[name_col].replace('', None).fillna(working_df['dish_name_et'])
        
        # Категория: category_ru -> если пусто -> product_type -> если пусто -> category_et
        cat_col = 'category_ru' if 'category_ru' in working_df.columns else 'category_et'
        working_df['display_category'] = working_df[cat_col].replace('', None).fillna(working_df.get('product_type', None)).fillna(working_df['category_et'])
        
        # Заголовки для таблицы на русском
        labels = {
            "restaurant": "Ресторан",
            "category": "Категория",
            "name": "Название блюда",
            "price": "Цена (€)",
            "old_price": "Прошлая цена (€)",
            "diff": "Разница / Вариант"
        }
    else:
        # Для эстонского: dish_name_et -> если пусто -> dish_name_ru
        working_df['display_name'] = working_df['dish_name_et'].replace('', None).fillna(working_df.get('dish_name_ru', ''))
        
        # Категория: category_et -> если пусто -> product_type -> если пусто -> category_ru
        working_df['display_category'] = working_df['category_et'].replace('', None).fillna(working_df.get('product_type', None)).fillna(working_df.get('category_ru', ''))
        
        # Заголовки для таблицы на эстонском
        labels = {
            "restaurant": "Restoran",
            "category": "Kategooria",
            "name": "Toote nimetus",
            "price": "Hind (€)",
            "old_price": "Endine hind (€)",
            "diff": "Vahe / Variant"
        }

    # Подстраховка на случай, если старой цены в базе физически нет
    if 'old_price' not in working_df.columns:
        working_df['old_price'] = "-"

    # --- ИНТЕРФЕЙС: ФИЛЬТРЫ ---
    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        restaurants = ["Все / Kõik"] + sorted(list(working_df['restaurant'].unique()))
        selected_restaurant = st.selectbox("🏪 Выберите ресторан / Valige restoran:", restaurants)
        
    with col2:
        if selected_restaurant != "Все / Kõik":
            temp_df = working_df[working_df['restaurant'] == selected_restaurant]
        else:
            temp_df = working_df
            
        categories = ["Все / Kõik"] + sorted(list(temp_df['display_category'].dropna().unique()))
        selected_category = st.selectbox("🗂️ Выберите категорию / Valige kategooria:", categories)

    # --- ФИЛЬТРАЦИЯ ДАННЫХ ---
    if selected_restaurant != "Все / Kõik":
        working_df = working_df[working_df['restaurant'] == selected_restaurant]
        
    if selected_category != "Все / Kõik":
        working_df = working_df[working_df['display_category'] == selected_category]

    # --- ВЫВОД ТАБЛИЦЫ ---
    st.write("")
    
    # Берем готовые данные из price_variant вместо математического расчета
    final_df = working_df[["restaurant", "display_category", "display_name", "price", "old_price", "price_variant"]]
    
    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "restaurant": labels["restaurant"],
            "display_category": labels["category"],
            "display_name": labels["name"],
            "price": st.column_config.NumberColumn(labels["price"], format="%.2f"),
            "old_price": labels["old_price"],
            "price_variant": labels["diff"]
        }
    )

except Exception as e:
    st.error("Ошибка отображения данных. Проверьте названия колонок в Supabase.")
    st.caption(f"Техническая информация: {str(e)}")
