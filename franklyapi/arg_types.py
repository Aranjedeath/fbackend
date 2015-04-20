import urlparse


def url_type(data):
    parts = urlparse.urlsplit(data)
    if not parts.scheme or not parts.netloc:
        raise ValueError('Not a valid url')
    return data
