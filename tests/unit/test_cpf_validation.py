import unittest

from vet_tech.features.auth.validation import is_valid_cpf, normalize_cpf


class CpfValidationTests(unittest.TestCase):
    def test_normalize_formatted_cpf(self):
        self.assertEqual(normalize_cpf("529.982.247-25"), "52998224725")

    def test_accepts_valid_formatted_and_unformatted_cpfs(self):
        self.assertTrue(is_valid_cpf("529.982.247-25"))
        self.assertTrue(is_valid_cpf("11144477735"))

    def test_rejects_invalid_or_repeated_digits(self):
        self.assertFalse(is_valid_cpf("529.982.247-24"))
        self.assertFalse(is_valid_cpf("000.000.000-00"))
        self.assertFalse(is_valid_cpf("11111111111"))
        self.assertFalse(is_valid_cpf("1234567890"))

    def test_rejects_characters_outside_cpf_format(self):
        self.assertEqual(normalize_cpf("529.982.247/A5"), "")
        self.assertFalse(is_valid_cpf("529.982.247/A5"))


if __name__ == "__main__":
    unittest.main()
