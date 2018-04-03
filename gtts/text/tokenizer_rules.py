# -*- coding: utf-8 -*-
from collections import namedtuple
import re

TokenizerRule = namedtuple(
    'TokenizerRule',
    'chars pattern_func')

# Keep tone-modifying punctuation. Match following character.
tone_marks = TokenizerRule(
    chars=u'?!？！',
    pattern_func=lambda c: u"(?<={}).".format(c))

# Period and comma rule.
# Match if not preceded by ".<letter>" and only if followed by space.
# Won't cut in the middle/after dotted abbreviations; won't cut numbers.
# Caveats: Won't match if a dotted abbreviation ends a sentence.
#          Won't match the end of a sentence if not followed by a space.
period_comma = TokenizerRule(
    chars=u'.,',
    pattern_func=lambda c: u"(?<!\.[a-zA-Z]){} ".format(c))

# Match other punctuation.
other_punctuation = TokenizerRule(
    chars=u'¡()[]¿…‥،;:—。，、：\n',
    pattern_func=lambda c: u"{}".format(c))
