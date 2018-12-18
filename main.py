import traceback
import collections
from os import makedirs, path
from meta import MetaHTMLParser, generate_html_from_package, generated_packages_path, generated_html_path

# html_parser = MetaHTMLParser()
#
# while True:
#     try:
#         html_file = input("Enter HTML file path (e.g 'resources/index.html'): ")
#         package_name = path.splitext(path.basename(html_file))[0].lower()
#
#         print("Generating package '%s'" % package_name)
#         html_parser.generate(html_file, package_name)
#         print("Package generated: ./%s/%s" % (generated_packages_path, package_name))
#
#         print("Generating HTML from '%s' package" % package_name)
#         generate_html_from_package(package_name)
#         print("HTML file generated: ./%s/%s.html" % (generated_html_path, package_name))
#     except Exception as e:
#         print("ERROR:", traceback.format_exc())
#     finally:
#         html_parser.reset()


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

                    while self.last_ch.isalnum() or self.last_ch in ['_', '-', '.', '#']:  # consume selector
                        self.consume_char()

                    yield self.token_type, self.token_value

                    self.skip_space()

                    if self.last_ch in [',', '>', '+', '~']:
                        yield 'op', self.last_ch
                        self.last_ch = next(self.it)
                    elif self.last_ch.isalpha() or self.last_ch in ['_', '-', '#', '.']:
                        yield 'op', ' '
                    elif self.last_ch == '{':
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
        token_iter = iter(CSSTokenizer(text).tokens())
        for (token_type, token_value) in token_iter:
            pass  # TODO


css_parser = MetaCSSParser()

css_parser.generate('resources/styles.css', 'styles')
