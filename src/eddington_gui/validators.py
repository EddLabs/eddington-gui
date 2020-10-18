"""
Validators module.

Most validators here will be replaces by Toga's default validators once they are out
"""
import re

NUMBER_REGEX = r"^[-]?(\d+|\d*\.\d+|\d+.\d*)$"


def number(allow_empty=True):
    def validator(input_string):
        if allow_empty and input_string == "":
            return None
        if not bool(re.search(NUMBER_REGEX, input_string)):
            return "Input should be a number"
        return None

    return validator
