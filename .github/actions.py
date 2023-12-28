import os
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


def transform_github_url(input_url):
    # Split the input URL to extract relevant information
    parts = input_url.rstrip('/').split('/')
    username, repo = parts[-2], parts[-1]

    # Create the raw GitHub content URL
    raw_url = f'https://raw.githubusercontent.com/{username}/{repo}/main/README.md'
    return raw_url


def find_homepage_url(soup):
    # Find the button with the onclick attribute containing the URL
    button = soup.find("button", onclick=lambda x: "location.href" in x)
    if button:
        # Extract the URL from the onclick attribute
        onclick_attr = button.get("onclick")
        url_start = onclick_attr.find("'") + 1
        url_end = onclick_attr.rfind("'")
        homepage_url = onclick_attr[url_start:url_end]
        return homepage_url
    else:
        return None  # If the button is not found


def register(pkg_name, version, author, short_desc, homepage):
    link = f'git+{homepage}@{version}'
    long_desc = transform_github_url(homepage)
    # Read our index first
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    norm_pkg_name = normalize(pkg_name)

    if package_exists(soup, norm_pkg_name):
        raise ValueError("Package {} seems to already exists".format(norm_pkg_name))

    # Create a new anchor element for our new package
    placeholder_card = soup.find('a', id='placeholder_card')
    new_skill = copy.copy(placeholder_card)
    new_skill['href'] = "{}/".format(norm_pkg_name)
    new_skill.attrs.pop('style', None)
    new_skill.attrs.pop('id', None)
    new_skill.contents[0].replace_with(pkg_name)
    spans = new_skill.find_all('span')
    spans[1].string = version       # First span contain the version
    spans[2].string = short_desc    # Second span contain the short description

    # Add it to our index and save it
    placeholder_card.insert_after(new_skill)
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
    template = template.replace("_latest_main", version)

    os.mkdir(norm_pkg_name)
    package_index = os.path.join(norm_pkg_name, INDEX_FILE)
    with open(package_index, "w") as f:
        f.write(template)


def update(pkg_name, version):
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
        
    # Extract the URL from the onclick attribute
    button = soup.find('a', id='repoHomepage')
    if button:
        link = button.get("href")
    else:
        raise Exception("Homepage URL not found")

    # Create a new anchor element for our new version
    original_div = soup.find('section', class_='versions').findAll('div')[-1]
    new_div = copy.copy(original_div)
    anchors = new_div.find_all('a')
    new_div['onclick'] = "load_readme('{}', scroll_to_div=true)".format(version)
    new_div['id'] = version
    new_div['class'] = ""
    if 'dev' in version:
        new_div['class'] += "prerelease"
    else:
        # replace the latest main version
        main_version_span = soup.find('span', id='latest-main-version')
        main_version_span.string = version
    anchors[0].string = version
    anchors[1]['href'] = "git+{}@{}#egg={}-{}".format(link,version,norm_pkg_name,version)

    # Add it to our index
    original_div.insert_after(new_div)

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
            homepage=os.environ["PKG_HOMEPAGE"],
        )
    elif action == "DELETE":
        delete(pkg_name=os.environ["PKG_NAME"])
    elif action == "UPDATE":
        update(
            pkg_name=os.environ["PKG_NAME"],
            version=os.environ["PKG_VERSION"]
        )


if __name__ == "__main__":
    main()
