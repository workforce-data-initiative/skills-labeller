from redis import Redis
import rq
import spacy
from textacy.preprocess import preprocess_text
from textacy.preprocess import fix_bad_unicode
from textacy.keyterms import singlerank
# should probably import from some kidn of ML api to define endpoints, queue names
# and the like

class JobPostingPreprocessor(object):
    def __init__(self, n_keyterms=0.05, text=None, url=None, options=None, model=None):
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
        self.text = text
        self.url = url
        self.options = options
        self.model = model
        self.nlp = None

        if not options:
            self.options = {'lowercase': True,
                            'no_urls': True,
                            'no_emails': True,
                            'no_phone_numbers': True,
                            'no_currency_symbols': True,
                            'no_punct': True}
        if not self.model:
            self.model = 'en'

        if 'en' == self.model:
            # en_core_web_sm.load() # make doc with nlp(...)
            self.nlp = spacy.load(self.model)

        # WIP: ideally we'd 'version' this class via its parameters so that we can
        # attach a set of preprocessor options, usage to system output and results

    def clean_html_markup(self, text):
        """
        Copied from NLTK package.
        Remove HTML markup from the given text.

        see: https://stackoverflow.com/questions/26002076/python-nltk-clean-html-not-implemented
        for more details
        """

        # First we remove inline JavaScript/CSS:
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        # Next we can remove the remaining tags:
        # Then, we deal with whitespace
        # ... finally we strip newlines
        cleaned = re.sub(
            r"(?is)<(script|style).*?>.*?(</\1>)", "", text.strip())
        cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
        cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"\n", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        return cleaned.strip()

    def get_job_posting_features(self,
                                 text=None,
                                 url=None,
                                 n_keyterms=None,
                                 timeout=5):
        """
        Extract key phrases from the given text or url
        """
        if not n_keyterms:
            n_keyterms = self.n_keyterms

        if not text:
            text = self.text

        if not url:
            url = self.url

        if url:
            try:
                html = requests.get(url, timeout=timeout).text
            except requests.exceptions.RequestException as e:
                html = 'REQUEST_TIMED_OUT_' + '(' + url + ')'
            text = self.get_text(html)
        else:  # assume text provided
            pass

        options = self.options
        processed_text = preprocess_text(text, **options)

        # todo: get lang parameter working, not depending on
        doc = self.nlp(processed_text)

        keyphrases = singlerank(doc, n_keyterms=n_keyterms)

        # use () for generator if desired
        return [element[0] for element in keyphrases]

class Endpoint(object):
    def __init__(self, options=None):
        """
        e = Endpoint()

        # interact with endpoint by...
        redis_conn = Redis()
        q = rq.Queue()
        result = q.enqueue('get_job_posting_features', text="fox fox fox multi tool jumped over the fence and and")
        """
        self.preprocessor = JobPostingPreprocessor() #should be called .api?
        self.options = options
        self.redis_options = None
        self.queue_options = None
        self.queue = None

        if self.options is not None and 'backend_options' in self.options:
                self.redis_options = self.options['backend_options']

        if self.options is not None and 'queue_options' in self.options:
                self.queue_options = self.options['queue_options']

    def setup_queue(self):
        redis_conn = Redis(**self.redis_options)
        self.queue = rq.Queue(name, **self.queue_options)

    def run(self):
        if not self.queue:
            self.setup_queue()

        # self.preprocessor has imported lannguage model so fork already has it
        with rq.Connection():
            w = rq.Worker(self.queue)
            w.work() # now listening on that queue/endpoint
