"""Integration checks proving the website uses the shared category package."""
import unittest

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

    def test_emojis_come_from_the_same_registry(self):
        self.assertEqual(get_category_emoji("sets"), "📦")
        self.assertEqual(get_category_emoji("Sushirullid ja maki"), "🍣")
        self.assertEqual(get_category_emoji("Алкогольные напитки (18+)"), "🍷")
        self.assertEqual(get_category_emoji("Соусы и добавки"), "🌶️")
        self.assertEqual(get_category_emoji("Сиропы и добавки"), "🍯")


if __name__ == "__main__":
    unittest.main()
