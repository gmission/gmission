
__author__ = 'chenzhao'


from flask import g


def contains_sensitive_words(content):
    for word in g.crabwords:  # may be slow
        if word in content:
            return True
    return False

