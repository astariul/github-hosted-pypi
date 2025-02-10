import os
import copy
import re
import shutil

from bs4 import BeautifulSoup


INDEX_FILE = "index.html"
TEMPLATE_FILE = "pkg_template.html"
YAML_ACTION_FILES = [".github/workflows/delete.yml", ".github/workflows/update.yml"]

INDEX_CARD_HTML = '''
<a class="card" href="">
    placeholder_name
    <span>
    </span>
    <span class="version">
        placehholder_version
    </span>
    <br/>
    <span class="description">
        placeholder_description
    </span>
</a>'''


def normalize(name):
    """ From PEP503 : https://www.python.org/dev/peps/pep-0503/ """
    return re.sub(r"[-_.]+", "-", name).lower()


def normalize_version(version):
    version = version.lower()
    return version[1:] if version.startswith("v") else version


def is_stable(version):
    return not ("dev" in version or "a" in version or "b" in version or "rc" in version)


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


def register(pkg_name, version, author, short_desc, homepage):
    link = f'git+{homepage}@{version}'
    long_desc = transform_github_url(homepage)
    # Read our index first
    with open(INDEX_FILE) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    norm_pkg_name = normalize(pkg_name)
    norm_version = normalize_version(version)

    if package_exists(soup, norm_pkg_name):
        raise ValueError(f"Package {norm_pkg_name} seems to already exists")

    # Create a new anchor element for our new package
    placeholder_card = BeautifulSoup(INDEX_CARD_HTML, 'html.parser')
    placeholder_card = placeholder_card.find('a')
    new_package = copy.copy(placeholder_card)
    new_package['href'] = f"{norm_pkg_name}/"
    new_package.contents[0].replace_with(pkg_name)
    spans = new_package.find_all('span')
    spans[1].string = norm_version  # First span contain the version
    spans[2].string = short_desc    # Second span contain the short description

    # Add it to our index and save it
    soup.find('h6', class_='text-header').insert_after(new_package)
    with open(INDEX_FILE, 'wb') as index:
        index.write(soup.prettify("utf-8"))

    # Then get the template, replace the content and write to the right place
    with open(TEMPLATE_FILE) as temp_file:
        template = temp_file.read()

    template = template.replace("_package_name", pkg_name)
    template = template.replace("_norm_version", norm_version)
    template = template.replace("_version", version)
    template = template.replace("_link", f"{link}#egg={norm_pkg_name}-{norm_version}")
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
    norm_version = normalize_version(version)

    if not package_exists(soup, norm_pkg_name):
        raise ValueError(f"Package {norm_pkg_name} seems to not exists")

    # Change the version in the main page (only if stable)
    if is_stable(version):
        anchor = soup.find('a', attrs={"href": f"{norm_pkg_name}/"})
        spans = anchor.find_all('span')
        spans[1].string = norm_version
        with open(INDEX_FILE, 'wb') as index:
            index.write(soup.prettify("utf-8"))

    # Change the package page
    index_file = os.path.join(norm_pkg_name, INDEX_FILE) 
    with open(index_file) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
        
    # Extract the URL from the onclick attribute
    button = soup.find('button', id='repoHomepage')
    if button:
        link = button.get("onclick")[len("openLinkInNewTab('"):-2]
    else:
        raise Exception("Homepage URL not found")

    # Create a new anchor element for our new version
    original_div = soup.find('section', class_='versions').findAll('div')[-1]
    new_div = copy.copy(original_div)
    anchor = new_div.find('a')
    new_div['onclick'] = f"load_readme('{version}', scroll_to_div=true);"
    new_div['id'] = version
    new_div['class'] = ""
    if not is_stable(version):
        new_div['class'] += "prerelease"
    else:
        # replace the latest main version
        main_version_span = soup.find('span', id='latest-main-version')
        main_version_span.string = version
    anchor.string = norm_version
    anchor['href'] = f"git+{link}@{version}#egg={norm_pkg_name}-{norm_version}"

    # Add it to our index
    original_div.insert_after(new_div)

    # Change the latest version (if stable)
    if is_stable(version):
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
        raise ValueError(f"Package {norm_pkg_name} seems to not exists")

    # Remove the package directory
    shutil.rmtree(norm_pkg_name)

    # Find and remove the anchor corresponding to our package
    anchor = soup.find('a', attrs={"href": f"{norm_pkg_name}/"})
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
        delete(
            pkg_name=os.environ["PKG_NAME"]
        )
    elif action == "UPDATE":
        update(
            pkg_name=os.environ["PKG_NAME"],
            version=os.environ["PKG_VERSION"]
        )


if __name__ == "__main__":
    main()
