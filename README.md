# Griptape Cloud CLI

[![PyPI Version](https://img.shields.io/pypi/v/griptape-cli.svg)](https://pypi.python.org/pypi/griptape-cli)
[![Tests](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

The Griptape CLI is a command-line interface for interacting with features of [Griptape Cloud](https://www.griptape.ai/cloud).
Today, it provides an emulator for Griptape Cloud Skatepark, which allows you to run and test your Structures locally. 

## Prerequisites
    - A GitHub account.
    - Python 3.11.
    - [Poetry](https://python-poetry.org/) for running the example client program.

## Installation 

1. Install griptape-cli
    ```bash
    pipx install griptape-cli
    ```

   You can also install a pre-release version from GitHub.
    ```bash
    git clone https://github.com/griptape-ai/griptape-cli.git
    ```

    ```bash
    pipx install ./griptape-cli
    ```
2. Verify installation
    ```bash
    gt --help
    ```

## Skatepark
You can use the CLI to spin up a local emulator of the Griptape Cloud Skatepark.
Use the Skatepark emulator to develop, test, and validate that your program will operate as expected when deployed as a Griptape Cloud Manage Structure.

1. Start by creating a new repository in your own Github account from the [Managed Structure Template](https://github.com/griptape-ai/managed-structure-template).
    a. Make sure you're logged in to GitHub.
    b. Go to the [Managed Structure Template repo](https://github.com/griptape-ai/managed-structure-template).
    c. Select the *Use this template* drop-down.
    d. Choose *Create a new repository*.
    e. Provide a name for the new repository and (optionally) a description.
    f. Press the *Create repository* button.
    g. You now have a repository in your own GitHub account that is a copy of the Managed Structure Template for you to begin working with.
2. Clone your newly-created repository to a directory in your local development environment so that you can begin authoring your own Griptape Managed Structure.
3. Start the Skatepark emulator.
    ```bash
    gt skatepark start
    ```
4. In a separate terminal window, register a Structure from within the directory of the locally cloned repository.
    ```bash
    gt skatepark register --directory structure/ --main-file structure.py
    ```
    This will result in the ID of the registered Structure. It is important to make note of this ID as it will be used to distinguish which Structure you want to run. You can register any number of Structures.

    The example client program uses the environment variable `GT_STRUCTURE_ID` to determine which Structure to run.
    Set this environment variable to the Structure ID you registered in the previous step.
    ```bash
    export GT_STRUCTURE_ID={STRUCTURE_ID}
    ```

    Or you can register and set the environment variable in one step.
    ```bash
    export GT_STRUCTURE_ID=$(gt skatepark register --directory structure/ --main-file structure.py)
    ```

> [!IMPORTANT]
> Structures registered with the emulator are not persisted across restarts. You will need to re-register the Structure each time you restart the emulator.
5. Confirm that the Structure is registered.
    ```bash
    gt skatepark list
    ```
    You should see a list of registered Structures and the directories they point to, confirming that your Managed Structure was properly registered
6. You can load environment variables into your Structure by creating an `.env` file in the directory of the Structure you registered. 
    a. Create a file named `.env` in the `structure/` directory.
    b. Open the `.env` file in a text editor
    c. The template expects an `OPENAI_API_KEY` environment variable by default to function. Add OPENAI_API_KEY=_your OpenAI API Key here_ to the `.env` file and save it.
    d. Add any other environment variables your Structure depends on as you expand the template.
7. Rebuild the structure to load in the new environment variable. 
    Note that this is only required for changes to `.env` or `requirements.txt`. Code changes do not require a rebuild. 
    ```bash
    gt skatepark build
    ```
8. Now that your Structure is registered and built with environment variables, use the example program to call the Skatepark emulator's API for running the Structure. Skatepark gives you confidence that when you bring your program into Griptape Cloud as a Managed Structure, it will continue to operate as expected, at scale.

    Navigate to the `example-client` directory.
    ```bash
    cd example-client
    ```

    Install the dependencies required by the example client program.
    ```bash
    poetry install
    ```

    Run the example client program.
    ```bash
    poetry run python client.py
    ```

    You should see the result of the Structure answering `What is 123 * 34, 23 / 12.3, and 9 ^ 4`, indicating a successful run. 


## Documentation

Please refer to [Griptape Docs](https://docs.griptape.ai/)

## Development

```shell
poetry install
poetry run gt
```

## Tests

```shell
poetry run pytest
```

## Contributing

Thank you for considering contributing to Griptape! Before you start, please read the following guidelines.

### Submitting Issues

If you have identified a bug, want to propose a new feature, or have a question, please submit an issue through our public [issue tracker](https://github.com/griptape-ai/griptape-cli/issues). Before submitting a new issue, please check the existing issues to ensure it hasn't been reported or discussed before.

## Versioning

Griptape CLI is in constant development and its APIs and documentation are subject to change. Until we stabilize the API and release version 1.0.0, we will use minor versions (i.e., x.Y.z) to introduce features and breaking features, and patch versions (i.e., x.y.Z) for bug fixes.

## License

Griptape CLI is available under the Apache 2.0 License.
