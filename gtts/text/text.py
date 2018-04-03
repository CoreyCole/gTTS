# -*- coding: utf-8 -*-
from . import preprocessor_rules
from . import tokenizer_rules
import logging
import re

log = logging.getLogger(__package__)
log.addHandler(logging.NullHandler())

PRE_PROCESSOR_RULES = [
    preprocessor_rules.tone_marks,
    preprocessor_rules.end_of_line,
    preprocessor_rules.abbreviations,
    preprocessor_rules.word_sub
]

TOKENIZER_RULES = [
    tokenizer_rules.tone_marks,
    tokenizer_rules.period_comma,
    tokenizer_rules.other_punctuation
]

def _tokenize(text, max_size=0):
    """Pre-process and tokenize <text>.
    Returns list of tokens.
    """

    # Apply each pre-processor rule on <text>
    for pp in PRE_PROCESSOR_RULES:
        log.debug("pp-rule: %s" % str(pp))
        for c in pp.chars:
            c, repl = _extract(c, pp.repl)
            c = re.escape(c)
            text = re.sub(pp.pattern_func(c), repl, text)

    # Build regex alternations
    alts = []
    for t in TOKENIZER_RULES:
        log.debug("t-rule: %s" % str(t))
        for c in t.chars:
            c = re.escape(c)
            alts.append(t.pattern_func(c))

    # Build pattern and tokenize
    pattern = '|'.join(alts)
    tokens = re.split(pattern, text)

    # Clean (strip out whitespace and empty tokens)
    tokens = [t.strip() for t in tokens if t.strip()]

    # Don't minimize if <max_size> is False or < 1
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
