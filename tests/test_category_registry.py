"""Integration checks proving the website uses the shared category package."""
import unittest

from app import canonical_website_category
from restaurant_taxonomy import (
    category_label,
    get_category_emoji,
    resolve_category_key,
)


class WebsiteCategoryRegistryTests(unittest.TestCase):
    def test_canonical_labels_match_the_shared_registry(self):
        expected = {
            "sets": ("Наборы и комбо", "Komplektid"),
            "sushi_rolls": ("Роллы и маки", "Sushirullid ja maki"),
            "sauces": ("Соусы и добавки", "Kastmed ja lisandid"),
            "syrups": ("Сиропы и добавки", "Siirupid ja lisandid"),
            "breakfast": ("Завтраки", "Hommikusöök"),
            "main_courses": ("Основные блюда", "Pearoad"),
            "gunkan": ("Гунканы", "Gunkan"),
            "bowls": ("Боулы", "Bow'id"),
            "tortillas": ("Тортильи", "Tortillad"),
            "hot_dogs": ("Хот-доги", "Hot dogid"),
            "noodles_pasta": ("Лапша и Паста", "Nuudlid ja pasta"),
        }
        for key, (ru, et) in expected.items():
            with self.subTest(category=key):
                self.assertEqual(category_label(key, "Русский"), ru)
                self.assertEqual(category_label(key, "Eesti"), et)

    def test_legacy_product_types_resolve_to_shared_categories(self):
        self.assertEqual(resolve_category_key("noodles"), "noodles_pasta")
        self.assertEqual(resolve_category_key("pasta"), "noodles_pasta")
        self.assertEqual(resolve_category_key("hosomaki"), "sushi_rolls")
        self.assertEqual(resolve_category_key("ice_cream_shakes"), "drinks")
        self.assertEqual(resolve_category_key("tortillas"), "tortillas")
        self.assertEqual(resolve_category_key("hotdog"), "hot_dogs")
        self.assertEqual(resolve_category_key("hot_dog"), "hot_dogs")
        self.assertEqual(resolve_category_key("hotdogs"), "hot_dogs")

    def test_category_boundaries_are_preserved(self):
        self.assertEqual(
            resolve_category_key("drinks", "Напитки", "Joogid"),
            "drinks",
        )
        self.assertEqual(
            resolve_category_key("drinks", "Алкогольные напитки (18+)", "Joogid"),
            "alcoholic_drinks",
        )
        self.assertNotEqual(resolve_category_key("appetizers"), resolve_category_key("sides"))
        self.assertNotEqual(resolve_category_key("sushi_rolls"), resolve_category_key("nigiri"))
        self.assertNotEqual(resolve_category_key("sushi_rolls"), resolve_category_key("sashimi"))
        self.assertNotEqual(resolve_category_key("sauces"), resolve_category_key("syrups"))

    def test_website_uses_shared_resolver_for_legacy_rows(self):
        cases = (
            (
                {"product_type": "tortillas", "category_ru": "Врапы и шаурма", "category_et": "Wrapid ja kebabid"},
                "Тортильи",
                "Tortillad",
            ),
            (
                {"product_type": "sets", "category_ru": "Сеты", "category_et": "Komplektid"},
                "Наборы и комбо",
                "Komplektid",
            ),
            (
                {"product_type": "sushi_rolls", "category_ru": "Роллы", "category_et": "Maki"},
                "Роллы и маки",
                "Sushirullid ja maki",
            ),
            (
                {"product_type": "drinks", "category_ru": "Алкогольные напитки (18+)", "category_et": "Alkohoolsed joogid (18+)"},
                "Алкогольные напитки (18+)",
                "Alkohoolsed joogid (18+)",
            ),
            (
                {"product_type": "main_courses", "category_ru": "Hot Dog", "category_et": "Hot Dog"},
                "Хот-доги",
                "Hot dogid",
            ),
            (
                {"product_type": "main_courses", "category_ru": "Основные блюда", "category_et": "Pearoad",
                 "dish_name_ru": "Classic hot dog"},
                "Хот-доги",
                "Hot dogid",
            ),
            (
                {"product_type": "tempura", "category_ru": "Темпура", "category_et": "Tempura"},
                "Темпура",
                "Tempura",
            ),
        )
        for row, expected_ru, expected_et in cases:
            with self.subTest(row=row):
                self.assertEqual(canonical_website_category(row, "Русский"), expected_ru)
                self.assertEqual(canonical_website_category(row, "Eesti"), expected_et)

    def test_all_break_time_hot_dogs_use_hot_dogs_even_when_legacy_type_is_tortillas(self):
        rows = (
            {
                "restaurant_name": "Break Time Burger & Wrap",
                "product_type": "tortillas",
                "category_ru": "Hot Dog",
                "category_et": "Hot Dog",
                "dish_name_ru": "Hot dog в лаваше",
            },
            {
                "restaurant_name": "Break Time Burger & Wrap",
                "product_type": "tortillas",
                "category_ru": "Основные блюда",
                "category_et": "Pearoad",
                "dish_name_et": "Klassikaline Hot-Dogid",
            },
        )
        for row in rows:
            with self.subTest(row=row):
                self.assertEqual(canonical_website_category(row, "Русский"), "Хот-доги")
                self.assertEqual(canonical_website_category(row, "Eesti"), "Hot dogid")

    def test_break_time_hot_dog_combos_remain_sets(self):
        wrap = {
            "restaurant_name": "Break Time Burger & Wrap",
            "product_type": "tortillas",
            "category_ru": "Врапы и шаурма",
            "category_et": "Wrapid ja kebabid",
            "dish_name_ru": "Chicken wrap",
        }
        combo = {
            "restaurant_name": "Break Time Burger & Wrap",
            "product_type": "sets",
            "category_ru": "Hot Dog",
            "category_et": "Hot Dog",
            "dish_name_ru": "Hot Dog Menu",
        }
        legacy_combo = {
            "restaurant_name": "Break Time Burger & Wrap",
            "product_type": "hot_dogs",
            "category_ru": "Hot Dog",
            "category_et": "Hot Dog",
            "dish_name_ru": "Hot Dog + Friikartulid + jook",
        }
        legacy_standalone = {
            "restaurant_name": "Break Time Burger & Wrap",
            "product_type": "tortillas",
            "category_ru": "Основные блюда",
            "category_et": "Pearoad",
            "dish_name_et": "Klassikaline Hot-Dog",
        }
        self.assertEqual(canonical_website_category(wrap, "Русский"), "Тортильи")
        self.assertEqual(canonical_website_category(combo, "Русский"), "Наборы и комбо")
        self.assertEqual(canonical_website_category(legacy_combo, "Русский"), "Наборы и комбо")
        self.assertEqual(canonical_website_category(legacy_standalone, "Русский"), "Хот-доги")

    def test_emojis_come_from_the_same_registry(self):
        self.assertEqual(get_category_emoji("sets"), "📦")
        self.assertEqual(get_category_emoji("Sushirullid ja maki"), "🍣")
        self.assertEqual(get_category_emoji("Алкогольные напитки (18+)"), "🍷")
        self.assertEqual(get_category_emoji("Соусы и добавки"), "🌶️")
        self.assertEqual(get_category_emoji("hot_dogs"), "🌭")
        self.assertEqual(get_category_emoji("Сиропы и добавки"), "🍯")


if __name__ == "__main__":
    unittest.main()
