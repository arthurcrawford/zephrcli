# Examples

## Getting decisions on all live features at once.

```bash
ARGS=(`python zpublic.py list-features -r sdk ac-test-site | jq -r '.[].id' | tr '\n' ' '`) && python zpublic.py decide ${ARGS[@]} | jq
```
The first part of the above command lists all SDK features for a site using `jq` to extract just the slug IDs.  The second half of the command sends all these IDs to Zephr to get a decision on each.

List Companies and Accounts

Filter just the names.

```bash
$ prp zadmin.py list-accounts | jq -r '.results[].name'
```
