# -*- coding: utf-8 -*-
from gtts.tokenizer import PreProcessorRegex, PreProcessorSub
import re

# Because the tokenizer will split after a tone-modidfying
# punctuation mark, make sure there's whitespace after.
tone_marks = PreProcessorRegex(
    search_args=u"?!？！",
    search_func=lambda x: u"(?<={})".format(x),
    repl=' ').run

# Re-form words cut by end-of-line hyphens (remove "<hyphen><newline>").
end_of_line = PreProcessorRegex(
    search_args=u'-',
    search_func=lambda x: u"{}\n".format(x),
    repl='').run

ABBREVIATIONS = ['dr', 'jr', 'mr',
                 'mrs', 'ms', 'msgr',
                 'prof', 'sr', 'st']

# Remove periods after abbrevations that can be read without.
# TODO Caveat: Could potentially remove the ending period of a sentence.
abbreviations = PreProcessorRegex(
    search_args=ABBREVIATIONS,
    search_func=lambda x: u"(?<={})(?=\.).".format(x),
    repl='', flags=re.IGNORECASE).run

SUBS = [
    ('M.', 'Monsieur')
]

# Word-for-word substitutions.
word_sub = PreProcessorSub(sub_pairs=SUBS).run
