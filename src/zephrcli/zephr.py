import hashlib
import json
import time
import uuid
import click
import requests
import importlib.resources

from .api_auth import admin_api_command, public_api_command, login, logout

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


# def do_post(tenant_id, client_id, client_secret, path, body={}, extra_headers={}):
#     protocol = "https"
#     host = f'{tenant_id}.api.zephr.com'
#     body_string = json.dumps(body)
#     method = "POST"
#     query = ""
#     authorization_header_value = create_zephr_authorization_header(body_string, method, path, query)
#     headers = {'Authorization': authorization_header_value,
#                'Content-Type': 'application/json'}
#     headers.update(extra_headers)
#
#     url = f'{protocol}://{host}{path}'
#     return requests.post(url, headers=headers, json=body)

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


@click.command(help='List users, or select by foreign key query')
@admin_api_command
@click.option('-f', '--foreign-key', nargs=2, help='Query by foreign key e.g. "-f my_fk 1234"')
def list_users(profile, tenant_id, client_id, client_secret, foreign_key):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)

    query = ''
    if foreign_key is not None:
        key, value = foreign_key
        query = f'foreign_key.{key}={value}'

    do_get_admin(tenant_id, client_id, client_secret, "/v3/users",
                 query=query)


@click.command()
@admin_api_command
@click.argument('user-id')
def get_user(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}")


@click.command()
@admin_api_command
@click.option('-j', '--jwt')
@click.option('-z', '--session-id', help='ID of the requesting session')
@click.argument('email')
def create_session(profile, tenant_id, client_id, client_secret, jwt, email):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
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
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)

    # https://{tenantId}.api.zephr.com/v3/users/{user_id}/sessions
    do_get_admin(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret,
                 path=f'/v4/users/{user_id}/sessions')


@click.command()
@admin_api_command
@click.argument('user-id')
def get_user_grants(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}/grants")


# TODO - doesn't work as documented - always returns 404! raise issue with Zephr
@click.command()
@admin_api_command
def list_account_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/accounts/users")


@click.command(help="Accounts the user is a member of")
@admin_api_command
@click.argument('user-id')
def list_user_accounts(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    # NOTE - rather than return empty list - this returns 404 if no results
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}/accounts")


@click.command(help='Add a user to a company account')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def add_user_to_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_put(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@click.command(help='Remove user from company account')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
@click.option('-a', '--account-id', required=True, help='The ID of the company account')
def remove_user_from_account(profile, tenant_id, client_id, client_secret, user_id, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}/users/{user_id}")


@click.command(help='Delete a user')
@admin_api_command
@click.option('-u', '--user-id', required=True, help='The ID of the user')
def delete_user(profile, tenant_id, client_id, client_secret, user_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/users/{user_id}")


@click.command()
@admin_api_command
def list_schema_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/schema/users")


@click.command()
@admin_api_command
def list_unclaimed_gifts(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/gift")


@click.command()
@admin_api_command
def list_request_rules(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/request-rules")


@click.command()
@admin_api_command
def list_accounts(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/accounts")


@click.command()
@admin_api_command
@click.argument('account-id')
def get_account(profile, tenant_id, client_id, client_secret, account_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/accounts/{account_id}")


@click.command()
@admin_api_command
def list_feature_rules(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/feature-rules")


@click.command()
@admin_api_command
def list_companies(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/companies")


@click.command()
@admin_api_command
@click.argument('company-id')
def get_company(profile, tenant_id, client_id, client_secret, company_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@click.command()
@admin_api_command
@click.argument('company-id')
def delete_company(profile, tenant_id, client_id, client_secret, company_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_delete_admin(tenant_id, client_id, client_secret, f"/v3/companies/{company_id}")


@click.command()
@admin_api_command
def list_products(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/products")


@click.command()
@admin_api_command
def list_meters(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/meters")


@click.command()
@admin_api_command
def list_static(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/static")


@click.command()
@admin_api_command
def list_webhooks(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/webhooks")


@click.command()
@admin_api_command
def list_schema_users(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/schema/users")


@click.command()
@admin_api_command
def list_cache_configurations(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/cache-configurations")


@click.command()
@admin_api_command
def get_configuration(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/configuration")


@click.command()
@admin_api_command
def list_credits(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/credits")


@click.command()
@admin_api_command
def list_entitlements(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/entitlements")


@click.command()
@admin_api_command
def list_bundles(profile, tenant_id, client_id, client_secret):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, "/v3/bundles")


@click.command()
@admin_api_command
@click.argument('bundle-id')
def get_bundle(profile, tenant_id, client_id, client_secret, bundle_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    do_get_admin(tenant_id, client_id, client_secret, f"/v3/bundles/{bundle_id}")


@click.command(help='List rules (aka Features)')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-r', '--rule-type', required=True,
              type=click.Choice(['html', 'json', 'sdk', 'browser'], case_sensitive=False))
def list_rules(profile, tenant_id, site_name, rule_type):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    query = f'ruleType={rule_type}' if rule_type else ''
    do_get_public("/zephr/features", tenant_id, site_name, query)


@click.command(help='List sessions for the authenticated user')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt', required=True, help='JWT bearing foreign key user ID')
@click.option('-z', '--session-id', help='ID of the requesting session')
def list_sessions(profile, tenant_id, site_name, jwt, session_id):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
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
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
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
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
    cookies = {'blaize_jwt': jwt,
               'blaize_session': session_id}
    do_delete_public(path=f"/zephr/public/sessions/v1/sessions?except-current",
                     tenant_id=tenant_id, site_name=site_name, cookies=cookies)


# https://{your-domain}/zephr/public/sessions/v1/sessions&except-current

@click.command(help='Invoke rule(s) and get decisions')
@public_api_command
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-j', '--jwt')
@click.option('-f', '--foreign-key', nargs=2, help='Specify a foreign key name and value')
@click.option('-i', '--ip', help='Specify IP address of caller: default = actual IP')
@click.option('-u', '--user-agent', help='Specify the User-Agent header')
@click.option('-z', '--session-id', help='ID of the requesting session')
@click.argument('features', nargs=-1)
def decide(profile, tenant_id, site_name, jwt, foreign_key, ip, user_agent, session_id, features):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
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
@click.option('-f', '--foreign-key', nargs=2, help='Specify a foreign key name and value')
def register_user(profile, tenant_id, site_name, email, foreign_key):
    click.echo(click.style(f'Using profile: {profile}', fg='green'), err=True)
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
admin.add_command(login)
admin.add_command(logout)
admin.add_command(list_products)
admin.add_command(list_users)
admin.add_command(list_user_sessions)
admin.add_command(get_user)
admin.add_command(create_session)
admin.add_command(get_user_grants)
admin.add_command(list_account_users)
admin.add_command(list_user_accounts)
admin.add_command(add_user_to_account)
admin.add_command(remove_user_from_account)
admin.add_command(delete_user)
admin.add_command(list_schema_users)
admin.add_command(list_unclaimed_gifts)
admin.add_command(list_request_rules)
admin.add_command(list_accounts)
admin.add_command(get_account)
admin.add_command(list_feature_rules)
admin.add_command(list_companies)
admin.add_command(get_company)
admin.add_command(delete_company)
admin.add_command(list_meters)
admin.add_command(list_static)
admin.add_command(list_webhooks)
admin.add_command(list_schema_users)
admin.add_command(list_cache_configurations)
admin.add_command(get_configuration)
admin.add_command(list_credits)
admin.add_command(list_entitlements)
admin.add_command(list_bundles)
admin.add_command(get_bundle)

public.add_command(register_user)
public.add_command(decide)
public.add_command(delete_other_sessions)
public.add_command(delete_session)
public.add_command(list_rules)
public.add_command(list_sessions)

# Add subcommands to CLI root
cli.add_command(admin)
cli.add_command(public)

if __name__ == '__main__':
    cli()
