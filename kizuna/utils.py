from urllib.parse import urlparse, urlencode, urlunparse


def build_url(baseurl, path, args_dict=None):
    # Returns a list in the structure of urlparse.ParseResult
    url_parts = list(urlparse(baseurl))
    url_parts[2] = path
    if args_dict:
        url_parts[4] = urlencode(args_dict)
    return urlunparse(url_parts)


def slack_link(text, url):
    return '<{}|{}>'.format(url, text)
