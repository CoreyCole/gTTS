# -*- coding: utf-8 -*-

from gtts.tokenizer import TokenizerCase
import re

ALL_PUNC = u"?!？！.,¡()[]¿…‥،;:—。，、：\n"

TONE_MARKS = u"?!？！"

PERIOD_COMMA = u".,"

# Keep tone-modifying punctuation. Match following character.
tone_marks = TokenizerCase(
    pattern_args=u'?!？！',
    pattern_func=lambda c: u"(?<={}).".format(c))

# Period and comma rule.
# Match if not preceded by ".<letter>" and only if followed by space.
# Won't cut in the middle/after dotted abbreviations; won't cut numbers.
# Caveats: Won't match if a dotted abbreviation ends a sentence.
#          Won't match the end of a sentence if not followed by a space.
period_comma = TokenizerCase(
    pattern_args=u'.,',
    pattern_func=lambda c: u"(?<!\.[a-z]){} ".format(c))

# Match other punctuation.
other_punctuation = TokenizerCase(
    pattern_args=u'¡()[]¿…‥،;:—。，、：\n',
    pattern_func=lambda c: u"{}".format(c))
