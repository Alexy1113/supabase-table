# Menuu Hinnad

A bilingual Streamlit website for browsing and comparing restaurant menu prices in Russian and Estonian.

## Streamlit configuration

In Streamlit Community Cloud, open **App settings → Secrets** and add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLIC_PUBLISHABLE_OR_ANON_KEY"
```

Use only the public publishable/anon key on the website, never a Supabase secret or service-role key. The public role must have SELECT permission and an RLS read policy for `public.dishes`.

## Data display rules

- Russian name: `dish_name_ru`, fallback to `dish_name`.
- Estonian name: `dish_name_et`, fallback to `dish_name`.
- Russian category: `category_ru`, fallback to `product_type`.
- Estonian category: `category_et`, fallback to `product_type`.
- Variant / difference column: `price_variant`.
- Current price: `current_price`, falling back to `price`.
- The restaurant name is read from `restaurant_name`.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
streamlit run app.py
```

Keep local `.env` files out of Git. Never put Supabase secret/service-role keys in this website repository or in Streamlit's public-facing source code.
