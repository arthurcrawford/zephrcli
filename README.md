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
### Tag a version
```bash
VERSION=$(cat src/zephrcli/VERSION); git tag -a $VERSION -m "version bump"; git push origin --tags
```
### Get SHA 256 checksum of the tagged tarball
```bash
VERSION=$(cat src/zephrcli/VERSION) && 
  wget "https://github.com/arthurcrawford/zephrcli/archive/refs/tags/${VERSION}.tar.gz" && 
  shasum -a 256 "${VERSION}.tar.gz"
```
### Update Homebrew tap formula
The following changes are made to the `zephrcli.rb` formula in the Homebrew tap repo.

```ruby
  url "https://github.com/arthurcrawford/zephrcli/archive/refs/tags/0.1.41.tar.gz"
  version "0.1.41"
  sha256 "b37f59a05f6a7b72f4cf01bfbfab1c5119473a411a1a05f1ef5cc74aa2f453d1"

  depends_on "python@3.11"

  bottle do
    root_url "https://github.com/arthurcrawford/zephrcli/releases/download/0.1.41"
    sha256 cellar: :any_skip_relocation, arm64_big_sur: "f694dbd875745c0c47ae6295b0c65844e92000cc1e796c2273c959cc3694e2d7"
  end
```
Modify the following in the formula file `zephrcli.rb`
* Update `url` to correct version
* Update `version` to correct version
* Update `sha256` to correct checksum
* Comment out the `bottle` clause 

```bash
git add zephrcli.rb
git commit -m "version bump"
git push
brew update
```

### Build bottle(s)
To speed up the installation, build bottle from the formula.

```bash
brew uninstall zephrcli
brew install --build-bottle arthurcrawford/tap/zephrcli
brew bottle zephrcli
==> Determining arthurcrawford/tap/zephrcli bottle rebuild...
==> Bottling zephrcli--0.1.43.arm64_big_sur.bottle.1.tar.gz...
==> Detecting if zephrcli--0.1.43.arm64_big_sur.bottle.1.tar.gz is relocatable...
./zephrcli--0.1.43.arm64_big_sur.bottle.1.tar.gz
  bottle do
    rebuild 1
    sha256 cellar: :any_skip_relocation, arm64_big_sur: "600614bd593f003fdc7bb2a38aa7229fc18669c46ce331677d9d5e57c3267284"
  end
```

### Create a Github release and add the Bottle
Rename the bottle file replacing `--` characters with `-` and removing the build number.

e.g.

```bash
mv zephrcli--0.1.43.arm64_big_sur.bottle.1.tar.gz zephrcli-0.1.43.arm64_big_sur.bottle.tar.gz
```
Create or update a GitHub release from the appropriate tag.
Upload the bottle binary file to the release and publish.

### Update the formula to use the bottle

Take the suggested bottle clause with the bottle SHA checksum as follows.

```ruby
  bottle do
    rebuild 1
    sha256 cellar: :any_skip_relocation, arm64_big_sur: "600614bd593f003fdc7bb2a38aa7229fc18669c46ce331677d9d5e57c3267284"
  end
```
Modify to remove any build number and add root URL to the GitHub release
```ruby
  bottle do
    root_url "https://github.com/arthurcrawford/zephrcli/releases/download/0.1.43"
    sha256 cellar: :any_skip_relocation, arm64_big_sur: "600614bd593f003fdc7bb2a38aa7229fc18669c46ce331677d9d5e57c3267284"
  end
```

```bash
git add zephrcli.rb
git commit -m "added bottle"
git push
```

Uninstall and then reinstall using the bottle.
```bash
brew uninstall zephrcli
brew update
brew install zephrcli
...
==> Installing zephrcli from arthurcrawford/tap
==> Pouring zephrcli-0.1.43.arm64_big_sur.bottle.tar.gz
🍺  /opt/homebrew/Cellar/zephrcli/0.1.43: 1,014 files, 11.9MB
...
```
