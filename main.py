import traceback
from os import path
from meta import MetaHTMLParser, generate_html_from_package, generated_packages_path, generated_html_path

html_parser = MetaHTMLParser()

while True:
    try:
        html_file = input("Enter HTML file path (e.g 'resources/index.html'): ")
        package_name = path.splitext(path.basename(html_file))[0].lower()

        print("Generating package '%s'" % package_name)
        html_parser.generate(html_file, package_name)
        print("Package generated: ./%s/%s" % (generated_packages_path, package_name))

        print("Generating HTML from '%s' package" % package_name)
        generate_html_from_package(package_name)
        print("HTML file generated: ./%s/%s.html" % (generated_html_path, package_name))
    except Exception as e:
        print("ERROR:", traceback.format_exc())
    finally:
        html_parser.reset()
