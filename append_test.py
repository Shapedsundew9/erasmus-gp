import sys

new_tests = """
    def test_is_compatible_inheritance(self):
        \"\"\"Test is_compatible logic for standard inheritance.\"\"\"
        int_td = types_def_store['int']
        number_td = types_def_store['Number']
        float_td = types_def_store['float']
        
        # int is a Number
        self.assertTrue(types_def_store.is_compatible(int_td, number_td))
        # Number is not an int
        self.assertFalse(types_def_store.is_compatible(number_td, int_td))
        # float is not an int
        self.assertFalse(types_def_store.is_compatible(float_td, int_td))
        # int is an int
        self.assertTrue(types_def_store.is_compatible(int_td, int_td))

    def test_is_compatible_covariance(self):
        \"\"\"Test is_compatible logic for generic covariance.\"\"\"
        # Get base concrete and abstract types
        dict_str_int = types_def_store['dict[str, int]']
        dict_str_num = types_def_store['dict[str, Number]']
        dict_int_num = types_def_store['dict[int, Number]']
        
        # Exact match
        self.assertTrue(types_def_store.is_compatible(dict_str_int, dict_str_int))
        
        # Subtype Covariance (int -> Number)
        self.assertTrue(types_def_store.is_compatible(dict_str_int, dict_str_num))
        
        # Covariance failure (str -> int)
        self.assertFalse(types_def_store.is_compatible(dict_str_int, dict_int_num))
        
        # Reverse Covariance failure (Number is not an int)
        self.assertFalse(types_def_store.is_compatible(dict_str_num, dict_str_int))

        # Check deeper nested covariance
        list_dict_str_int = types_def_store['list[dict[str, int]]']
        list_dict_str_num = types_def_store['list[dict[str, Number]]']
        
        self.assertTrue(types_def_store.is_compatible(list_dict_str_int, list_dict_str_num))
        self.assertFalse(types_def_store.is_compatible(list_dict_str_num, list_dict_str_int))
"""

with open("tests/test_egppy/test_genetic_code/test_types_def_store.py", "r") as f:
    content = f.read()

content = content.replace("if __name__ == \"__main__\":", new_tests + "\nif __name__ == \"__main__\":")

with open("tests/test_egppy/test_genetic_code/test_types_def_store.py", "w") as f:
    f.write(content)

