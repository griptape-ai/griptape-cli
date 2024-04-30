# Griptape Cloud CLI

[![PyPI Version](https://img.shields.io/pypi/v/griptape-cli.svg)](https://pypi.python.org/pypi/griptape-cli)
[![Tests](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

The Griptape CLI is a command-line interface for interacting with features of [Griptape Cloud](https://www.griptape.ai/cloud).
Today, it provides an emulator for Griptape Cloud Managed Structures, which allows you to run and test your Managed Structures locally. 

## Prerequisites
- A GitHub account.
- Python 3.11.
- [Poetry](https://python-poetry.org) for running the example client program.

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
    pipx install ./griptape-cli --force
    ```
2. Verify installation
    ```bash
    gt --help
    ```

## Skatepark Emulator
You can use the CLI to spin up Skatepark, a local emulator for Griptape Cloud Managed Structures. It exposes an API that is identical to the one you would interact with when running your Managed Structure in Griptape Cloud.
Use Skatepark to develop, test, and validate that your program will operate as expected when deployed as a Griptape Cloud Managed Structure. Skatepark gives you confidence that when you bring your Structure into Griptape Cloud as a Managed Structure, it will continue to operate as expected, at scale.

1. Start by creating a new repository in your own Github account from the [Managed Structure Template](https://github.com/griptape-ai/managed-structure-template).
    1. Make sure you're logged in to GitHub.
    2. Go to the [Managed Structure Template repo](https://github.com/griptape-ai/managed-structure-template).
    3. Select the *Use this template* drop-down.
    4. Choose *Create a new repository*.
    5. Provide a name for the new repository and (optionally) a description.
    6. Press the *Create repository* button.
    7. You now have a repository in your own GitHub account that is a copy of the Managed Structure Template for you to begin working with.
2. Clone your newly-created repository to a directory in your local development environment so that you can begin authoring your own Griptape Cloud Managed Structure.
3. Start Skatepark.
    ```bash
    gt skatepark start
    ```
4. Open a new terminal window. Navigate to the directory with the locally-cloned repository.
5. Register a Structure with Skatepark.
    ```bash
    gt skatepark register --main-file structure.py
    ```
    This will result in the ID of the registered Structure. It is important to make note of this ID as it will be used to distinguish which Structure you want to run. You can register any number of Structures.

    The example client program uses the environment variable `GT_STRUCTURE_ID` to determine which Structure to run.
    Set this environment variable to the Structure ID you registered in the previous step.
    ```bash
    export GT_STRUCTURE_ID={STRUCTURE_ID}
    ```

    Or you can register and set the environment variable in one step.
    ```bash
    export GT_STRUCTURE_ID=$(gt skatepark register --main-file structure.py --tldr)
    ```

> [!IMPORTANT]
> Structures registered with the Skatepark are not persisted across restarts. You will need to re-register the Structure each time you restart Skatepark.
5. Confirm that the Structure is registered.
    ```bash
    gt skatepark list
    ```
    You should see a list of registered Structures and the directories they point to, confirming that your Structure was properly registered
6. You can load environment variables into your Structure by creating an `.env` file in the directory of the Structure you registered. 
    1. Create a file named `.env` in the `structure/` directory.
    2. Open the `.env` file in a text editor.
    3. The template expects an `OPENAI_API_KEY` environment variable by default to function. Add OPENAI_API_KEY=_your OpenAI API Key here_ to the `.env` file and save it.
    4. As you expand on the template, you may add any other environment variables your Structure depends on to this file.
7. Rebuild the structure to load in the new environment variable. 
    Note that this is only required for changes to `.env` or `requirements.txt`. Code changes do not require a rebuild. 
    ```bash
    gt skatepark build
    ```
8. Now that your Structure is registered and built with environment variables, use the example client program to call Skatepark's API for running the Structure.

    Navigate to the `example-client` directory.
    ```bash
    cd example-client
    ```

    Install the dependencies required by the example client program.
    ```bash
    poetry install --no-root
    ```

    Run the example client program.
    ```bash
    poetry run python client.py
    ```

    You should see the result of the Structure answering `What is 123 * 34, 23 / 12.3, and 9 ^ 4`, indicating a successful run. 

> [!IMPORTANT]
> The client program is an _example_ for how to interact with the Managed Structure's API. It is useful for testing your Managed Structure locally, but ultimately you will want to integrate your Managed Structure with your own application. 


# Simulating Structure Run Delay
By default, Skatepark adds a 2 second delay before transitioniong Structure Runs from the `QUEUED` state to the `RUNNING` state.
If you want to change this delay in order to test the behavior of your Structure when it is in the `QUEUED` state, you can do so by setting the `GT_SKATEPARK_QUEUE_DELAY` environment variable.
For example, a value of `GT_SKATEPARK_QUEUE_DELAY=5` will cause Skatepark to wait 5 seconds before transitioning the Structure Run from `QUEUED` to `RUNNING`. Setting a value of `GT_SKATEPARK_QUEUE_DELAY=0` will cause Skatepark to transition the Structure Run immediately.

Note that this environment variable must be set in the terminal where the Skatepark server is running, not in the terminal where the client program is run.

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
