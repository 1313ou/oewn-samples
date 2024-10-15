import re

# `s´ grave-acute
# ‘s’ lquote-rquote
grave = '`'
acute = '´'
lquote = '‘'
rquote = '’'

quote_pattern = fr'{lquote}[^{rquote}]*{rquote}'

def has_grave_or_acute(input_text):
    return True if grave in input_text or acute in input_text else None


def has_lquote_or_rquote(input_text):
    return True if lquote in input_text or rquote in input_text else None


def has_quote(input_text):
    m = re.findall(quote_pattern, input_text)
    return str(m) if m else None
