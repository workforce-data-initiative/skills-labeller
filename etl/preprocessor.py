import spacy
from textacy.preprocess import preprocess_text
from textacy.keyterms import singlerank
import re

class SingleRankWithContext(object):
    def __init__(self, n_keyterms=0.05, context_chars=50, text=None, options=None, model=None):
        """
        This class accepts a set of parameters for extracting keyterms/keyphrases from
        a given body of text. See Textacy, textacy.keyterms for related use and
        documentation.

        example usage:
        from preprocessor import JobPostingPreprocessor
        j = JobPostingPreprocessor()
        j.get_job_posting_features(text="fox fox fox multi tool jumped over the fence and and")
        # ['fox fox fox'] # one keyphrase
        """
        self.n_keyterms = n_keyterms
        self.context_chars = context_chars
        self.text = text
        self.options = options
        self.model = model
        self.nlp = None

        if not options:
            self.options = {'lowercase': False,
                            'no_urls': True,
                            'no_emails': True,
                            'no_phone_numbers': True,
                            'no_currency_symbols': False,
                            'no_punct': False}
        if not self.model:
            self.model = 'en'

        if 'en' == self.model:
            # en_core_web_sm.load() # make doc with nlp(...)
            self.nlp = spacy.load(self.model)

    def get_job_posting_keyterms(self,
                                 text=None,
                                 n_keyterms=None):
        """
        Extract key terms/key phrases from the given text, with context

        Returns: (list) each element is a dictionary, with keys:
            token_phrase: the candidate phrase
            token_span: the start/end span of the candidate phrase
            context_span: the start/end span of the candidate phrase + context
        """
        if not n_keyterms:
            n_keyterms = self.n_keyterms

        if not text:
            text = self.text

        processed_text = preprocess_text(text, **self.options)

        doc = self.nlp(processed_text)
        keyphrases = singlerank(doc, n_keyterms=n_keyterms, normalize=None)
        results = []
        for keyphrase, confidence in keyphrases:
            for match in re.finditer(keyphrase, processed_text):
                context_start = match.start() - self.context_chars
                if context_start < 0:
                    context_start = 0

                context_end = match.end() + self.context_chars
                if context_end > len(processed_text) - 1:
                    context_end = len(processed_text) - 1

                results.append(dict(
                    token_phrase=keyphrase,
                    token_span=match.span(),
                    context_span=(context_start, context_end)
                ))

        return results
