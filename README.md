<h1 align="center">github-hosted-pypi</h1>

<p align="center">
Make all your private packages accessible in one place<br>with this github-hosted PyPi index
</p>

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

---

Now try to install the package `private-hello` :
```console
pip install private-hello --extra-index-url https://astariul.github.io/github-hosted-pypi/
```

It will not work, because it's private and only me can access it !

## Get started

* Use this template and create your own repository : <a class="btn btn-primary ml-2" href="/astariul/github-hosted-pypi/generate">Use this template</a>
* Customize `index.html` and `pkg_template.html` to your liking
* You're ready to go !

## Modify indexed packages

TODO

## Contribute

TODO

## References

**This repository is greatly inspired from [this repository](https://github.com/ceddlyburge/python-package-server).**  
It's just a glorified version, with cleaner pages and github actions for easily adding, updating and removing packages from your repository.

Also check the [blogpost](https://www.freecodecamp.org/news/how-to-use-github-as-a-pypi-server-1c3b0d07db2/) of the original author !

---

_Icon used in the page was made by [Freepik](https://www.flaticon.com/authors/freepik) from [Flaticon](https://www.flaticon.com/)_
