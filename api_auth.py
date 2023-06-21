import keyring
import click
import json
import pwinput
from click import ClickException
from keyring.backends.macOS import Keyring
from keyring.errors import PasswordDeleteError


# Custom click.Option type that prompts for value only if value is None
class KeychainCredentialsOption(click.Option):
    _creds = None

    def __init__(self, *args, **kwargs):
        super(KeychainCredentialsOption, self).__init__(*args, **kwargs)

    # Override normal option parsing to fine tune prompting behaviour
    def handle_parse_result(self, ctx, opts, args):
        # Parse as normal with superclass
        rv = super(KeychainCredentialsOption, self).handle_parse_result(ctx, opts, args)

        # If the option value is still None after normal parsing
        value = rv[0]
        profile = ctx.params['profile']
        if value is None:
            # Look for the value in the keychain
            value = self.get_cred(self.name, profile, get_app_name(ctx))
        if value is None:
            if self.hide_input:
                # Mask the input if it's a secret
                value = pwinput.pwinput(f'{self.name}: ')
            else:
                value = click.prompt(f'{self.name}: ')
        # Push value into the context
        ctx.params[self.name] = value
        # Follow superclass convention for return value
        return value, args

    def get_creds(self, profile, app_name):
        # global _creds
        if self._creds is None:
            creds_string = keyring.get_password(app_name, profile)
            if creds_string is not None:
                self._creds = json.loads(creds_string)
        return self._creds

    def get_cred(self, param_name, profile, app_name):
        creds = self.get_creds(profile, app_name)
        if creds is not None:
            return creds[param_name]
        else:
            return None


# Options to decorate all commands using keychain credentials
_admin_api_options = [
    click.option('--profile', help="Profile name used for persistent credentials"),
    click.option('--tenant-id', envvar='TENANT_ID', help="Zephr tenant ID", cls=KeychainCredentialsOption),
    click.option('--client-id', envvar='CLIENT_ID', help="Zephr API client key ID", cls=KeychainCredentialsOption),
    click.option('--client-secret', envvar='CLIENT_SECRET', help="Zephr API client secret",
                 cls=KeychainCredentialsOption, hide_input=True),
]

# Options to decorate all commands using keychain credentials
_public_api_options = [
    click.option('--profile', help="Profile name used for persistent credentials"),
    click.option('--tenant-id', envvar='TENANT_ID', help="Zephr tenant ID", cls=KeychainCredentialsOption),
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


def get_app_name(ctx):
    if ctx.obj is None or 'app_name' not in ctx.obj:
        err_msg = """
  api_auth.py - incorrect usage: 'app_name' is missing from the Click context
  this is required for identifying key chain items          
  initialise this key with a value in the Click context object as follows:

    cli(obj={"app_name": <app_name>}
        """
        raise ClickException(err_msg)

    return ctx.obj['app_name']


@click.command(help="Authorise and save credentials to key ring")
@click.option('--profile', help="Profile name used for persistent credentials")
@click.option('--tenant-id', envvar='TENANT_ID', help="Zephr tenant ID", required=True, prompt=True)
@click.option('--client-id', envvar='CLIENT_ID', help="Zephr API client key ID", required=True, prompt=True)
@click.option('--client-secret', envvar='CLIENT_SECRET', help="Zephr API client secret")
@click.pass_context
def login(ctx, profile, tenant_id, client_id, client_secret):
    # Custom prompt using pwinput for secret to mask with *
    if client_secret is None:
        client_secret = pwinput.pwinput(f'client_secret: ')

    # Save to keyring
    creds = {'tenant_id': tenant_id, 'client_id': client_id, 'client_secret': client_secret}
    print(f'saving credentials for profile: {profile}')
    keyring.set_password(get_app_name(ctx), profile, json.dumps(creds))


@click.command(help="Remove credentials from key ring")
@click.option('--profile', help="Profile name used for persistent credentials", required=True)
@click.pass_context
def logout(ctx, profile):
    try:
        keyring.delete_password(get_app_name(ctx), profile)
        print(f'logged out profile: {profile}')
    except PasswordDeleteError:
        print(f'profile: {profile} already logged out')
