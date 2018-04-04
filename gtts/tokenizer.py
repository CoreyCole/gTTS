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


class Ruleset():
    """
    A base Ruleset
    """

    def __init__(self, criteria, pattern_func, flags=0):
        self.criteria = criteria
        self.pattern_func = pattern_func

    @property
    def criteria(self):
        return self._criteria

    @criteria.setter
    def criteria(self, val):
        try:
            _ = iter(val)
        except TypeError:
            raise ValueError("'criteria' is not iterable")
        self._criteria = set(val)

    @property
    def pattern_func(self):
        return self._pattern_func

    @pattern_func.setter
    def pattern_func(self, val):
        if not callable(val):
            raise ValueError("'pattern_func' is not callable")
        self._pattern_func = val

    def items(self):
        for c in self.criteria:
            yield self._transform_item(c)

    def _transform_item(self, e):
        raise NotImplementedError


class PreProcessorRuleset(Ruleset):
    """
    A pre-processor rule set
    i.e. set of items (pattern, repl) for `re.sub()`s
    """

    def __init__(self, criteria, pattern_func, flags=0, repl=None):
        super(PreProcessorRuleset, self).__init__(criteria, pattern_func, flags)
        self.repl = repl

    def _transform_item(self, item):
        try:
            # item is a (criterion, repl) tuple
            _crit, _repl = item
        except ValueError:
            if len(item) > 2:
                # item is a tuple with too many values
                ValueError('item must be (a,b) tuple')
            elif self.repl is not None:
                # item is a criterion only, augment with default repl
                _crit, _repl = item, self.repl
            else:
                # item is a criterion only, but default repl is None
                raise ValueError('must define repl if not tuples')

        pattern = self.pattern_func(re.escape(_crit))
        return pattern, _repl


class TokenizerRuleset(Ruleset):
    """
    A tokenizer rule set
    i.e. set of items (pattern) for `re.split()`s
    """

    def _transform_item(self, c):
        pattern = self.pattern_func(re.escape(c))
        return pattern


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
