import hashlib
import json
import time
import uuid
from pathlib import Path

import click
import requests

from api_auth import api_command, login, logout


def sign_zephr_request(secret_key, body, path, query, method, timestamp, nonce):
    message = f'{secret_key}{body}{path}{query}{method}{timestamp}{nonce}'
    sha_hash = hashlib.sha256(bytes(message, 'UTF-8'))
    return sha_hash.hexdigest()


def create_zephr_authorization_header(client_id, client_secret, body_string, method, path, query):
    # access_key = "d80dc778-b316-43cf-bb86-2204875f1322"
    access_key = client_id
    # secret_key = "7c2d8fc0-1678-468b-910b-9e75e6be58a9"
    secret_key = client_secret
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid1())
    digest = sign_zephr_request(secret_key, body_string, path,
                                query, method, timestamp, nonce)
    authorization_header_value \
        = f'ZEPHR-HMAC-SHA256 {access_key}:{timestamp}:{nonce}:{digest}'
    return authorization_header_value


def do_get(tenant_id, client_id, client_secret, path, query=""):
    protocol = "https"
    host = f"{tenant_id}.api.zephr.com"
    body_string = ""
    method = "GET"

    authorization_header_value = create_zephr_authorization_header(client_id, client_secret, body_string,
                                                                   method, path, query)

    url = f'{protocol}://{host}{path}?{query}'
    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json'}

    r = requests.get(url, headers=headers)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


def do_post(path, body={}, extra_headers={}):
    protocol = "https"
    tenant_id = "newsuk-dev"
    host = f'{tenant_id}.api.zephr.com'
    body_string = json.dumps(body)
    method = "POST"
    query = ""
    authorization_header_value = create_zephr_authorization_header(body_string, method, path, query)
    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json'}
    headers.update(extra_headers)

    url = f'{protocol}://{host}{path}'
    return requests.post(url, headers=headers, json=body)


def do_put(tenant_id, client_id, client_secret, path, body={}, extra_headers={}):
    protocol = "https"
    host = f'{tenant_id}.api.zephr.com'
    body_string = json.dumps(body)
    method = "PUT"
    query = ""

    authorization_header_value = create_zephr_authorization_header(client_id, client_secret, body_string,
                                                                   method, path, query)

    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json'}
    headers.update(extra_headers)

    url = f'{protocol}://{host}{path}'
    r = requests.put(url, headers=headers, json=body)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


def do_delete(tenant_id, client_id, client_secret, path, query=""):
    protocol = "https"
    host = f"{tenant_id}.api.zephr.com"
    body_string = ""
    method = "DELETE"

    authorization_header_value = create_zephr_authorization_header(client_id, client_secret, body_string,
                                                                   method, path, query)

    url = f'{protocol}://{host}{path}?{query}'
    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json'}

    r = requests.delete(url, headers=headers)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


@click.group()
def cli():
    pass


# # TODO - needs testing - need to validate a request that requires a valid session id
# # TODO - find out why it always returns 200 even if the session has been deleted
# @cli.command()
# @click.argument('admin-session-id')
# def logout(admin_session_id):
#     path = "/v3/admin/logout"
#     body = {}
#     r = do_post(path=path, body=body, extra_headers={"blaize-admin-session": f"{admin_session_id}"})
#     if r.ok:
#         print(json.dumps(r.json()))
#     else:
#         print(r)
#

# TODO - needs some testing - what is it useful for?
# @cli.command()
# @click.argument('email')
# @click.argument('password')
# def get_session(email, password):
#     body = {
#         "identifiers": {
#             "email_address": f"{email}"
#         },
#         "validators": {
#             "password": f"{password}"
#         }
#     }
#     path = "/v3/admin/login"
#     r = do_post(path=path, body=body)
#     if r.ok:
#         print(json.dumps(r.json(), indent=2))
#         # print(json.dumps(dict(r.headers), indent=2))
#         print(f'blaize_admin_session: {r.cookies["blaize_admin_session"]}')
#     else:
#         print(r)

# TODO - needs some testing - what is it useful for?
# @cli.command()
# @click.argument('admin-session-id')
# def get_admin_user(admin_session_id):
#     do_get(f"/v3/admin/sessions/{admin_session_id}")


@cli.command()
@api_command
@click.option('-c', '--cpn')
def list_users(profile, tenant_id, client_id, client_secret, cpn):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    if cpn is None:
        do_get(tenant_id, client_id, client_secret, "/v3/users")
    else:
        do_get(tenant_id, client_id, client_secret, "/v3/users", query=f'foreign_key.CPN={cpn}')


@cli.command()
@api_command
@click.argument('user-id')
def get_user(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/users/{user_id}")


@cli.command()
@api_command
@click.argument('user-id')
def get_user_grants(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/users/{user_id}/grants")


# TODO - doesn't work as documented - always returns 404! raise issue with Zephr
@cli.command()
@api_command
def list_account_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get(tenant_id, client_id, client_secret, f"/v3/accounts/users")


@cli.command(help="Accounts the user is a member of")
@api_command
@click.argument('user-id')
def list_user_accounts(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get(tenant_id, client_id, client_secret, f"/v3/users/{user_id}/accounts")


@cli.command(help='Add a user to a company account')
@api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def add_user_to_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_put(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@cli.command(help='Remove user from company account')
@api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def remove_user_from_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_delete(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@cli.command()
@api_command
def list_schema_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/schema/users")


@cli.command()
@api_command
def list_unclaimed_gifts(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/gift")


@cli.command()
@api_command
def list_request_rules(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/request-rules")


@cli.command()
@api_command
def list_accounts(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/accounts")


@cli.command()
@api_command
@click.argument('account-id')
def get_account(profile, tenant_id, client_id, client_secret, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}")


@cli.command()
@api_command
def list_feature_rules(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/feature-rules")


@cli.command()
@api_command
def list_companies(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/companies")


@cli.command()
@api_command
@click.argument('company-id')
def get_company(profile, tenant_id, client_id, client_secret, company_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@cli.command()
@api_command
@click.argument('company-id')
def delete_company(profile, tenant_id, client_id, client_secret, company_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_delete(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@cli.command()
@api_command
def list_products(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/products")


@cli.command()
@api_command
def list_meters(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/meters")


@cli.command()
@api_command
def list_static(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/static")


@cli.command()
@api_command
def list_webhooks(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/webhooks")


@cli.command()
@api_command
def list_schema_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/schema/users")


@cli.command()
@api_command
def list_cache_configurations(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/cache-configurations")


@cli.command()
@api_command
def get_configuration(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/configuration")


@cli.command()
@api_command
def list_credits(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/credits")


@cli.command()
@api_command
def list_entitlements(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/entitlements")


@cli.command()
@api_command
def list_bundles(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, "/v3/bundles")


@cli.command()
@api_command
@click.argument('bundle-id')
def get_bundle(profile, tenant_id, client_id, client_secret, bundle_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get(tenant_id, client_id, client_secret, f"/v3/bundles/{bundle_id}")


@click.group(help='Manage API credentials')
def auth():
    pass


auth.add_command(login)
auth.add_command(logout)

# Add auth subcommand family to CLI root
cli.add_command(auth)

_app_name = Path(__file__).stem

if __name__ == '__main__':
    cli(obj={'app_name': _app_name})
