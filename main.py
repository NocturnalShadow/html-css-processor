import traceback
import collections
from os import makedirs, path
from meta import MetaCSSParser, MetaHTMLParser, generate_html_from_package, generated_packages_path, generated_html_path

html_parser = MetaHTMLParser()
css_parser = MetaCSSParser()

while True:
    try:
        file = input("Enter HTML or CSS file path (e.g 'resources/index.html'): ")
        filename, file_extension = path.splitext(path.basename(file))
        package_name = filename.lower()

        if file_extension == '.html':
            print("Generating package '%s'" % package_name)
            html_parser.generate(file, package_name)
            print("Package generated: ./%s/%s" % (generated_packages_path, package_name))

            print("Generating HTML from '%s' package" % package_name)
            generate_html_from_package(package_name)
            print("HTML file generated: ./%s/%s.html" % (generated_html_path, package_name))
        elif file_extension == '.css':
            print("Generating package '%s'" % package_name)
            css_parser.generate(file, 'styles')
        else:
            print("Unsupported file extension.")
    except Exception as e:
        print("ERROR:", traceback.format_exc())
    finally:
        html_parser.reset()



