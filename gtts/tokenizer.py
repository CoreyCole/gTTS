# -*- coding: utf-8 -*-
import re

"""
from test import PreProcessorRule, TokenizerRule
from test import preprocessor_rules, tokenizer_rules
"""

PRE_PROCESSOR_RULES_DEFAULTS = []
"""
    preprocessor_rules.tone_marks,
    preprocessor_rules.end_of_line,
    preprocessor_rules.abbreviations,
    preprocessor_rules.word_sub
]
"""

TOKENIZER_RULES_DEFAULTS = []
"""
    tokenizer_rules.tone_marks,
    tokenizer_rules.period_comma,
    tokenizer_rules.other_punctuation
]
"""


class Rule():
    """
    A base rule
    """
    def __init__(self, expr, pattern_func):
        self.expr = expr
        self.pattern_func = pattern_func

    @property
    def expr(self):
        return self._expr

    @expr.setter
    def expr(self, val):
        try:
            _ = iter(val)
        except TypeError:
            raise ValueError("'expr' is not iterable")
        self._expr = val

    @property
    def pattern_func(self):
        return self._pattern_func

    @pattern_func.setter
    def pattern_func(self, val):
        if not callable(val):
            raise ValueError("'pattern_func' is not callable")
        self._pattern_func = val

    def pattern(self):
        raise NotImplementedError

class PreProcessorRule(Rule):
    """
    A pre-processor rule
    """
    def __init__(self, expr, pattern_func, repl):
        super(PreProcessorRule, self).__init__(expr, pattern_func)
        self.repl = repl

    def pattern(self):
        

class TokenizerRule(Rule):
    """
    A tokenizer rule
    """
    def pattern(self):
        re_alts = []
        for e in self.expr:
            ee = re.escape(e)
            re_alts.append(self.pattern_func(ee))
        return '|'.join(re_alts)


"""
    def _char_repl(self, el):
        # Returns a (`char`, `repl`) tuple.
        # If `repl` is `None`, `el` is already (`char`, `repl`)
        # else return (`el`, `repl`)
        if self.repl is not None:
            return char, self.repl
        else:
            return char
"""


class Tokenizer():
    def __init__(self,
                 preprocessor_rules=PRE_PROCESSOR_RULES_DEFAULTS,
                 tokenizer_rules=TOKENIZER_RULES_DEFAULTS):

        self.preprocessor_rules = preprocessor_rules
        self.tokenizer_rules = tokenizer_rules

    def preprocess(self, text):
        """Apply each pre-processor rule on `text`"""
        for pp in self.preprocessor_rules:
            for c in pp.chars:
                c, repl = pp._char_repl(c)
                c = re.escape(c)
                text = re.sub(pp.pattern_func(c), repl, text)
        return text

    def tokenize(self):
        pass
