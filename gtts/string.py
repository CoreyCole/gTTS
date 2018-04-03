# -*- coding: utf-8 -*-
from collections import namedtuple
import re

ABBREVIATIONS = ['dr', 'jr', 'mr', 'mrs', 'ms', 'msgr', 'prof', 'sr', 'st']

SUBS = [
    ('M.', 'Monsieur')
]

PreProcessorRule = namedtuple(
    'PreProcessorRule',
    'chars pattern_func repl')

TokenizerRule = namedtuple(
    'TokenizerRule',
    'chars pattern_func')

# Because the tokenizer will split after a tone-modidfying
# punctuation mark, make sure there's whitespace after.
tone_marks_pp_rule = PreProcessorRule(
    chars=u'?!？！',
    pattern_func=lambda x: u"(?<={})".format(x),
    repl=' ')

# Re-form words cut by end-of-line hyphens (remove "<hyphen><newline>").
end_of_line_pp_rule = PreProcessorRule(
    chars=u'-',
    pattern_func=lambda x: u"{}\n".format(x),
    repl='')

# Remove periods after abbrevations that can be read without.
# The API sometimes reads them as an end-of-sentence.
# Caveat: Could potentially remove the ending period of a sentence.
abbreviations_pp_rule = PreProcessorRule(
    chars=ABBREVIATIONS,
    pattern_func=lambda x: u"(?<=(?i){})(?=\.).".format(x),
    repl='')

# Word-for-word substitutions.
word_sub_pp_rule = PreProcessorRule(
    chars=SUBS,
    pattern_func=lambda x: u"{}".format(x),
    repl=None)

PRE_PROCESSOR_RULES = [
    tone_marks_pp_rule,
    end_of_line_pp_rule,
    abbreviations_pp_rule,
    word_sub_pp_rule
]

# Keep tone-modifying punctuation. Match following character.
tone_marks_tokenizer_rule = TokenizerRule(
    chars=u'?!？！',
    pattern_func=lambda c: u"(?<={}).".format(c))

# Period and comma rule.
# Match if not preceded by ".<letter>" and only if followed by space.
# Won't cut in the middle/after dotted abbreviations; won't cut numbers.
# Caveats: Won't match if a dotted abbreviation ends a sentence.
#          Won't match the end of a sentence if not followed by a space.
period_comma_tokenizer_rule = TokenizerRule(
    chars=u'.,',
    pattern_func=lambda c: u"(?<!\.[a-zA-Z]){} ".format(c))

# Match other punctuation.
other_punctuation_tokenizer_rule = TokenizerRule(
    chars=u'¡()[]¿…‥،;:—。，、：\n',
    pattern_func=lambda c: u"{}".format(c))


TOKENIZER_RULES = [
    tone_marks_tokenizer_rule,
    period_comma_tokenizer_rule,
    other_punctuation_tokenizer_rule
]


def _tokenize(text, max_size):
    """Pre-process and tokenize <text>.
    Returns list of tokens.
    """

    # Apply each pre-processor rule on <text>
    for pp in PRE_PROCESSOR_RULES:
        for c in pp.chars:
            c, repl = _extract(c, pp.repl)
            c = re.escape(c)
            text = re.sub(pp.pattern_func(c), repl, text)

    # Build regex alternations
    alts = []
    for t in TOKENIZER_RULES:
        for c in t.chars:
            c = re.escape(c)
            alts.append(t.pattern_func(c))

    # Build pattern and tokenize
    pattern = '|'.join(alts)
    tokens = re.split(pattern, text)

    # Clean (strip out whitespace and empty tokens)
    tokens = [t.strip() for t in tokens if t.strip()]

    # Don't minimize when <max_size> is False
    if not max_size or max_size < 1:
        return tokens

    # Minimize tokens to ensure they're of max <max_size>
    min_tokens = []
    for t in tokens:
        min_tokens += _minimize(t, ' ', max_size)
    return min_tokens


def _minimize(the_string, delim, max_size):
    """ Recursive function that splits `the_string` in chunks
    of maximum `max_size` chars delimited by `delim`. Returns list.
    """

    # Remove <delim> from start of <the_string>
    if the_string.startswith(delim):
        the_string = the_string[len(delim):]

    if _len(the_string) > max_size:
        try:
            idx = the_string.rindex(delim, 0, max_size)
        except ValueError:
            idx = max_size
        return [the_string[:idx]] + \
            _minimize(the_string[idx:], delim, max_size)
    else:
        return [the_string]


def _extract(c, default_repl):
    if default_repl is not None:
        return c, default_repl
    else:
        return c


def _len(text):
    """Get real char len of <text>, via unicode() if Python 2"""
    try:
        # Python 2
        return len(unicode(text))
    except NameError:
        # Python 3
        return len(text)
