"""Erasmus GP ASCII Art"""

from datetime import datetime, timedelta, timezone
from typing import Literal, LiteralString

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


EGP_DEFAULT_BW_HEADER: Literal["wide3_bold"] = "wide3_bold"
_SPACER: Literal[6] = 6
# pylint: disable=fixme
# TODO: Add dynamic versioning
_VERSION: Literal["0.1"] = "0.1"
_DATETIME: datetime = datetime(2023, 2, 11, 11, 7, tzinfo=timezone(timedelta(0)))
_HEADER: tuple[str, ...] = (
    f"Erasmus Genetic Programming (EGP) v{_VERSION}",
    f"Released {_DATETIME.strftime('%d-%b-%Y %H:%M:%S')} UTC under MIT license",
    "Copyright (c) 2023 Shapedsundew9.  https://github.com/Shapedsundew9",
)


# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
class TestColors:  # pylint: disable=too-few-public-methods
    """Terminal 8-bit text color escape sequences."""

    EGP_TREE_GROUND: Literal["\u001b[38;5;143m"] = "\033[38;5;143m"
    EGP_TREE_TRUNK: Literal["\u001b[38;5;52m"] = "\033[38;5;52m"
    EGP_TREE_BRANCHES: Literal["\u001b[38;5;22m"] = "\033[38;5;22m"
    EGP_TREE_UNIVERSE: Literal["\u001b[38;5;39m"] = "\033[38;5;39m"
    EGP_TREE_LEAVES: Literal["\u001b[38;5;22m"] = "\033[38;5;22m"
    BOLD: Literal["\u001b[1m"] = "\033[1m"
    UNDERLINE: Literal["\u001b[4m"] = "\033[4m"
    ENDC: Literal["\u001b[0m"] = "\033[0m"


EGP_TEXT_TREE: dict[str, tuple[LiteralString, LiteralString, LiteralString]] = {
    "slim_color": (
        f"{TestColors.EGP_TREE_BRANCHES}\\{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_UNIVERSE}O{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_BRANCHES}/{TestColors.ENDC}",
        f" {TestColors.EGP_TREE_TRUNK}|{TestColors.ENDC} ",
        f"{TestColors.EGP_TREE_GROUND}~~~{TestColors.ENDC}",
    ),
    "standard_color": (
        f"{TestColors.EGP_TREE_BRANCHES}\\{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_UNIVERSE}(){TestColors.ENDC}"
        f"{TestColors.EGP_TREE_BRANCHES}/{TestColors.ENDC}",
        f" {TestColors.EGP_TREE_TRUNK}||{TestColors.ENDC} ",
        f"{TestColors.EGP_TREE_GROUND}~~~~{TestColors.ENDC}",
    ),
    "wide1_color": (
        f"{TestColors.EGP_TREE_BRANCHES}\\({TestColors.ENDC}"
        f"{TestColors.EGP_TREE_UNIVERSE}O{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_BRANCHES})/{TestColors.ENDC}",
        f" {TestColors.EGP_TREE_TRUNK}/|\\{TestColors.ENDC} ",
        f"{TestColors.EGP_TREE_GROUND}~~~~~{TestColors.ENDC}",
    ),
    "wide2_color": (
        f"{TestColors.EGP_TREE_BRANCHES}\\({TestColors.ENDC}"
        f"{TestColors.EGP_TREE_UNIVERSE}O{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_BRANCHES})/{TestColors.ENDC}",
        f" {TestColors.EGP_TREE_TRUNK}|||{TestColors.ENDC} ",
        f"{TestColors.EGP_TREE_GROUND}~~~~~{TestColors.ENDC}",
    ),
    "wide3_color": (
        f"{TestColors.EGP_TREE_BRANCHES}\\({TestColors.ENDC}"
        f"{TestColors.EGP_TREE_UNIVERSE}O{TestColors.ENDC}"
        f"{TestColors.EGP_TREE_BRANCHES})/{TestColors.ENDC}",
        f" {TestColors.EGP_TREE_TRUNK}|@|{TestColors.ENDC} ",
        f"{TestColors.EGP_TREE_GROUND}~~~~~{TestColors.ENDC}",
    ),
    "slim_bold": (
        f"{TestColors.BOLD}\\{TestColors.ENDC}"
        f"{TestColors.BOLD}O{TestColors.ENDC}"
        f"{TestColors.BOLD}/{TestColors.ENDC}",
        f" {TestColors.BOLD}|{TestColors.ENDC} ",
        f"{TestColors.BOLD}~~~{TestColors.ENDC}",
    ),
    "standard_bold": (
        f"{TestColors.BOLD}\\{TestColors.ENDC}"
        f"{TestColors.BOLD}(){TestColors.ENDC}"
        f"{TestColors.BOLD}/{TestColors.ENDC}",
        f" {TestColors.BOLD}||{TestColors.ENDC} ",
        f"{TestColors.BOLD}~~~~{TestColors.ENDC}",
    ),
    "wide1_bold": (
        f"{TestColors.BOLD}\\({TestColors.ENDC}"
        f"{TestColors.BOLD}O{TestColors.ENDC}"
        f"{TestColors.BOLD})/{TestColors.ENDC}",
        f" {TestColors.BOLD}/|\\{TestColors.ENDC} ",
        f"{TestColors.BOLD}~~~~~{TestColors.ENDC}",
    ),
    "wide2_bold": (
        f"{TestColors.BOLD}\\({TestColors.ENDC}"
        f"{TestColors.BOLD}O{TestColors.ENDC}"
        f"{TestColors.BOLD})/{TestColors.ENDC}",
        f" {TestColors.BOLD}|||{TestColors.ENDC} ",
        f"{TestColors.BOLD}~~~~~{TestColors.ENDC}",
    ),
    "wide3_bold": (
        f"{TestColors.BOLD}\\({TestColors.ENDC}"
        f"{TestColors.BOLD}O{TestColors.ENDC}"
        f"{TestColors.BOLD})/{TestColors.ENDC}",
        f" {TestColors.BOLD}|@|{TestColors.ENDC} ",
        f"{TestColors.BOLD}~~~~~{TestColors.ENDC}",
    ),
    "slim_bw": (
        "\\O/",
        " | ",
        "~~~",
    ),
    "standard_bw": (
        "\\()/",
        " || ",
        "~~~~",
    ),
    "wide1_bw": (
        "\\(O)/",
        " /|\\ ",
        "~~~~~",
    ),
    "wide2_bw": (
        "\\(O)/",
        " ||| ",
        "~~~~~",
    ),
    "wide3_bw": (
        "\\(O)/",
        " |@| ",
        "~~~~~",
    ),
}


def as_string(text_tree: str = "wide3", attr: str = "color") -> str:
    """A string representation of the selected text tree logo.

    Args
    ----
    text_tree: Must be a valid key of egp_logo.text_tree
    attr: One of 'color', 'bold', 'bw'

    Returns
    -------
    Single string of text logo lines delimited by \\n.
    """
    return "\n".join(EGP_TEXT_TREE[text_tree + "_" + attr])


def gallery() -> str:
    """Return a display gallery string of all text logo variants."""
    max_len: int = max((len(name) for name in EGP_TEXT_TREE))
    spacer: str = " " * (max_len + _SPACER)
    string: str = ""
    for name, logo in EGP_TEXT_TREE.items():
        space: LiteralString = " " * (max_len - len(name) + _SPACER - 1)
        string += f"{TestColors.BOLD}{name}{TestColors.ENDC}:{space}"
        string += logo[0] + "\n"
        for line in logo[1:]:
            string += spacer + line + "\n"
        string = string + "\nAll EGP text logos are Copyright (c) 2023 Shapedsundew9\n"
    return string


def header(text_tree: str = "wide3", attr: str = "color") -> str:
    """Text header with logo.

    Args
    ----
    text_tree: Must be a valid key of EGP_TEXT_TREE
    attr: One of 'color', 'bold', 'bw'

    Returns
    -------
    Single string of text logo lines delimited by \\n.
    """
    return "\n".join(header_lines(text_tree, attr))


def header_lines(text_tree: str = "wide3", attr: str = "color") -> list[str]:
    """Text header with logo.

    Args
    ----
    text_tree: Must be a valid key of EGP_TEXT_TREE
    attr: One of 'color', 'bold', 'bw'

    Returns
    -------
    A list of strings, one for each line in the header.
    """
    str_list: list[str] = [""]
    for line, _header in zip(EGP_TEXT_TREE[text_tree + "_" + attr], _HEADER, strict=True):
        str_list.append(" " + line + "   " + _header)
    str_list.append("")
    return str_list
