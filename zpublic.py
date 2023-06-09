import click
import requests
import json


def do_get(path, tenant_id, site_name, rule_type):
    protocol = "https"
    stage = "cdn"
    host = f'{tenant_id}-{site_name}.{stage}.zephr.com'
    query = f'ruleType={rule_type}' if rule_type else ''
    headers = ""

    url = f'{protocol}://{host}{path}?{query}'

    r = requests.get(url, headers=headers)
    print(json.dumps(r.json(), indent=2))


def do_post(path, body, cookies, tenant_id, site_name):
    protocol = "https"
    stage = "cdn"
    host = f'{tenant_id}-{site_name}.{stage}.zephr.com'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    url = f'{protocol}://{host}{path}'

    r = requests.post(url, headers=headers, json=body, cookies=cookies)
    print(json.dumps(r.json(), indent=2))


@click.group()
def cli():
    pass


@cli.command(help='Invoke Zephr rule(s) and retrieve outcomes')
@click.argument('features', nargs=-1)
@click.option('-j', '--jwt')
@click.option('-t', '--tenant-id', required=True, help='Name/Id of the Zephr tenant')
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-i', '--ip', help='Specify IP address of caller: default = actual IP')
@click.option('-f', '--foreign-key', nargs=2, help='Specify a foreign key name and value')
def decide(features, jwt, tenant_id, site_name, ip, foreign_key):
    body = {'features': []}
    cookies = {}
    for f_id in features:
        body['features'].append({'slug': f_id})

    if ip is not None:
        body['ip'] = ip

    if jwt is not None:
        body['jwt'] = jwt
        # Also add to cookies as not certain that jwt in the body works correctly
        cookies = {'blaize_jwt': jwt}

    if foreign_key is not None:
        key, value = foreign_key
        body['foreign_keys'] = {key: value}

    do_post('/zephr/decide', body, cookies, tenant_id, site_name)


@cli.command(help='List available Zephr Features (rules)')
@click.option('-t', '--tenant-id', required=True, help='Name/Id of the Zephr tenant')
@click.option('-s', '--site-name', required=True, help='Name of the Zephr site')
@click.option('-r', '--rule-type', required=True,
              type=click.Choice(['html', 'json', 'sdk', 'browser'], case_sensitive=False))
def list_features(tenant_id, site_name, rule_type):
    do_get("/zephr/features", tenant_id, site_name, rule_type)


if __name__ == '__main__':
    cli()
