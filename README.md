<h1 align="center">github-hosted-pypi</h1>

<p align="center">
Make all your private packages accessible in one place<br>with this github-hosted PyPi index
</p>

---

<p align="center">
  <a href="#description">Description</a> •
  <a href="#try-it-">Try it !</a> •
  <a href="#get-started">Get Started</a> •
  <a href="#modify-indexed-packages">Modify indexed packages</a> •
  <a href="#contribute">Contribute</a> •
  <a href="#references">References</a>
</p>

---

## Features

* **:octocat: Github-hosted**
* **🚀 Template ready to deploy**
* **🔆 Easy to use** through Github Actions

## Description

This repository is a Github page used as a PyPi index, conform to [PEP503](https://www.python.org/dev/peps/pep-0503/).

You can use it to group all your packages in one place, and access it easily through `pip`, almost like any other package publicly available !

---

_While the PyPi index is public, private packages indexed here are kept private : you will need Github authentication to be able to retrieve it._

## Try it !

Visit [astariul.github.io/github-hosted-pypi/](http://astariul.github.io/github-hosted-pypi/) and try to install packages indexed there !

---

Try to install the package `public-hello` :
```console
pip install public-hello --extra-index-url https://astariul.github.io/github-hosted-pypi/
```

It will also install the package `mydependency`, automatically ! 

Try it with :

```python
from public_hello import hi
print(hi())
```

You can also install a specific version :

```console
pip install public-hello==0.1 --extra-index-url https://astariul.github.io/github-hosted-pypi/
```

---

Now try to install the package `private-hello` :
```console
pip install private-hello --extra-index-url https://astariul.github.io/github-hosted-pypi/
```

_It will not work, because it's private and only me can access it !_

## Get started

* Use this template and create your own repository : [![Generic badge](https://img.shields.io/badge/Use%20this%20template-blueviolet.svg)](https://github.com/astariul/github-hosted-pypi/generate)
* Customize `index.html` and `pkg_template.html` to your liking
* You're ready to go !

## Modify indexed packages

Now that your PyPi index is setup, you can register / update / delete packages indexed.  
_Github actions are setup to do it automatically for you._

You just have to :
* Open an issue with the appropriate template
* Fill the information of the template (replace the comments)
* Wait a bit
* Check the new PR opened (ensure the code added correspond to what you want)
* Merge the PR

## Contribute

Issues and PR are welcome !

If you come across anything weird / that can be improved, please get in touch !

## References

**This is greatly inspired from [this repository](https://github.com/ceddlyburge/python-package-server).**  
It's just a glorified version, with cleaner pages and github actions for easily adding, updating and removing packages from your index.

Also check the [blogpost](https://www.freecodecamp.org/news/how-to-use-github-as-a-pypi-server-1c3b0d07db2/) of the original author !

---

_Icon used in the page was made by [Freepik](https://www.flaticon.com/authors/freepik) from [Flaticon](https://www.flaticon.com/)_
