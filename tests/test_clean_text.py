import unittest

from src.preprocessing.clean_text import clean_text


class CleanTextTests(unittest.TestCase):
    def test_clean_text_normalizes_whitespace(self) -> None:
        raw_text = "  Clínica\t\t\ncom\u00a0espaços   extras  "
        self.assertEqual(clean_text(raw_text), "Clínica com espaços extras")

    def test_clean_text_returns_empty_string_for_blank_input(self) -> None:
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text("   \n\t  "), "")


if __name__ == "__main__":
    unittest.main()
