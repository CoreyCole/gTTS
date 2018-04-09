# -*- coding: utf-8 -*-
from gtts.tokenizer import RegexBuilder, symbols


def tone_marks():
    """
    Keep tone-modifying punctuation. Match following character.
    Assumes the `tone_marks()` pre-processor was run.
    """
    return RegexBuilder(
        pattern_args=symbols.TONE_MARKS,
        pattern_func=lambda x: u"(?<={}).".format(x)).regex


def period_comma():
    """
    Period and comma case.
    Match if not preceded by ".<letter>" and only if followed by space.
    Won't cut in the middle/after dotted abbreviations; won't cut numbers.
    Caveats: Won't match if a dotted abbreviation ends a sentence.
             Won't match the end of a sentence if not followed by a space.
    """
    return RegexBuilder(
        pattern_args=symbols.PERIOD_COMMA,
        pattern_func=lambda x: u"(?<!\.[a-z]){} ".format(x)).regex


def other_punctuation():
    """
    Match other punctuation.
    """
    OTHER_PUNC = ''.join((
        set(symbols.ALL_PUNC) -
        set(symbols.TONE_MARKS) -
        set(symbols.PERIOD_COMMA)))
    return RegexBuilder(
        pattern_args=OTHER_PUNC,
        pattern_func=lambda x: u"{}".format(x)).regex
