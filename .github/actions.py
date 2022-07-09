import os
import json
import copy
import re
import shutil

from bs4 import BeautifulSoup


INDEX_FILE = "index.html"
TEMPLATE_FILE = "pkg_template.html"
YAML_ACTION_FILES = [".github/workflows/delete.yml", ".github/workflows/update.yml"]


def normalize(name):
    """ From PEP503 : https://www.python.org/dev/peps/pep-0503/ """
    return re.sub(r"[-_.]+", "-", name).lower()


def package_exists(soup, package_name):
    package_ref = package_name + "/"
    for anchor in soup.find_all('a'):
        if anchor['href'] == package_ref:
            return True
    return False


def register(pkg_name, version, author, short_desc, long_desc, homepage, link):
    # Read our index first
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    norm_pkg_name = normalize(pkg_name)

    if package_exists(soup, norm_pkg_name):
        raise ValueError("Package {} seems to already exists".format(norm_pkg_name))

    # Create a new anchor element for our new package
    last_anchor = soup.find_all('a')[-1]        # Copy the last anchor element
    new_anchor = copy.copy(last_anchor)
    new_anchor['href'] = "{}/".format(norm_pkg_name)
    new_anchor.contents[0].replace_with(pkg_name)
    spans = new_anchor.find_all('span')
    spans[1].string = version       # First span contain the version
    spans[2].string = short_desc    # Second span contain the short description

    # Add it to our index and save it
    last_anchor.insert_after(new_anchor)
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))

    # Then get the template, replace the content and write to the right place
    with open(TEMPLATE_FILE) as temp_file:
        template = temp_file.read()

    template = template.replace("_package_name", pkg_name)
    template = template.replace("_version", version)
    template = template.replace("_link", "{}#egg={}-{}".format(link, norm_pkg_name, version))
    template = template.replace("_homepage", homepage)
    template = template.replace("_author", author)
    template = template.replace("_long_description", long_desc)

    os.mkdir(norm_pkg_name)
    package_index = os.path.join(norm_pkg_name, INDEX_FILE)
    with open(package_index, "w") as f:
        f.write(template)


def update(pkg_name, version, link):
    # Read our index first
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    norm_pkg_name = normalize(pkg_name)

    if not package_exists(soup, norm_pkg_name):
        raise ValueError("Package {} seems to not exists".format(norm_pkg_name))

    # Change the version in the main page
    anchor = soup.find('a', attrs={"href": "{}/".format(norm_pkg_name)})
    spans = anchor.find_all('span')
    spans[1].string = version
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))

    # Change the package page
    index_file = os.path.join(norm_pkg_name, INDEX_FILE) 
    with open(index_file) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")

    # Create a new anchor element for our new version
    last_anchor = soup.find_all('a')[-1]        # Copy the last anchor element
    new_anchor = copy.copy(last_anchor)
    new_anchor['href'] = "{}#egg={}-{}".format(link, norm_pkg_name, version)

    # Add it to our index
    last_anchor.insert_after(new_anchor)

    # Change the latest version
    soup.html.body.div.section.find_all('span')[1].contents[0].replace_with(version) 

    # Save it
    with open(index_file, 'wb') as index:
        index.write(soup.prettify("utf-8"))


def delete(pkg_name):
    # Read our index first
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    norm_pkg_name = normalize(pkg_name)

    if not package_exists(soup, norm_pkg_name):
        raise ValueError("Package {} seems to not exists".format(norm_pkg_name))

    # Remove the package directory
    shutil.rmtree(norm_pkg_name)

    # Find and remove the anchor corresponding to our package
    anchor = soup.find('a', attrs={"href": "{}/".format(norm_pkg_name)})
    anchor.extract()
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))


def main():
    # Call the right method, with the right arguments
    action = os.environ["PKG_ACTION"]

    if action == "REGISTER":
        register(
            pkg_name=os.environ["PKG_NAME"],
            version=os.environ["PKG_VERSION"],
            author=os.environ["PKG_AUTHOR"],
            short_desc=os.environ["PKG_SHORT_DESC"],
            long_desc=os.environ["PKG_LONG_DESC"],
            homepage=os.environ["PKG_HOMEPAGE"],
            link=os.environ["PKG_LINK"],
        )
    elif action == "DELETE":
        delete(pkg_name=os.environ["PKG_NAME"])
    elif action == "UPDATE":
        update(
            pkg_name=os.environ["PKG_NAME"],
            version=os.environ["PKG_VERSION"],
            link=os.environ["PKG_LINK"],
        )


if __name__ == "__main__":
    main()
