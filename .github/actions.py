import os
import json
import copy
import re
import shutil

from bs4 import BeautifulSoup


INDEX_FILE = "index.html"
TEMPLATE_FILE = "pkg_template.html"


def normalize(name):
    """ From PEP503 : https://www.python.org/dev/peps/pep-0503/ """
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_issue(issue_ctx):
    arguments = {}

    parts = issue_ctx['body'].split('- **')[1:]      # Ignore the first one : it's the title
    for text_arg in parts:
        arg_name, arg_value = text_arg.split(':**')
        arg_name, arg_value = arg_name.strip(), arg_value.strip()
        
        if arg_name == "Long description":
            # Special case, where we have more than 1 line : it contain HTML code
            arg_value = arg_value.split('```')[1] if '```' in arg_value else arg_value.split('`')[1]
            
            code_lang = arg_value.split('\n')[0].strip()
            if code_lang != 'html':
                raise ValueError("The {} argument should contain a HTML code section. But it contain {} code.".format(arg_name, code_lang))

            arg_value = "\n".join(arg_value.split('\n')[1:])
        else:
            if "\n" in arg_value:
                raise ValueError("The {} argument should be a single line. Current value : {}".format(arg_name, arg_value))
        
        arguments[arg_name.lower()] = arg_value
    return arguments


def print_args(args):
    print("\n--- Arguments detected from issue ---\n")
    for arg_name, arg_value in args.items():
        print("\t{} : {}".format(arg_name, arg_value))
    print("\n")


def check_args(args, must_have):
    for name in must_have:
        if name not in args:
            raise ValueError("Couldn't find argument {}".format(name))
        if args[name].strip() == "":
            raise ValueError("Argument {} is empty. Please specify it".format(name))


def package_exists(soup, package_name):
    package_ref = package_name + "/"
    for anchor in soup.find_all('a'):
        if anchor['href'] == package_ref:
            return True
    return False


def register(issue_ctx):
    args = parse_issue(issue_ctx)
    print_args(args)
    check_args(args, ['package name', 'version', 'author', 'short description', 'long description', 'homepage', 'link'])
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    if package_exists(soup, args['package name']):
        raise ValueError("Package {} seems to already exists".format(args['package name']))

    # Create a new anchor element for our new package
    last_anchor = soup.find_all('a')[-1]        # Copy the last anchor element
    new_anchor = copy.copy(last_anchor)
    new_anchor['href'] = "{}/".format(args['package name'])
    new_anchor.contents[0].replace_with(args['package name'])
    spans = new_anchor.find_all('span')
    spans[1].string = args['version']       # First span contain the version
    spans[2].string = args['short description']       # Second span contain the short description

    # Add it to our index and save it
    last_anchor.insert_after(new_anchor)
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))

    # Then get the template, replace the content and write to the right place
    with open(TEMPLATE_FILE) as temp_file:
        template = temp_file.read()

    template = template.replace("_package_name", args['package name'])
    template = template.replace("_version", args['version'])
    template = template.replace("_link", "{}#egg={}-{}".format(args['link'], normalize(args['package name']), args['version']))
    template = template.replace("_homepage", args['homepage'])
    template = template.replace("_author", args['author'])
    template = template.replace("_long_description", args['long description'])

    os.mkdir(args['package name'])
    package_index = os.path.join(args['package name'], INDEX_FILE)
    with open(package_index, "w") as f:
        f.write(template)


def update(issue_ctx):
    args = parse_issue(issue_ctx)
    print_args(args)
    check_args(args, ['package name', 'new version', 'link for the new version'])
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    if not package_exists(soup, args['package name']):
        raise ValueError("Package {} seems to not exists".format(args['package name']))

    # Change the version in the main page
    anchor = soup.find('a', attrs={"href": "{}/".format(args['package name'])})
    spans = anchor.find_all('span')
    spans[1].string = args['new version']
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))

    # Change the package page
    index_file = os.path.join(args['package name'], INDEX_FILE) 
    with open(index_file) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    # Create a new anchor element for our new version
    last_anchor = soup.find_all('a')[-1]        # Copy the last anchor element
    new_anchor = copy.copy(last_anchor)
    new_anchor['href'] = "{}#egg={}-{}".format(args['link for the new version'], normalize(args['package name']), args['new version'])

    # Add it to our index
    last_anchor.insert_after(new_anchor)

    # Change the latest version
    soup.html.body.div.section.find_all('span')[1].contents[0].replace_with(args['new version']) 

    # Save it
    with open(index_file, 'wb') as index:
        index.write(soup.prettify("utf-8"))


def delete(issue_ctx):
    args = parse_issue(issue_ctx)
    print_args(args)
    check_args(args, ['package name'])
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    if not package_exists(soup, args['package name']):
        raise ValueError("Package {} seems to not exists".format(args['package name']))

    # Remove the package directory
    shutil.rmtree(args['package name'])

    # Find and remove the anchor corresponding to our package
    anchor = soup.find('a', attrs={"href": "{}/".format(args['package name'])})
    anchor.extract()
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))


def main():
    # Get the context from the environment variable
    context = json.loads(os.environ['GITHUB_CONTEXT'])
    issue_ctx = context['event']['issue']

    labels = [label['name'] for label in issue_ctx['labels']]

    if 'register-package' in labels:
        register(issue_ctx)

    if 'update-package' in labels:
        update(issue_ctx)

    if 'delete-package' in labels:
        delete(issue_ctx)


if __name__ == "__main__":
    main()
