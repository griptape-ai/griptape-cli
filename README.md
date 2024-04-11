# griptape-cli

[![PyPI Version](https://img.shields.io/pypi/v/griptape-cli.svg)](https://pypi.python.org/pypi/griptape-cli)
[![Tests](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/griptape-ai/griptape-cli/actions/workflows/tests.yml)
[![Docs](https://readthedocs.org/projects/griptape/badge/)](https://griptape.readthedocs.io/)
[![Griptape Discord](https://dcbadge.vercel.app/api/server/gnWRz88eym?compact=true&style=flat)](https://discord.gg/gnWRz88eym)

CLI for the Griptape Framework and Cloud.

## Prerequisites

CLI `cloud` commands require a [Griptape Cloud](https://www.griptape.ai/griptape-cloud/) account.

## Quick Start

1. Install griptape-cli
   ```
   pipx install griptape-cli
   ```
1. Verify installation
   ```
   gt --help
   ```

## Griptape Cloud

### Skatepark Emulator
You can use the CLI to spin up a local emulator of the Griptape Cloud Skatepark. This is useful for testing and development.

1. Start the emulator
```
gt cloud server start
```

2. Register a structure
```
gt cloud server register
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
