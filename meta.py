import collections
from os import makedirs
from html.parser import HTMLParser

self_closing_tags = [
    'area', 'base', 'br', 'col', 'embed',
    'hr', 'img', 'input', 'link', 'meta',
    'param', 'source', 'track', 'wbr'
]

potentially_unclosed_tags = [
    'html',
    'head', 'body',
    'thead', 'tbody', 'tfoot',
    'tr', 'li',
    'th', 'td', 'dt', 'dd',
    'p'
]

tags_hierarchy = {
    'html': 1,
    'head': 2, 'body': 2,
    'thead': 3, 'tbody': 3, 'tfoot': 3,
    'tr': 4, 'li': 4,
    'th': 5, 'td': 5, 'dt': 5, 'dd': 5,
    'p': 6
    # else 7
}

generated_html_path = 'generated/html'
generated_packages_path = 'generated/packages'


class HtmlClassGenerator:
    def __init__(self, package):
        self.package = package
        self.tag_occurrence = {}

    def create_from_html_tag(self, tag_name, attributes, base_class):
        if tag_name in self.tag_occurrence:
            self.tag_occurrence[tag_name] += 1
        else:
            self.tag_occurrence[tag_name] = 1

        class_name = tag_name.capitalize() + str(self.tag_occurrence[tag_name])

        args = {
            'imports': 'from .%s import %s' % (base_class.lower(), base_class) if base_class else '',
            'class_name': class_name,
            'base_class': base_class,
            'tag_name': tag_name,
            'attributes': '\n'.join(['\t\tself._%s = "%s"' % attribute for attribute in attributes]) if attributes else ''
        }

        template = '''# Generated by HtmlTagClassGenerator
{imports}


class {class_name}({base_class}):
\tdef __init__(self):
\t\tself.tag = "{tag_name}"
{attributes}
'''

        module = '%s/%s/%s.py' % (generated_packages_path, self.package, class_name.lower())
        with open(module, 'w') as file:
            file.write(template.format(**args))

        return class_name


class MetaHTMLParser(HTMLParser):
    tag_chain = [{'name': '', 'class': ''}]
    class_generator = None
    package_path = None

    def generate(self, html_file, package_name):
        self.package_path = generated_packages_path + '/' + package_name + '/'
        self.class_generator = HtmlClassGenerator(package_name)

        with open(html_file, 'r') as file:
            makedirs(self.package_path, exist_ok=True)
            self.feed(str(file.read()))

        package_init_code = '''import glob
from os.path import dirname, basename, isfile

modules = glob.glob(dirname(__file__) + "/*.py")

__all__ = [basename(module)[:-3] for module in modules if isfile(module) and not module.endswith('__init__.py')]
'''
        with open(self.package_path + '__init__.py', 'w') as file:
            file.write(package_init_code)

    def handle_starttag(self, tag, attrs):
        for prev_tag in reversed(self.tag_chain):
            if prev_tag['name'] in potentially_unclosed_tags \
                    and tags_hierarchy[prev_tag['name']] >= tags_hierarchy.get(tag, 7):
                self.tag_chain.pop()
            else:
                break

        tag_class = self.class_generator.create_from_html_tag(tag, attrs, self.tag_chain[-1]['class'])

        if tag not in self_closing_tags:
            self.tag_chain.append({'name': tag, 'class': tag_class})

    def handle_endtag(self, tag):
        if tag not in self_closing_tags:
            if self.tag_chain:
                if tag not in potentially_unclosed_tags:
                    for prev_tag in reversed(self.tag_chain):
                        if prev_tag['name'] in potentially_unclosed_tags:
                            self.tag_chain.pop()
                        else:
                            break
                self.tag_chain.pop()
            else:
                print("ERROR: Opening and closing tags mismatch.")

    def reset(self):
        self.tag_chain = [{'name': '', 'class': ''}]
        super().reset()


def object_to_html(tag_object, indentation=0):
    args = {
        'indentation': '\t' * indentation,
        'tag': tag_object.tag,
        'properties': ''.join(
            ' %s="%s"' % (attribute[1:], value) for attribute, value in vars(tag_object).items() if attribute[0] == '_'),
        'elements': '\n'.join(
            [object_to_html(subclass(), indentation + 1) for subclass in tag_object.__class__.__subclasses__()]
        )
    }

    if tag_object.tag in self_closing_tags:
        template = '''{indentation}<{tag}{properties}>'''
    else:
        template = '''{indentation}<{tag}{properties}>
{elements}
{indentation}</{tag}>'''

    return template.format(**args)


def generate_html_from_package(package_name):
    package = '.'.join(generated_packages_path.split('/') + [package_name])
    module = __import__(package, globals(), locals(), ['*'])
    makedirs(generated_html_path, exist_ok=True)
    generated_html = '%s/%s.html' % (generated_html_path, package_name)
    with open(generated_html, 'w') as file:
        file.write(object_to_html(module.html1.Html1()))


class CSSTokenizer:
    def __init__(self, str):
        self.token_type = ''
        self.token_value = ''
        self.expect_property = False
        self.it = iter(str)
        self.last_ch = next(self.it)

    def skip_space(self):
        while self.last_ch.isspace():
            self.last_ch = next(self.it)

    def consume_char(self):
        self.token_value += self.last_ch
        self.last_ch = next(self.it)

    def tokens(self):
        while True:
            self.token_type = ''
            self.token_value = ''

            self.skip_space()

            if not self.expect_property:  # outside { } - search for selector
                if self.last_ch.isalpha() or self.last_ch in ['_', '-', '#', '.']:  # selector
                    self.token_type = 'selector'

                    while self.last_ch.isalnum() or self.last_ch in ['_', '-', '.', '#', ',', '>', '+', '~', ' ']:
                        self.consume_char()

                    if self.last_ch == '{':
                        self.token_value.rstrip()
                        yield self.token_type, self.token_value

                        self.last_ch = next(self.it)
                        self.expect_property = True
                    else:
                        print("ERROR: Unexpected character in selector: " + self.last_ch)
                        return
                else:
                    print("ERROR: expected selector. Unexpected character: " + self.last_ch)
                    return
            else:  # inside { }
                if self.last_ch == '}':
                    self.last_ch = next(self.it)
                    self.expect_property = False
                    yield 'prop_end', ''

                    self.tokens()
                elif self.last_ch.isalpha() or self.last_ch == '_':  # property key
                    self.token_type = 'property'

                    while self.last_ch.isalnum() or self.last_ch in ['_', '-']:  # consume property key
                        self.consume_char()

                    self.skip_space()

                    if self.last_ch == ':':
                        self.consume_char()
                        self.skip_space()

                        while not self.last_ch.isspace() and self.last_ch != ';':  # consume property value
                            self.consume_char()

                        yield self.token_type, self.token_value

                        self.skip_space()

                        if self.last_ch == ';':
                            self.last_ch = next(self.it)
                    else:
                        print("ERROR: expected property value.")
                        return


class MetaCSSParser:
    package_path = None

    def generate(self, css_file, package_name):
        self.package_path = generated_packages_path + '/css/' + package_name + '/'
        with open(css_file, 'r') as file:
            makedirs(self.package_path, exist_ok=True)
            self.parse(str(file.read()))

        package_init_code = '''import glob
from os.path import dirname, basename, isfile

modules = glob.glob(dirname(__file__) + "/*.py")

__all__ = [basename(module)[:-3] for module in modules if isfile(module) and not module.endswith('__init__.py')]
'''
        with open(self.package_path + '__init__.py', 'w') as file:
            file.write(package_init_code)

    def parse(self, text):
        id = 0
        token_iter = iter(CSSTokenizer(text).tokens())
        for (token_type, token_value) in token_iter:
            if token_type == 'selector':
                id += 1
                declarations = []
                for (token_type, token_value) in token_iter:
                    if token_type == 'property':
                        declarations.append(token_value)
                    else:
                        break

                self.generate_class("CSS" + str(id), declarations)
            else:
                print("ERROR: Expected selector.")

    def generate_class(self, class_name, declarations):
        args = {
            'class_name': class_name,
            'attributes': '\n'.join(
                ['\t\tself["%s"] = "%s"' % tuple(declaration.split(":")) for declaration in declarations]) if declarations else ''
        }

        template = '''# Generated by MetaCSSParser
class {class_name}(dict):
\tdef __init__(self, *args, **kwargs):
\t\tself.store = dict()
\t\tself.update(dict(*args, **kwargs))
{attributes}
'''

        module = self.package_path + class_name.lower() + '.py'
        with open(module, 'w') as file:
            file.write(template.format(**args))

        return class_name