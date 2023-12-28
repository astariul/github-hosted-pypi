import subprocess

def execute_main(pkg_name, versions, short_desc, homepage):
    #delete
    env = {
        "PKG_ACTION": "DELETE",
        "PKG_NAME": pkg_name
    }
    subprocess.run(['python3', '.github/actions.py'], env=env)
    print("Package {} deleted".format(pkg_name))
    
    #register
    env = {
        "PKG_ACTION": "REGISTER",
        "PKG_NAME": pkg_name,
        "PKG_VERSION": versions[0],
        "PKG_AUTHOR": 'Nicolas Remond',
        "PKG_SHORT_DESC": short_desc,
        "PKG_HOMEPAGE": homepage
    }
    subprocess.run(['python3', '.github/actions.py'], env=env)
    print("Package {} registered".format(pkg_name))
    
    #update
    for version in versions[1:]:
        env = {
            "PKG_ACTION": "UPDATE",
            "PKG_NAME": pkg_name,
            "PKG_VERSION": version
        }
        subprocess.run(['python3', '.github/actions.py'], env=env)
        print("Package {} updated to version {}".format(pkg_name, version))
    print("Package {} Done".format(pkg_name))



if __name__ == "__main__":
    # transformers
    pkg_name = "transformers"
    versions = ["3.0"] 
    short_desc = 'A simulator for electrical components'
    homepage = 'https://github.com/huggingface/transformers'
    execute_main(pkg_name, versions, short_desc, homepage)
    
    # public-hello
    pkg_name = "public-hello"
    versions = ["0.1", "0.2"] 
    short_desc = 'A public github-hosted repo, with a dependency to another package.'
    homepage = 'https://github.com/astariul/public-hello'
    execute_main(pkg_name, versions, short_desc, homepage)
    
    
    # mydependency
    pkg_name = "mydependency"
    versions = ["1.0"] 
    short_desc = 'A public github-hosted repo.'
    homepage = 'https://github.com/astariul/mydependency'
    execute_main(pkg_name, versions, short_desc, homepage)
    
    # private-hello
    pkg_name = "private-hello"
    versions = ["0.4.5"] 
    short_desc = 'This is an example of a private, github-hosted package. Only me can access this repo, you can try to install it with the pip command but a password is required : only people with repo access can download it.'
    homepage = 'https://github.com/astariul/private-hello'
    execute_main(pkg_name, versions, short_desc, homepage)
    
    
