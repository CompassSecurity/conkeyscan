# Conkeyscan

Scan Confluence Wikis for keywords.

The approach is using the search functionality and CQL queries to search for keywords in Confluence.

# PyPI

`pip install conkeyscan`

# Run It

1. Download the latest release [here](https://github.com/CompassSecurity/conkeyscan/releases).

2. Create a dictionary with search terms per line or copy the default `dict.txt` from this repository.

3. and then run it 
```bash
./conkeyscan -url 'https://example.atlassian.net'  --username 'ex@amp.le' --password 'ATAT...' -p 'socks5://127.0.0.1:1337' -d ./dict.txt 
```

# Get Up And Running Manually

1. Install dependencies `pip install -r requirements.txt`

2. Update the `dict.txt` file, containing keywords you want to search for. One per line.

3. run it `python3 -m conkeyscan.conkeyscan --url http://192.168.1.2:8090/ --username someUsr --password somePassOrAPIkey`

4. Profit 🍾 check the generated logfile or stdout

5. Further Help `python3 -m conkeyscan.conkeyscan -h`


# Authentication

> It is possible to use a password or an API key.

To create an API key in the cloud go to: https://id.atlassian.com/manage-profile/security/api-tokens
If testing against OnPrem instance you can create an API key in the user settings.

# Dictionary

The default `dict.txt` file was taken from from [Conf-Thief](https://raw.githubusercontent.com/antman1p/Conf-Thief/master/dictionaries/secrets-keywords.txt)

# Features

* Search for provided keywords
* Handle rate limiting by itself, as long as the returned status code equals `HTTP 429`, or specify max requests per second in CLI
* The user agent is randomized
* Proxying is supported either via HTTP or socks. See cli help for examples
* Custom CQL
* SSL/TLS checks are disabled by default

# Alternatives 

* https://spark1.us/n0s1 actually great, supports Jira and others as well, has some drawbacks in on-prem engagements e.g disable TLS verification, missing Proxying, rate-limiting adaption?. Scans everything, nice for CI.
* https://github.com/BluBracket/confluence-risk-scanner
* https://github.com/antman1p/Conf-Thief