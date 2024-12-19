xmlIdAttr = '{http://www.w3.org/XML/1998/namespace}id'


def make_qname(namespace: str, name: str) -> str:
    if namespace is not None and len(namespace) > 0:
        return '{' + namespace + '}' + name
    return name


def get_namespace(tag: str) -> str:
    if (len(tag) == 0 or tag[0] != '{'):
        return ''

    if '}' not in tag:
        raise ValueError('No closing brace found')

    return tag.split('{', 1)[1].split('}', 1)[0]


def get_unqualified_name(tag: str) -> str:
    if '}' not in tag:
        return tag

    return tag.split('}', 1)[1]
