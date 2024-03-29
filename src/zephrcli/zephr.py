import hashlib
import json
import time
import uuid
import click
import pwinput
import requests
import importlib.resources

from click import UsageError

from .api_auth import admin_api_command, public_api_command, login, logout, get_cred, get_creds

# Load VERSION as a resource because we may not have access to file system
version = importlib.resources.read_text(__package__, "VERSION")


def sign_zephr_request(secret_key, body, path, query, method, timestamp, nonce):
    message = f'{secret_key}{body}{path}{query}{method}{timestamp}{nonce}'
    sha_hash = hashlib.sha256(bytes(message, 'UTF-8'))
    return sha_hash.hexdigest()


def create_zephr_authorization_header(client_id, client_secret, body_string, method, path, query):
    access_key = client_id
    secret_key = client_secret
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid1())
    digest = sign_zephr_request(secret_key, body_string, path,
                                query, method, timestamp, nonce)
    authorization_header_value \
        = f'ZEPHR-HMAC-SHA256 {access_key}:{timestamp}:{nonce}:{digest}'
    return authorization_header_value


def do_get_admin(tenant_id, client_id, client_secret, path, query=""):
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


def do_get_public(path, tenant_id, site_name, query="", cookies=None):
    if cookies is None:
        cookies = {}
    protocol = "https"
    stage = "cdn"
    host = f'{tenant_id}-{site_name}.{stage}.zephr.com'
    headers = ""

    url = f'{protocol}://{host}{path}?{query}'

    r = requests.get(url, headers=headers, cookies=cookies)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


def do_post_admin(path, body, cookies, tenant_id, client_id, client_secret):
    protocol = "https"
    host = f'{tenant_id}.api.zephr.com'
    body_string = json.dumps(body)
    method = "POST"
    query = ""
    authorization_header_value = create_zephr_authorization_header(client_id, client_secret, body_string,
                                                                   method, path, query)
    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json', 'Accept': 'application/json'}

    url = f'{protocol}://{host}{path}'

    r = requests.post(url, headers=headers, json=body, cookies=cookies)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


def do_post_public(path, body, cookies, tenant_id, site_name, extra_headers=None):
    if extra_headers is None:
        extra_headers = {}
    protocol = "https"
    stage = "cdn"
    host = f'{tenant_id}-{site_name}.{stage}.zephr.com'
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    headers.update(extra_headers)

    url = f'{protocol}://{host}{path}'

    r = requests.post(url, headers=headers, json=body, cookies=cookies)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


def do_put(tenant_id, client_id, client_secret, path, body=None, extra_headers=None):
    if extra_headers is None:
        extra_headers = {}
    if body is None:
        body = {}
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


def do_delete_admin(tenant_id, client_id, client_secret, path, query=""):
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


def do_delete_public(path, tenant_id, site_name, cookies=None):
    if cookies is None:
        cookies = {}
    protocol = "https"
    stage = "cdn"
    host = f'{tenant_id}-{site_name}.{stage}.zephr.com'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    url = f'{protocol}://{host}{path}'

    r = requests.delete(url, headers=headers, cookies=cookies)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


@click.group()
@click.version_option(version=version)
def cli():
    pass


# # TODO - needs testing - need to validate a request that requires a valid session id
# # TODO - find out why it always returns 200 even if the session has been deleted
# @click.command()
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
# @click.command()
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
# @click.command()
# @click.argument('admin-session-id')
# def get_admin_user(admin_session_id):
#     do_get(f"/v3/admin/sessions/{admin_session_id}")

@click.command(help='Create a user')
@admin_api_command
@click.option('-e', '--email', required=True, help='Email address of the user, used as identifier')
@click.option('-f', '--first-name', help='First name of the user')
@click.option('-l', '--last-name', help='Last name of the user')
@click.option('-k', '--foreign-key', nargs=2, help='Foreign key to external user system e.g. "-k myfk 1234"')
def create_user(profile, tenant_id, client_id, client_secret, email, first_name, last_name, foreign_key):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)

    body = {
        'identifiers': {
            'email_address': email
        },
        'attributes': {}
    }
    cookies = {}

    if first_name is not None:
        # Zephr documentation incorrectly shows attribute name as 'first_name'
        body['attributes'].update({'firstname': first_name})
    if last_name is not None:
        # Zephr documentation incorrectly shows attribute name as 'surname'
        body['attributes'].update({'lastname': last_name})

    if foreign_key is not None:
        key, value = foreign_key
        body['foreign_keys'] = {key: value}

    do_post_admin("/v3/users", body, cookies, tenant_id, client_id, client_secret)


def parse_credential_options(profile, tenant_id, client_id, client_secret):
    # Prefer to use the profile option if specified
    if profile is not None:
        # If any credential options also specified - incorrect usage and exit
        if tenant_id is not None or client_id is not None or client_secret is not None:
            raise UsageError(
                'Please use either --profile, or [--tenant-id, --client-id, --client-secret], but not both')
        # Get credential from profile
        creds = get_creds(profile)
        return creds['tenant_id'], creds['client_id'], creds['client_secret']
    else:
        if tenant_id is None:
            tenant_id = click.prompt('Tenant ID')
        if client_id is None:
            client_id = click.prompt('Client ID')
        if client_secret is None:
            client_secret = pwinput.pwinput('Client secret: ')

    click.echo(click.style(f'Using Zephr tenant: {tenant_id}', fg='green'), err=True)
    return tenant_id, client_id, client_secret


@click.command(help='List users, or select by foreign key query')
@admin_api_command
@click.option('-k', '--foreign-key', nargs=2, help='Query by foreign key e.g. "-f my_fk 1234"')
@click.option('-r', '--results-per-page', help='Number of results per page response', default=50)
@click.option('-p', '--page', help='Number of page', default=1)
@click.option('-s', '--search', help='Search term')
def list_users(profile, tenant_id, client_id, client_secret, foreign_key, results_per_page, page, search):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)

    query = f'rpp={results_per_page}&page={page}'

    if search is not None:
        query += f'&search=*{search}*'

    # query = 'rpp=2'
    if foreign_key is not None:
        key, value = foreign_key
        query = f'foreign_key.{key}={value}'

    do_get_admin(tenant_id, client_id, client_secret, '/v3/users',
                 query=query)


def debug(profile):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)


@click.command()
@admin_api_command
@click.argument('user-id')
def get_user(profile, tenant_id, client_id, client_secret, user_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}")


@click.command()
@admin_api_command
@click.option('-j', '--jwt')
@click.option('-z', '--session-id', help='ID of the requesting session')
@click.argument('email')
def create_session(profile, tenant_id, client_id, client_secret, jwt, email):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    body = {
        "identifiers": {
            "email_address": f"{email}"
        }
    }
    cookies = {}

    if jwt is not None:
        # body['jwt'] = jwt
        # Also add to cookies as not certain that jwt in the body works correctly
        cookies = {'blaize_jwt': jwt}

    do_post_admin("/v3/sessions", body, cookies, tenant_id, client_id, client_secret)


@click.command(help="List sessions for the given user")
@admin_api_command
# @click.option('-j', '--jwt')
# @click.option('-z', '--session-id', help='ID of the requesting session')
@click.option('-u', '--user-id', required=True, help='Unique ID of the user')
def list_user_sessions(profile, tenant_id, client_id, client_secret, user_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)

    # https://{tenantId}.api.zephr.com/v3/users/{user_id}/sessions
    do_get_admin(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret,
                 path=f'/v4/users/{user_id}/sessions')


@click.command()
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
def get_user_grants(profile, tenant_id, client_id, client_secret, user_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f'/v3/users/{user_id}/grants')


@click.command(help='Get a user grant')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-g', '--grant-id', required=True, help='The ID of the grant')
def get_user_grant(profile, tenant_id, client_id, client_secret, user_id, grant_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f'/v3/users/{user_id}/grants/{grant_id}')


@click.command(help="Grant a product to a user")
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-p', '--product-id', required=True, help='The ID of the product')
# If it's a product share, not sure we need entitlement_id - i.e. we could get the product to get its bundle entitlement ID instead
@click.option('-e', '--entitlement-id', required=True, help='The ID of the associated bundle entitlement')
@click.option('-b', '--start-time', help='When grant will begin - e.g. 2023-12-31 23:59:59 - default=now')
@click.option('-f', '--end-time', help='When grant will finish e.g. 2024-12-31 23:59:59 - default=indefinite')
def create_user_grant(profile, tenant_id, client_id, client_secret, user_id, product_id, entitlement_id,
                      start_time, end_time):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    body = {
        "entitlement_type": "bundle",
        "entitlement_id": f"{entitlement_id}",
        "product_id": f"{product_id}"
    }
    if start_time is not None:
        body['startTime'] = start_time

    if end_time is not None:
        body['endTime'] = end_time

    cookies = {}

    do_post_admin(f'/v3/users/{user_id}/grants', body, cookies, tenant_id, client_id, client_secret)


@click.command(help='Delete a user grant')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-g', '--grant-id', required=True, help='The ID of the grant')
def delete_user_grant(profile, tenant_id, client_id, client_secret, user_id, grant_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_delete_admin(tenant_id, client_id, client_secret, f'/v3/users/{user_id}/grants/{grant_id}')


# TODO - doesn't work as documented - always returns 404! raise issue with Zephr
@click.command()
@admin_api_command
def list_account_users(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/accounts/users")


@click.command(help="Accounts the user is a member of")
@admin_api_command
@click.argument('user-id')
def list_user_accounts(profile, tenant_id, client_id, client_secret, user_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}/accounts")


@click.command(help='Add a user to a company account')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def add_user_to_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_put(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@click.command(help='Remove user from company account')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def remove_user_from_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@click.command(help='Delete a user')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
def delete_user(profile, tenant_id, client_id, client_secret, user_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}")


@click.command()
@admin_api_command
def list_schema_users(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/schema/users")


@click.command()
@admin_api_command
def list_unclaimed_gifts(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/gift")


@click.command()
@admin_api_command
def list_request_rules(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/request-rules")


@click.command()
@admin_api_command
def list_accounts(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/accounts")


@click.command()
@admin_api_command
@click.argument('account-id')
def get_account(profile, tenant_id, client_id, client_secret, account_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}")


@click.command()
@admin_api_command
def list_feature_rules(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/feature-rules")


@click.command()
@admin_api_command
def list_companies(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/companies")


@click.command()
@admin_api_command
@click.argument('company-id')
def get_company(profile, tenant_id, client_id, client_secret, company_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@click.command()
@admin_api_command
@click.argument('company-id')
def delete_company(profile, tenant_id, client_id, client_secret, company_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@click.command()
@admin_api_command
def list_products(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/products")


@click.command()
@admin_api_command
def list_meters(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/meters")


@click.command()
@admin_api_command
def list_static(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/static")


@click.command()
@admin_api_command
def list_webhooks(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/webhooks")


@click.command()
@admin_api_command
def list_cache_configurations(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/cache-configurations")


@click.command()
@admin_api_command
def get_configuration(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/configuration")


@click.command()
@admin_api_command
def list_credits(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/credits")


@click.command()
@admin_api_command
def list_entitlements(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/entitlements")


@click.command(help="Create a bundle (for attachment to a Product)")
@admin_api_command
@click.option('-l', '--label', required=True, help='The label of the bundle')
@click.option('-d', '--description', required=False, help='The description of the bundle', default="Same as label")
def create_bundle(profile, tenant_id, client_id, client_secret, label, description=None):
    if description is None:
        description = label
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    body = {
        "label": f"{label}",
        "description": f"{description}",
        "includes": {
            "entitlements": [],
            "meters": [],
            "credits": [],
            "bundles": []
        },
        "auto_assign": "none"
    }

    cookies = {}

    do_post_admin(f'/v3/bundles', body, cookies, tenant_id, client_id, client_secret)


@click.command(help="List all bundles")
@admin_api_command
def list_bundles(profile, tenant_id, client_id, client_secret):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/bundles")


@click.command(help="Get the specified bundle")
@admin_api_command
@click.argument('bundle-id')
def get_bundle(profile, tenant_id, client_id, client_secret, bundle_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/bundles/{bundle_id}")


@click.command(help="Update a bundle")
@admin_api_command
@click.option('-l', '--label', required=True, help='The label of the bundle')
@click.option('-d', '--description', required=True, help='The description of the bundle')
@click.argument('bundle-id')
def update_bundle(profile, tenant_id, client_id, client_secret, label, description, bundle_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    body = {
        "label": f"{label}",
        "description": f"{description}",
        "includes": {
            "entitlements": [],
            "meters": [],
            "credits": [],
            "bundles": []
        },
        "auto_assign": "none"
    }

    do_put(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret, path=f'/v3/bundles/{bundle_id}',
           body=body)


@click.command(help="Delete the specified bundle")
@admin_api_command
@click.argument('bundle-id')
def delete_bundle(profile, tenant_id, client_id, client_secret, bundle_id):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/bundles/{bundle_id}")


def parse_single_credential_option(profile=None, tenant_id=None):
    # Prefer to use the profile option if specified
    if profile is not None:
        # If tenant_id also specified - incorrect usage and exit
        if tenant_id is not None:
            raise UsageError('Please use either --profile, or --tenant-id, but not both')
        # Get credential from profile
        tenant_id = get_cred('tenant_id', profile)
    else:
        if tenant_id is None:
            # Prompt for tenant_id
            tenant_id = click.prompt('Tenant ID')
    click.echo(click.style(f'Using Zephr tenant: {tenant_id}', fg='green'), err=True)
    return tenant_id


@click.command(help='List rules (aka Features)')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-r', '--rule-type', required=True,
              type=click.Choice(['html', 'json', 'sdk', 'browser'], case_sensitive=False))
def list_rules(profile, tenant_id, site_name, rule_type):
    tenant_id = parse_single_credential_option(profile, tenant_id)
    query = f'ruleType={rule_type}' if rule_type else ''
    do_get_public("/zephr/features", tenant_id, site_name, query)


@click.command(help='List sessions for the authenticated user')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt', required=True, help='JWT bearing foreign key user ID')
@click.option('-z', '--session-id', help='ID of the requesting session')
def list_sessions(profile, tenant_id, site_name, jwt, session_id):
    tenant_id = parse_single_credential_option(profile=profile, tenant_id=tenant_id)
    cookies = {}
    if jwt is not None:
        cookies['blaize_jwt'] = jwt
    if session_id is not None:
        cookies['blaize_session'] = session_id
    do_get_public(path="/zephr/public/sessions/v1/sessions", tenant_id=tenant_id,
                  site_name=site_name, cookies=cookies)


@click.command(help='Delete session for the authenticated user')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt', required=True, help='JWT bearing foreign key user ID')
@click.option('-z', '--session-id', required=True, help='ID of the requesting session')
def delete_session(profile, tenant_id, site_name, jwt, session_id):
    tenant_id = parse_single_credential_option(profile=profile, tenant_id=tenant_id)
    cookies = {}
    if jwt is not None:
        cookies['blaize_jwt'] = jwt
    if session_id is not None:
        cookies['blaize_session'] = session_id
    do_delete_public(path=f"/zephr/public/sessions/v1/sessions/{session_id}",
                     tenant_id=tenant_id, site_name=site_name, cookies=cookies)


@click.command(help='Delete all other sessions except this one')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt', required=True, help='JWT bearing foreign key user ID')
@click.option('-z', '--session-id', required=True, help='ID of the requesting session')
def delete_other_sessions(profile, tenant_id, site_name, jwt, session_id):
    tenant_id = parse_single_credential_option(profile=profile, tenant_id=tenant_id)
    cookies = {'blaize_jwt': jwt,
               'blaize_session': session_id}
    do_delete_public(path=f"/zephr/public/sessions/v1/sessions?except-current",
                     tenant_id=tenant_id, site_name=site_name, cookies=cookies)


def do_admin_graphql(body, cookies, client_id, client_secret):
    path = '/v4/admin/graphql/'
    body_string = json.dumps(body)
    method = "POST"
    query = ""
    authorization_header_value = create_zephr_authorization_header(client_id, client_secret, body_string,
                                                                   method, path, query)
    headers = {'Authorization': authorization_header_value,
               'Content-Type': 'application/json', 'Accept': 'application/json'}

    url = f'https://console.zephr.com{path}'

    r = requests.post(url, headers=headers, json=body, cookies=cookies)
    if r.ok:
        print(json.dumps(r.json(), indent=2))
    else:
        print(r)


# This operation was not available through the documented API, so we use the admin console graphql.
# This may not be supported in the future, so this approach will need to be reviewed
@click.command()
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-l', '--session-limit', required=True, help='User concurrent session limit')
def set_user_session_limit(profile, tenant_id, client_id, client_secret, user_id, session_limit):
    tenant_id, client_id, client_secret = parse_credential_options(profile, tenant_id, client_id, client_secret)

    body = {
        "operationName": "updateUserConcurrentSessionLimit",
        "variables": {
            "userId": user_id,
            "limit": session_limit
        },
        "query": "mutation updateUserConcurrentSessionLimit($userId: ID!, $limit: Int) {"
                 "    updateUserConcurrentSessionLimit(userId: $userId, limit: $limit) {"
                 "      status"
                 "      message"
                 "      __typename"
                 "    }"
                 "}"
    }

    do_admin_graphql(body=body, cookies={}, client_id=client_id, client_secret=client_secret)


@click.command(help='Invoke rule(s) and get decisions')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt', help='Specify userID/product claims in a signed JWT')
@click.option('-k', '--foreign-key', nargs=2, help='Specify user by foreign key e.g. "-k my_fk 1234"')
@click.option('-i', '--ip', help='Specify IP address of caller: default = actual IP')
@click.option('-u', '--user-agent', help='Specify the User-Agent header')
@click.option('-z', '--session-id', help='ID of the requesting session')
@click.argument('features', nargs=-1, required=True)
def decide(profile, tenant_id, site_name, jwt, foreign_key, ip, user_agent, session_id, features):
    tenant_id = parse_single_credential_option(profile=profile, tenant_id=tenant_id)
    body = {'features': []}
    cookies = {}
    headers = {}
    for f_id in features:
        body['features'].append({'slug': f_id})

    if ip is not None:
        body['ip'] = ip

    if session_id is not None:
        body['session'] = session_id

    if jwt is not None:
        body['jwt'] = jwt
        # Also add to cookies as not certain that jwt in the body works correctly
        cookies = {'blaize_jwt': jwt}

    if user_agent is not None:
        # Some versions of Zephr documentation say you should do this which doesn't work
        # body['UserAgent'] = user_agent
        # This doesn't seem to work either
        # headers.update({'User-Agent': user_agent})
        # Only this, un-documented method seems to work
        body['user_agent'] = user_agent

    # N.B. If you specify a foreign key, no user session is created for this user.
    # An anonymous session is created - this overrides the JWT
    # JWT + session id is required to consume a user session.
    if foreign_key is not None:
        key, value = foreign_key
        body['foreign_keys'] = {key: value}

    do_post_public(path='/zephr/decide', body=body,
                   cookies=cookies, tenant_id=tenant_id, site_name=site_name,
                   extra_headers=headers)


@click.command(help='Register a new user')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-e', '--email', required=True, help='Email of the user to register')
@click.option('-k', '--foreign-key', nargs=2, help='Foreign key to your user platform e.g. "-k my_fk 1234"')
def register_user(profile, tenant_id, site_name, email, foreign_key):
    tenant_id = parse_single_credential_option(profile, tenant_id)
    body = {'identifiers': {'email_address': email}}
    cookies = {}

    if foreign_key is not None:
        key, value = foreign_key
        body['foreign_keys'] = {key: value}

    do_post_public('/blaize/register', body, cookies, tenant_id, site_name)


@click.group(help='Admin commands that require API keys')
def admin():
    pass


@click.group(help='Public commands')
def public():
    pass


# Add admin API subcommands to the admin group
admin_commands = [
    login, logout, list_products, list_users, create_user, list_user_sessions, set_user_session_limit, get_user,
    create_session, get_user_grants, get_user_grant, create_user_grant, delete_user_grant, list_account_users,
    list_user_accounts, add_user_to_account, remove_user_from_account, delete_user, list_schema_users,
    list_unclaimed_gifts, list_request_rules, list_accounts, get_account, list_feature_rules, list_companies,
    get_company, delete_company, list_meters, list_static, list_webhooks, list_schema_users, list_cache_configurations,
    get_configuration, list_credits, list_entitlements, create_bundle, list_bundles, get_bundle, update_bundle,
    delete_bundle
]
for command in admin_commands:
    admin.add_command(command)

# Add public API subcommands to the public group
public_commands = [register_user, decide, delete_other_sessions, delete_session, list_rules, list_sessions]
for command in public_commands:
    public.add_command(command)

# Add group subcommands to CLI root
cli.add_command(admin)
cli.add_command(public)

if __name__ == '__main__':
    cli()
