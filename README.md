# Local build

```
pipenv install
```

# Running locally

Use pipenv run for local testing.
```
alias prp='pipenv run python'
```
The main zephr script is in the `zephrcli` package under the `src` directory.
To run locally, `pipenv` reads the contents of the `.env` file which adds this package directory to the `PYTHONPATH` environment variable.
The `.env` file looks like this.

```
cat .env
PYTHONPATH=${PYTHONPATH}:src
```

Show default help message.
```
prp -m zephrcli.zephr
Usage: zephr.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  admin          Admin commands needing API keys
  decide         Invoke rule(s) and get decisions
  list-rules     List rules (aka Features)
  register-user  Register a new user
```
Alternatively, you can use the following `scripts` definition in the Pipfile.

```
[scripts]
zephr = "python -m zephrcli.zephr"
```
You would use it like this.
```
pipenv run zephr
```


The admin commands group require API key/secret credentials.

# Examples

List all product ids.
```bash
prp zephr.py admin list-products --profile dev | jq -r '.results[].id'
```

## Getting decisions on all live features at once.

```bash
ARGS=(`prp zephr.py list-rules --profile dev -r sdk -s ac-test-site | jq -r '.[].id' | tr '\n' ' '`) && prp zephr.py decide --profile dev -s ac-test-site ${ARGS[@]} | jq
```
The first part of the above command lists all SDK features for a site using `jq` to extract just the slug IDs.  The second half of the command sends all these IDs to Zephr to get a decision on each.

List Companies and Accounts

Filter just the names.

```bash
$ prp zephr.py admin list-accounts --profile dev | jq -r '.results[].name'
```
