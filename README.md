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

1. Start by creating a new directory and navigating to it.
```
mkdir skatepark-local 
cd skatepark-local
```

2. Create a `structure.py` file with with the following sample code.
```python
import os
import sys

from griptape.config import StructureConfig, StructureGlobalDriversConfig
from griptape.drivers import (
    GriptapeCloudEventListenerDriver,
    OpenAiChatPromptDriver,
)
from griptape.events import (
    EventListener,
)
from griptape.structures import Agent
from griptape.tools import Calculator

structure = Agent(
    tools=[Calculator(off_prompt=False)],
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=OpenAiChatPromptDriver(
                model="gpt-4",
                stream=True,
            ),
        )
    ),
    event_listeners=[
        EventListener(
            driver=GriptapeCloudEventListenerDriver(
                base_url="http://127.0.0.1:5000",
                api_key=os.environ["GRIPTAPE_CLOUD_API_KEY"],
            ),
        )
    ],
)

structure.run(sys.argv[1]) # Structure Run arguments are passed in via standard input. 
```

And a `requirements.txt` file with the following content.
```
griptape
```

3. Start the emulator.
```
gt cloud server start
```

By default, the emulator runs on `127.0.0.1` and port `5000`. You can change these values by providing the `--host` and `--port` options.
```
gt cloud server start --host localhost --port 5001
```
We'll continue with the default values for the rest of this guide.

4. In a separate terminal window, register a Structure.
```
gt cloud server register --directory skatepark-local --main-file structure.py
```

5. Run your Structure from a separate program. Here is an example using the `requests` library.
```python
import requests
import time

host = "http://127.0.0.1:5000"

# Start a run with the args "What is 5 ^ 2".
# These args will be passed into our Structure program as standard input.
response = requests.post(f"{host}/api/structures/active/runs", json={"env": {}, "args": ["What is 5 ^ 2"]})
response.raise_for_status()

# Runs are asynchronous, so we need to poll the status until it's no longer running.
run_id = response.json()["run_id"]
status = response.json()["status"]
while status == "RUNNING":
    response = requests.get(f"{host}/api/runs/{run_id}")
    response.raise_for_status()
    status = response.json()["status"]
    
    time.sleep(1) # Poll every second.

output = response.json()["output"]
print(output["value"])
```

And our output should be:
```
The result of 5 raised to the power of 2 is 25.
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
