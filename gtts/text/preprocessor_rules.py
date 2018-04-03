# -*- coding: utf-8 -*-
from .constants import ABBREVIATIONS, SUBS
from collections import namedtuple
import re

PreProcessorRule = namedtuple(
    'PreProcessorRule',
    'chars pattern_func repl')

# Because the tokenizer will split after a tone-modidfying
# punctuation mark, make sure there's whitespace after.
tone_marks = PreProcessorRule(
    chars=u'?!？！',
    pattern_func=lambda x: u"(?<={})".format(x),
    repl=' ')

# Re-form words cut by end-of-line hyphens (remove "<hyphen><newline>").
end_of_line = PreProcessorRule(
    chars=u'-',
    pattern_func=lambda x: u"{}\n".format(x),
    repl='')

# Remove periods after abbrevations that can be read without.
# TODO Caveat: Could potentially remove the ending period of a sentence.
abbreviations = PreProcessorRule(
    chars=ABBREVIATIONS,
    pattern_func=lambda x: u"(?<=(?i){})(?=\.).".format(x),
    repl='')

# Word-for-word substitutions.
word_sub = PreProcessorRule(
    chars=SUBS,
    pattern_func=lambda x: u"{}".format(x),
    repl=None)
