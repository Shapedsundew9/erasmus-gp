"""Tokenisation of user strings.

This module is used to map tokens to user text.
"""

from typing import Any, Literal

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Valid token code prefixes
#    'D': Debug
#    'I': Information
#    'W': Warning
#    'E': Error
#    'F': Fatal
#    'X': Unknown
_CODE_PREFIXES: tuple[
    Literal["D"], Literal["I"], Literal["W"], Literal["E"], Literal["F"], Literal["X"]
] = ("D", "I", "W", "E", "F", "X")


"""The token library maps token codes to formatted strings.

The code:fmt_str pairs are added using register_token_code()
When a token with a code in the token_library is converted to a string
The fmt_str is looked up and formatted with the token parameters.
"""
token_library: dict[str, str] = {}


def register_token_code(code: str, fmt_str: str) -> None:
    """Register a token code and text in the token_library.

    The registered code can then be used to generate a human readable
    string when the _str_() function is called on a token with that code.

    Args
    ----
    code : Format "E<i><i><i><i><i>" where <i> is a digit 0 to 9. Every code is unique.
    fmt_str : A human readable string for the code with optional formatting parameters.

    Returns
    -------
    True if the token is valid else False
    """
    if not code[0] in _CODE_PREFIXES:
        raise ValueError(f"Invalid token code prefix '{code[0]}' must be one of {_CODE_PREFIXES}.")
    if len(code) != 6:
        raise ValueError(f"Invalid token code '{code}' must be 6 characters long.")
    code_num: int = int(code[1:])
    if code_num < 0 or code_num > 99999:
        raise ValueError(f"Invalid token code '{code}' must be in the range 00000 to 99999.")
    if code in token_library:
        raise ValueError(f"Invalid token code '{code}' is already in use.")
    token_library[code] = fmt_str


class TextToken:
    """Maintains a relationship between a code and a human readable string.

    A token has the structure:
    { '<code>', {<parameters>} }
    where <code> is the same as in register_token_code() and <parameters> is a
    set of key:value pairs defining the values of the formatting keys in the
    fmt_str for the code in the token_library.
    """

    def __init__(self, token: dict[str, dict[str, Any]]) -> None:
        self.code: str = tuple(token.keys())[0]
        self.parameters: dict[str, Any] = token[self.code]

    def __str__(self) -> str:
        """Convert the token to a human readbale string."""
        # text_token._logger.debug("Code {}: Parameters: {} Library string: {}".format(
        #   self.code, self.parameters, token_library[self.code]))
        return (
            self.code
            + ": "
            + token_library.get(self.code, "TOKEN NOT FOUND").format_map(self.parameters)
        )
