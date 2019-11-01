import re
from gensim.utils import deaccent

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

# regexp for matching URLs
urls = r"((\w+:\/\/)[-a-zA-Z0-9:@;?&=\/%\+\.\*!'\(\),\$_\{\}\^~\[\]`#|]+)"

multi_pattern = '|'.join([tw_handles, urls])
# regexp for Twitter Handles or URLs/URIs
non_plain_re = re.compile(multi_pattern, re.UNICODE)
####################

def remove_non_plain(document):
    """
    Replaces urls, @usernames and #tags with an empty string
    :param document: string
    """
    return non_plain_re.sub('', document)


def strip_punctuation(token):
    """
    Remove accents and trailing punctuation marks
    from a given token
    :param token: string
    """
    return deaccent(token).strip('",.:;?¿-()[]<>!¡“”| ')

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
        if token not in stopwords and token != '':
            wordbag.append(token)
    return wordbag

def build_counter(doc_stream):
    """
    Creates a collections.Counter object from a corpus.
    :param doc_stream: iterator or iterable of lists of strings
    :returns: Counter
    """
    ctr = Counter()
    for document in doc_stream:
        ctr.update(document)
     
    return ctr