# Griptape Cloud CLI

[![PyPI Version](https://img.shields.io/pypi/v/griptape-cli.svg)](https://pypi.python.org/pypi/griptape-cli)
[![Tests](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

CLI for the Griptape Framework and Cloud.

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


## Skatepark Emulator
You can use the CLI to spin up a local emulator of the Griptape Cloud Skatepark. This is useful for testing and development.

1. Start by creating a new repository from the [Managed Structure Template](https://github.com/griptape-ai/managed-structure-template).
2. Clone the repository and navigate to the root directory.
    ```bash
    git clone https://github.com/{YOUR_GITHUB_ID}/managed-structure-template
    ```

    ```bash
    cd managed-structure-template
    ```
3. Start the emulator.
   ```bash
   gt server start
   ```
4. In a separate terminal window, register a Structure.
   ```bash
   gt server register --directory . --main-file structure.py
   ```

   The example client program uses the environment variable `GT_STRUCTURE_ID` to determine which Structure to run.
   Set this environment variable to the Structure ID you registered in the previous step.
   ```bash
   export GT_STRUCTURE_ID={STRUCTURE_ID}
   ```

   Or you can register and set the environment variable in one step.
   ```bash
   export GT_STRUCTURE_ID=$(gt server register --directory . --main-file structure.py)
   ```

   > [!IMPORTANT]
   > Structures registered with the emulator are not persisted across restarts. You will need to re-register the Structure each time you restart the emulator.
5. Confirm that the Structure is registered.
   ```bash
   gt server list
   ```
6. Add your OPENAI_API_KEY to the `.env` file.
   ```bash
   echo "OPENAI_API_KEY=sk-XXXXXX-XXXXXX-XXXXXX-XXXXXX" >> .env
   ```
7. Rebuild the structure to load in the new environment variable. 
   Note that this is only required for changes to `.env` or `requirements.txt`. Code changes do not require a rebuild. 
   ```bash
   gt server build --structure-id {STRUCTURE_ID}
   ```
8. Now that your Structure is registered, use the example client program to call the emulator's API for running the Structure.
    ```bash
    poetry run python app.py
    ```


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
