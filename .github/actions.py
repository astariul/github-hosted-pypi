import os
import json


def is_register_job(context):
    return "register-package" in [label.name for label in context.event.issue.labels]


def is_update_job(context):
    return "update-package" in [label.name for label in context.event.issue.labels]


def main():
    # Get the context from the environment variable
    context = json.loads(os.environ['GITHUB_CONTEXT'])

    if is_register_job(context):
        print("This is a register job !")

    if is_update_job(context):
        print("This is a update job !")


if __name__ == "__main__":
    main()