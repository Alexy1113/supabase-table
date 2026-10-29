# Menuu Hinnad

Bilingual Streamlit app for browsing restaurant menu prices in Russian and Estonian, comparing current offers, and viewing price history from Supabase.

## Streamlit configuration

In Streamlit Community Cloud, open **App settings → Secrets** and add the project's **public publishable/anon key** (never a server-side secret key):

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLIC_PUBLISHABLE_OR_ANON_KEY"
```

The app only reads data. Supabase RLS must allow `SELECT` on `public.dishes` for `anon`, plus `SELECT` on `public.price_history`.

## Data display rules

- Russian name: `dish_name_ru`, fallback to `dish_name`, then `dish_name_et`.
- Estonian name: `dish_name_et`, fallback to `dish_name`, then `dish_name_ru`.
- Russian category: `category_ru`, fallback to `product_type`.
- Estonian category: `category_et`, fallback to `product_type`.
- Current price: `current_price`, fallback to `price`.
- The restaurant is read from `restaurant_name`, not inferred from `dish_code`.

## Price history

Run the SQL in `supabase_price_history.sql` in Supabase SQL Editor to create the read-only public history table. The parser repository must also insert an initial history row for new products and a row when a price changes; the website cannot reconstruct a full past timeline from `old_price` alone.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
streamlit run app.py
```

Keep local `.env` files out of Git. Never put Supabase secret/service-role keys in this website repository or in Streamlit's public-facing source code.
