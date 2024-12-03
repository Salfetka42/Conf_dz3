import unittest

from git.objects.util import parse_date

from StudyL3 import parse_custom_config, ConfigSyntaxError, convert_to_toml


class TestConfigParser(unittest.TestCase):

    def test_parse_empty_config(self):
        input_text = ""
        result = parse_custom_config(input_text)
        self.assertEqual(result, {})

    def test_parse_basic_key_value(self):
        input_text = "key: 'value'"
        result = parse_custom_config(input_text)
        self.assertEqual(result, {"key": "value"})

    def test_parse_integer_value(self):
        input_text = "key: 123"
        result = parse_custom_config(input_text)
        self.assertEqual(result, {"key": 123})

    def test_parse_constant(self):
        input_text = """var pi = 3.14
key: |pi|"""
        result = parse_custom_config(input_text)
        self.assertEqual(result, {"key": 3.14})

    def test_parse_constant_with_expression(self):
        input_text = """var base = 2
var exponent = 3
var result = |base| ** |exponent|
key: |result|"""
        result = parse_custom_config(input_text)
        self.assertEqual(result, {"key": 8})

    def test_parse_syntax_error(self):
        input_text = "key : value"
        with self.assertRaises(ConfigSyntaxError):
            parse_custom_config(input_text)

    def test_parse_unknown_constant(self):
        input_text = "key: |non_existent|"
        with self.assertRaises(ConfigSyntaxError):
            parse_custom_config(input_text)

    def test_parse_no_value_for_key(self):
        input_text = "key:"
        with self.assertRaises(ConfigSyntaxError):
            parse_custom_config(input_text)

    def test_parse_invalid_dict_syntax(self):
        input_text = "key: {subkey: 'value',"
        with self.assertRaises(ConfigSyntaxError):
            parse_custom_config(input_text)

    def test_parse_dict_to_toml(self):
        input_text = """
        {
            screen_width: 1920;
            screen_height: 1080;
            title: 'My Application';
        }
        """
        expected = """screen_width = 1920
screen_height = 1080
title = "My Application"
"""

        parsed_data = parse_custom_config(input_text)
        result = convert_to_toml(parsed_data)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
