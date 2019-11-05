import re
from collections import Counter
from gensim.utils import deaccent, to_unicode
import  gensim.parsing.preprocessing as proc
####################
# Global variables
####################

# Load list of stopwords
with open('stopwords-es.txt', 'r') as file:
    stopwords = list()
    for line in file:
        stop_word = deaccent(line.strip('\n'))
        stopwords.append(stop_word)
stopwords = frozenset(stopwords)

# regexp for matching @usernames and #hashtags
tw_handles = r"([@][A-z]+)|([#][A-z]+)"
# for matching URLs
urls = r"((\w+:\/\/)[-a-zA-Z0-9:@;?&=\/%\+\.\*!'\(\),\$_\{\}\^~\[\]`#|]+)"
punctuation_es = r'([!¡"\#\$%\&\'\(\)\*\+,\-\./:;<=>\?\¿@\[\\\]\^_`\{\|\}\~])+'
# Master Regexp
multi_pattern = '|'.join([tw_handles, urls, punctuation_es])
non_plain_re = re.compile(multi_pattern, re.UNICODE)
####################

def remove_non_plain(document):
    """
    Replaces urls, @usernames, #tags, emojis and numbers
    with a ' ' (space). Also removes accents and punctuation
    to finally remove redundant whitespace and lowercase all
    characters
    :param document: string
    :return: processed unicode string
    """
    document = to_unicode(document)
    document = non_plain_re.sub(' ', document)
    document = proc.strip_non_alphanum(document)
    document = proc.strip_numeric(document)
    document = proc.strip_multiple_whitespaces(document)
    document = deaccent(document)
    return document.lower()

def process(document):
    """
    Tokenize a document (a tweet) removing:
    - punctuation
    - URLs and Twitter handles
    - Uppercases
    - Stopword
    - Whitespace
    :param document: string
    :returns: a list of strings
    """
    wordbag = list()
    for token in set(remove_non_plain(document).split()):
        if token not in stopwords and token != '' \
           and token != 'rt':
            wordbag.append(token)
    return wordbag

def init_counter(corpus):
    """
    Creates a collections.Counter object from a corpus.
    :param corpus: iterator or iterable of lists of strings
    :returns: Counter
    """
    ctr = Counter()
    for worbag in corpus:
        ctr.update(worbag)

    return ctr
