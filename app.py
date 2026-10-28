import streamlit as st
import pandas as pd
from supabase import create_client

# Настраиваем внешний вид страницы (делаем ее широкой)
st.set_page_config(page_title="Меню Hesburger", layout="wide", page_icon="🍔")

st.title("🍔 Актуальное меню и цены Hesburger")
st.write("Данные загружаются в реальном времени напрямую из базы данных Supabase.")

# Инициализация подключения к Supabase (ключи безопасно берутся из настроек хостинга)
@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Функция загрузки данных с кэшированием на 5 минут (чтобы сайт работал быстро и не перегружал Supabase при наплыве людей)
@st.cache_data(ttl=300)
def load_data():
    supabase = get_supabase_client()
    # Замените 'dishes', если ваша таблица в Supabase называется иначе
    response = supabase.table("dishes").select("*").execute()
    return pd.DataFrame(response.data)

try:
    # Загружаем данные в таблицу
    df = load_data()

    # Поиск по меню
    search_query = st.text_input("🔍 Быстрый поиск по названию или категории:", "")
    
    if search_query:
        # Ищем совпадения в эстонском названии или категории
        df = df[df['dish_name_et'].str.contains(search_query, case=False, na=False) | 
                df['category_et'].str.contains(search_query, case=False, na=False)]

    # Тюнинг отображения таблицы для пользователей
    st.dataframe(
        df,
        use_container_width=True, # Растянуть на весь экран
        hide_index=True,          # Скрыть системные ID строк
        column_order=["dish_name_et", "category_et", "price_variant", "price", "product_url"],
        column_config={
            "dish_name_et": "Название",
            "category_et": "Категория",
            "price_variant": "Вариант",
            "price": st.column_config.NumberColumn("Цена (€)", format="%.2f"),
            "product_url": st.column_config.LinkColumn("Ссылка на продукт")
        }
    )

except Exception as e:
    st.error("Произошла ошибка при подключении к базе данных.")
    st.caption(f"Технические детали: {str(e)}")
