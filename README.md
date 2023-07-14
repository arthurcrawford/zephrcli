# zephrcli
I created `zephrcli` as my own test and development tool during an integration project with the subscriber
experience platform Zephr. 

As my needs became more involved, scripts using `curl` and `postman` etc started to become limited me and 
were difficult to share around the team.  So I built this to help me learn how to use Zephr more effectively.

If you find it helpful too, please feel free to use.  If you don't find it helpful, I don't really mind 😌.

It is provided as-is, with no guarantees, and does not represent any official 
Zephr or Zuora sanctioned project.

Currently only `macOS` is supported.

# Installation

```bash
# Install zephrcli
brew install arthurcrawford/tap/zephrcli
# Check it works
zephr --help                                   
```

`zephrcli` subcommands are grouped into either `zephr admin`, requiring API keys, or `zephr public`, which just 
require the tenant ID.

# Authentication

The `admin login` command stores an API key and secret encrypted in the keychain, under a named profile.
```bash
zephr admin login
```
```
Profile: dev
Tenant id: acmecorp-dev
Client id: c47f5039-306b-46a3-941d-4f191a9cd838
Client secret: ****
```
The `admin logout` command removes the named profile from the keychain.
```bash
zephr admin logout --profile dev
```
```
logged out profile: dev
```
With a stored profile you can execute `zephr admin` commands like this.
```bash
zephr admin list-users --profile dev
```

Stored profiles can be found in the login keychain by searching for `zephr`.

You don't have to store keys in a profile.  You can specify them in command line arguments, environment variables or 
just enter the values when prompted.

`zephr public` commands do not need API keys, but it is still convenient to specify them with a profile, since the 
profile also stores the tenant ID, which is required.  For example:

```bash
# by specifying a profile
zephr public list-rules -r sdk -s my-site --profile dev
```
```bash
# or by specifying the tenant ID explicitly
zephr public list-rules -r sdk -s my-site --tenant-id acmecorp
```

# Local install & run
You will need `python > 3.11` and `pipenv` installed locally. The most convenient way to install, run and test locally 
is then to use `pipenv` which manages the dependencies and creates a virtual environment.
```bash
pipenv install
pipenv run zephr
```

`pipenv` uses the following `scripts` definition in the Pipfile to run the right module.
```
[scripts]
zephr = "python -m zephrcli.zephr"
```

The main zephr script is in the `zephrcli` package under the `src` directory.
When running in this way, `pipenv` reads the contents of the `.env` file which adds this 
package directory to the `PYTHONPATH` environment variable as follows.

```
PYTHONPATH=${PYTHONPATH}:src
```

# Example Usage
#### List SDK rules
```bash
zephr public list-rules --profile dev -s ac-test-site -r sdk | jq -r '.[].id'
```
#### List users
```bash
zephr admin list-users --profile dev | jq -r '.results[].identifiers.email_address'
```
#### List product IDs
```bash
zephr admin list-products --profile dev | jq -r '.results[].id'
```
#### List company account names
```bash
zephr admin list-accounts --profile dev | jq -r '.results[].name'
```
#### Get decisions for all live features
```bash
ARGS=(`zephr public list-rules --profile dev -r sdk -s ac-test-site \
  | jq -r '.[].id' | tr '\n' ' '`) && \
  zephr public decide --profile dev -s ac-test-site ${ARGS[@]} | jq
```
The first part of the above command lists all SDK features for a site
using `jq` to extract just the slug IDs.  The second half of the command
sends all these IDs to Zephr to get a decision on each.

# Packaging
