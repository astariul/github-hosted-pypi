import os
import json


def is_label_x(context, label_name):
    return label_name in [label['name'] for label in context['event']['issue']['labels']]


def main():
    # Get the context from the environment variable
    context = json.loads(os.environ['GITHUB_CONTEXT'])

    if is_label_x(context, 'register-package'):
        print("This is a register job !")

    if is_label_x(context, 'update-package'):
        print("This is a update job !")


if __name__ == "__main__":
    main()