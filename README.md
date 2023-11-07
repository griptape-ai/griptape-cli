# Griptape CLI

CLI for the Griptape Framework and Cloud.

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

Note: You can create an API Key using the [frontend](https://cloud-staging.griptape.ai/).

Configure the Cloud:

```shell
poetry run gt cloud configure
```

Note: Copy and paste the full 'name: ID' string in the terminal to select

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
