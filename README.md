# Griptape CLI

CLI for the Griptape Framework and Cloud.

## Can I Just Install the CLI?

Sure!

1. Install [pipx](https://github.com/pypa/pipx)
1. Run:
   ```shell
   pipx install git+https://github.com/griptape-ai/griptape-cli.git
   ```

## Development

```shell
poetry install
poetry run gt
```

## Tests

```shell
poetry run pytest
```

## Griptape Cloud

Set environment variables:

```shell
export GRIPTAPE_CLOUD_API_KEY=<api_key>
```

Note: You can create an API Key using the [frontend](https://cloud.griptape.ai/).

To override the Griptape Cloud endpoint used, set the following environment variable:

```shell
export GRIPTAPE_CLOUD_ENDPOINT_URL="https://<endpoint>"
```

Configure the Cloud:

```shell
poetry run gt cloud configure
```

Use the cloud command to make API calls:

```shell
poetry run gt cloud list-organizations
```

Create an App from the template using the app command:

```shell
poetry run gt app new --directory ~/workplace demo_app
```

Test an App locally:

```shell
poetry run gt app run --directory ~/workplace/demo_app --arg "what is griptape?"
```

Create an App on the Cloud:

```shell
poetry run gt cloud create-app --name "Demo App"
```

Create a Deployment for the App on the Cloud using the App ID:

```shell
poetry run gt cloud create-deployment --app-id ee95ba10-9e29-4759-b357-dc513821c5b2 --directory ~/workplace/demo_app
```
