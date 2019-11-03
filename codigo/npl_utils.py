import re
from collections import Counter
from gensim.utils import deaccent
from emoji import get_emoji_regexp
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
# for matching numbers
numbers = r"[^a-z ]\ *([.0-9])*\d"
# for matching emojis
emojis = get_emoji_regexp().pattern

# Master Regexp
multi_pattern = '|'.join([tw_handles, urls, numbers, emojis])
non_plain_re = re.compile(multi_pattern, re.UNICODE)
####################

def remove_non_plain(document):
    """
    Replaces urls, @usernames, #tags, emojis and numbers
    with an empty string.
    :param document: string
    """
    return non_plain_re.sub('', document)


def strip_punctuation(token):
    """
    Remove accents and trailing punctuation marks
    from a given token
    :param token: string
    """
    return deaccent(token).strip('",.:;?¿-()[]<>!¡“”|*/\=+&$% ')

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
    for token in remove_non_plain(document).lower().split():
        token = strip_punctuation(token)
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
    for document in corpus:
        ctr.update(document)

    return ctr
