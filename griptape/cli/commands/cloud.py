import os
from typing import Optional
import click
from click import echo
from griptape.cli.core.app_packager import AppPackager
from griptape.cli.core.cloud_client import CloudClient
from griptape.cli.core.utils.constants import DEFAULT_ENDPOINT_URL
from InquirerPy import inquirer


@click.group()
@click.pass_context
def cloud(ctx):
    pass


@cloud.command(name="configure")
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
def configure(endpoint_url: str) -> None:
    try:
        counter = 0
        cloud_client = CloudClient(endpoint_url=endpoint_url)
        organizations = cloud_client.list_organizations().json()["organizations"]

        org_choices = [
            f"{counter+1}). {org['name']}: {org['organization_id']}"
            for org in organizations
        ]
        org_choice = inquirer.select(
            message="Select the organization you want to use:",
            choices=org_choices,
        ).execute()

        org = organizations[org_choices.index(org_choice)]

        environments = cloud_client.list_environments(
            organization_id=org["organization_id"]
        ).json()["environments"]

        counter = 0
        environment_choices = [
            f"{counter+1}). {env['name']}: {env['environment_id']}"
            for env in environments
        ]

        env_choice = inquirer.select(
            message="Select the environment you want to use:",
            choices=environment_choices,
        ).execute()

        env = environments[environment_choices.index(env_choice)]

        profile_name = click.prompt(
            "Enter a name for this profile",
            type=str,
            show_default=True,
            default="default",
        )

        cloud_client._write_gt_cloud_profile(
            profile_name=profile_name,
            organization_id=org["organization_id"],
            environment_id=env["environment_id"],
        )

        echo(f"Successfully configured profile {profile_name}!")

    except Exception as e:
        echo(f"{e}")


@cloud.command(name="list-organizations")
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
def list_organizations(endpoint_url: str):
    """
    List Griptape Cloud Organizations.
    """

    cloud_client = CloudClient(endpoint_url=endpoint_url)
    response = cloud_client.list_organizations()
    echo(response.json())


@cloud.command(name="list-environments")
@click.option(
    "--organization-id",
    "-o",
    type=str,
    required=True,
    help="Organization ID to list environments for",
)
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
def list_environments(organization_id: str, endpoint_url: str):
    """
    List Griptape Cloud Environments.
    """

    cloud_client = CloudClient(endpoint_url=endpoint_url)
    response = cloud_client.list_environments(organization_id=organization_id)
    echo(response.json())


@cloud.command(name="list-apps")
@click.option(
    "--environment-id",
    "-n",
    type=str,
    required=True,
    help="Environment ID to list apps for",
)
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
def list_apps(environment_id: str, endpoint_url: str):
    """
    List Griptape Cloud Apps.
    """

    cloud_client = CloudClient(endpoint_url=endpoint_url)
    response = cloud_client.list_apps(environment_id=environment_id)
    echo(response.json())


@cloud.command(name="create-app")
@click.option(
    "--name",
    "-n",
    type=str,
    help="Griptape Cloud app name",
    required=True,
)
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
@click.option(
    "--environment-id",
    "-v",
    type=str,
    help="Griptape Cloud environment id",
    default=None,
    required=False,
)
@click.option(
    "--profile",
    "-p",
    type=str,
    help="Griptape Cloud profile name",
    default=None,
    required=False,
)
def create_app(
    name: str, endpoint_url: str, environment_id: Optional[str], profile: Optional[str]
) -> None:
    """
    Create a Griptape App on the Griptape Cloud.
    """
    app_data = {
        "name": name,
    }
    cloud_client = CloudClient(endpoint_url=endpoint_url, profile=profile)
    response = cloud_client.create_app(app_data=app_data, environment_id=environment_id)
    echo(response.json())


@cloud.command(name="create-deployment")
@click.option(
    "--app-id",
    "-a",
    type=str,
    help="Griptape Cloud app id",
    required=True,
)
@click.option(
    "--directory",
    "-d",
    type=str,
    help="Directory where app resides. Defaults to current directory.",
    default=os.getcwd(),
    show_default=True,
)
@click.option(
    "--endpoint-url",
    "-e",
    type=str,
    required=False,
    help="Override default endpoint url",
    default=DEFAULT_ENDPOINT_URL,
)
def create_deployment(app_id: str, directory: str, endpoint_url: str) -> None:
    """
    Deploy a Griptape App to Griptape Cloud.
    """

    cloud_client = CloudClient(endpoint_url=endpoint_url)

    app_packager = AppPackager(
        app_directory=directory,
    )
    source = app_packager.get_deployment_source()

    deployment_data = {"source": {"zip_file": {"base64_content": source}}}

    try:
        response = cloud_client.create_deployment(
            deployment_data=deployment_data, app_id=app_id
        )
        if response.status_code != 202:
            raise Exception(response.json())
        echo(response.json())
    except Exception as e:
        echo(f"Unable to create deployment: {e}", err=True)
        raise e
