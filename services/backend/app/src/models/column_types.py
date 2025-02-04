from piccolo.columns import Varchar

from .constants import STRING_SHORT_LENGTH, STRING_LONG_LENGTH


def StringShortPk():
    return Varchar(length=STRING_SHORT_LENGTH, required=True, unique=True)


def StringLong():
    return Varchar(length=STRING_LONG_LENGTH, null=True)
