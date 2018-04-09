# -*- coding: utf-8 -*-
from gtts.tokenizer import pre_processors, Tokenizer, tokenizer_cases
from gtts.lang import Languages, LanguagesFetchError
from gtts.utils import _minimize, _len, _clean_tokens

from gtts_token import gtts_token
from six.moves import urllib
import urllib3
import requests
import logging

__all__ = ['gTTS', 'gTTSError']


class Speed:
    """The Google API supports two speeds.
    (speed <= 0.3: slow; speed > 0.3: normal; default: 1)
    """

    SLOW = 0.3
    NORMAL = 1


class gTTS:
    """gTTS -- Google Text-to-Speech

    An interface to Google Translate's Text-to-Speech API

    Args:
        text (str): The text to be read.
        lang (str, optional): The language (IETF language tag) to
            read the text in. Defaults to 'en'.
        slow (bool, optional): Reads text more slowly. Defaults to :data:`False`.
        lang_check (bool, optional): Strictly enforce a documented
            ``lang``. Defaults to :data:`False`.

    Raises:
        AssertionError: When ``text`` is :data:`None` or empty.
        AssertionError: When there's nothing left to speak after pre-processing,
            tokinization and cleaning.
        ValueError: When ``lang_check`` is :data:`True` and
            ``lang`` is not supported.

    """

    MAX_CHARS = 100  # Max characters the Google TTS API takes at a time
    GOOGLE_TTS_URL = "https://translate.google.com/translate_tts"
    GOOGLE_TTS_HEADERS = {
        "Referer": "http://translate.google.com/",
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/47.0.2526.106 Safari/537.36"
    }

    def __init__(
            self,
            text,
            lang='en',
            slow=False,
            lang_check=False,
            pre_processor_funcs=[
                pre_processors.tone_marks,
                pre_processors.end_of_line,
                pre_processors.abbreviations,
                pre_processors.word_sub
            ],
            tokenizer_func=Tokenizer([
                tokenizer_cases.period_comma,
                tokenizer_cases.other_punctuation
            ]).run
    ):

        # Logger
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.debug = self.log.isEnabledFor(logging.DEBUG)

        # Debug
        if self.debug:
            for k, v in locals().items():
                if k == 'self':
                    continue
                self.log.debug("%s: %s", k, v)

        # Text
        assert text, 'No text to speak'
        self.text = text

        # Language
        if lang_check:
            try:
                if lang.lower() not in Languages().get():
                    raise ValueError("Language not supported: %s" % lang)
            except LanguagesFetchError as e:
                self.log.debug(str(e), exc_info=True)
                self.log.warning(str(e))

        self.lang_check = lang_check
        self.lang = lang.lower()

        # Read speed
        if slow:
            self.speed = Speed.SLOW
        else:
            self.speed = Speed.NORMAL

        # Pre-processors and tokenizer
        self.pre_processor_funcs = pre_processor_funcs
        self.tokenizer_func = tokenizer_func

        # Google Translate token
        self.token = gtts_token.Token()

    def _tokenize(self, text):
        # Pre-clean
        text = text.strip()

        # Apply pre-processorss
        for pp in self.pre_processor_funcs:
            text = pp(text)

        if _len(text) <= self.MAX_CHARS:
            return [text]

        # Tokenize
        tokens = self.tokenizer_func(text)

        # Clean
        tokens = _clean_tokens(tokens)

        # Minimize
        min_tokens = []
        for t in tokens:
            min_tokens += _minimize(t, ' ', self.MAX_CHARS)
        return min_tokens

    def write_to_fp(self, fp):
        """Do the TTS API request and write result to a file-like object

        Args:
            fp (file object): Any file-like object to write the `mp3` to.

        Raises:
            :class:`gTTSError`: When there's an error with the API request.
            TypeError: When ``fp`` is not a file-like object.

        """

        # When disabling ssl verify in requests (for proxies and firewalls),
        # urllib3 prints an insecure warning on stdout. We disable that.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        text_parts = self._tokenize(self.text)
        self.log.debug("text_parts: %i", len(text_parts))
        assert text_parts, 'No text to send to TTS API'

        for idx, part in enumerate(text_parts):
            try:
                # Calculate token
                part_tk = self.token.calculate_token(part)
            except requests.exceptions.RequestException as e:  # pragma: no cover
                self.log.debug(str(e), exc_info=True)
                raise gTTSError(
                    "Connection error during token calculation: %s" %
                    str(e))

            payload = {'ie': 'UTF-8',
                       'q': part,
                       'tl': self.lang,
                       'ttsspeed': self.speed,
                       'total': len(text_parts),
                       'idx': idx,
                       'client': 'tw-ob',
                       'textlen': _len(part),
                       'tk': part_tk}

            self.log.debug("payload-%i: %s", idx, payload)

            try:
                # Request
                r = requests.get(self.GOOGLE_TTS_URL,
                                 params=payload,
                                 headers=self.GOOGLE_TTS_HEADERS,
                                 proxies=urllib.request.getproxies(),
                                 verify=False)

                self.log.debug("headers-%i: %s", idx, r.request.headers)
                self.log.debug("url-%i: %s", idx, r.request.url)
                self.log.debug("status-%i: %s", idx, r.status_code)

                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # Request successful, bad response
                raise gTTSError(tts=self, response=r)
            except requests.exceptions.RequestException as e:  # pragma: no cover
                # Request failed
                raise gTTSError(str(e))

            try:
                # Write
                for chunk in r.iter_content(chunk_size=1024):
                    fp.write(chunk)
                self.log.debug("part-%i written to %s", idx, fp)
            except AttributeError as e:
                raise TypeError("'fp' must be a file-like object: %s" % str(e))

    def save(self, savefile):
        """Do the TTS API request and write result to file

        Args:
            savefile (str): The file name to save the `mp3` to.

        Raises:
            :class:`gTTSError`: When there's an error with the API request.

        """
        with open(savefile, 'wb') as f:
            self.write_to_fp(f)
            self.log.debug("Saved to %s" % savefile)


class gTTSError(Exception):
    """Exception that uses context to present a meaningful error message"""

    def __init__(self, msg=None, **kwargs):
        self.tts = kwargs.pop('tts', None)
        self.rsp = kwargs.pop('response', None)
        if msg:
            self.msg = msg
        elif self.tts is not None and self.rsp is not None:
            self.msg = self.infer_msg(self.tts, self.rsp)
        else:
            self.msg = None
        super(gTTSError, self).__init__(self.msg)

    def infer_msg(self, tts, rsp):
        """Attempt to guess what went wrong by using known
        information (e.g. http response) and observed behaviour"""

        # rsp should be <requests.Response>
        # http://docs.python-requests.org/en/master/api/
        status = rsp.status_code
        reason = rsp.reason

        cause = "Unknown"
        if status == 403:
            cause = "Bad token or upstream API changes"
        elif status == 404 and not tts.lang_check:
            cause = "Unsupported language '%s'" % self.tts.lang
        elif status >= 500:
            cause = "Uptream API error. Try again later."

        return "%i (%s) from TTS API. Probable cause: %s" % (
            status, reason, cause)
