def utf8bytes(maybe_text):
    if maybe_text is None:
        return
    if isinstance(maybe_text, type(b'')):
        return maybe_text
    return maybe_text.encode('utf-8')


def utf8text(maybe_bytes, errors='strict'):
    if maybe_bytes is None:
        return
    if isinstance(maybe_bytes, type(u'')):
        return maybe_bytes
    return maybe_bytes.decode('utf-8', errors)
