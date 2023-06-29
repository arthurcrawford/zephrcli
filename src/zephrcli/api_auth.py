import keyring
import click
import json
import pwinput
from click import BadParameter
from keyring.backends.macOS import Keyring
from keyring.errors import PasswordDeleteError
from .config import app_name

# Options to decorate all commands using keychain credentials
_admin_api_options = [
    click.option('--profile', help="Profile name used for persistent credentials"),
    click.option('--tenant-id', envvar='TENANT_ID', help="Zephr tenant ID"),
    click.option('--client-id', envvar='CLIENT_ID', help="Zephr API client key ID"),
    click.option('--client-secret', envvar='CLIENT_SECRET', help="Zephr API client secret", hide_input=True)
]

# Options to decorate all commands using keychain credentials
_public_api_options = [
    click.option('--profile', help="Name of stored keychain credentials; don't use with options [--tenant-id "
                                   "--client-id --client-secret]"),
    click.option('--tenant-id', envvar='TENANT_ID', help="Zephr tenant ID; don't use with option --profile")
]


# Decorator used to add auth_options to any admin API command
def admin_api_command(func):
    # Hardcode backend to macOS for the moment; otherwise keyring warns of missing config file
    keyring.set_keyring(Keyring())

    for option in reversed(_admin_api_options):
        func = option(func)
    return func


# Decorator used to add profile options for public API commands
def public_api_command(func):
    for option in reversed(_public_api_options):
        func = option(func)
    return func


def get_creds(profile):
    creds_string = keyring.get_password(app_name, profile)
    if creds_string is None:
        raise BadParameter(message=f'"{profile}" not found', param_hint='--profile')
    return json.loads(creds_string)


def get_cred(param_name, profile):
    creds = get_creds(profile)
    if creds is not None:
        return creds[param_name]
    else:
        return None


@click.command(help="Authorise and save credentials to key ring")
@click.option('--profile', required=True, prompt=True, help="Profile name used for persistent credentials")
@click.option('--tenant-id', envvar='TENANT_ID', required=True, prompt=True, help="Zephr tenant ID")
@click.option('--client-id', envvar='CLIENT_ID', required=True, prompt=True, help="Zephr API client key ID")
@click.option('--client-secret', envvar='CLIENT_SECRET', help="Zephr API client secret")
def login(profile, tenant_id, client_id, client_secret):
    # Custom prompt using pwinput for secret to mask with *
    if client_secret is None:
        client_secret = pwinput.pwinput(f'Client secret: ')

    # Save to keyring
    creds = {'tenant_id': tenant_id, 'client_id': client_id, 'client_secret': client_secret}
    print(f'saving credentials for profile: {profile}')
    keyring.set_password(app_name, profile, json.dumps(creds))


@click.command(help="Remove credentials from key ring")
@click.option('--profile', required=True, prompt=True, help="Profile name used for persistent credentials")
def logout(profile):
    try:
        keyring.delete_password(app_name, profile)
        print(f'logged out profile: {profile}')
    except PasswordDeleteError:
        print(f'profile: {profile} already logged out')
