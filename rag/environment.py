from jinja2 import Environment, PackageLoader

def environment() -> Environment:
    return Environment(loader=PackageLoader('rag', 'templates'),)