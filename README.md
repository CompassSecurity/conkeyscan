<p align="center">
    <img width="150" src="https://github.com/CompassSecurity/conkeyscan/blob/main/logo.svg" alt="Conkeyscan logo">
</p>

# Conkeyscan
[![PyPI version](https://badge.fury.io/py/conkeyscan.svg)](https://badge.fury.io/py/conkeyscan)

> A Pentesters Confluence Keyword Scanner

Using the Confluence API search functionality and CQL queries to search for keywords.

# Installation

1. Install from PyPI `pip install conkeyscan`
2. Create a custom dictionary with search terms per line (recommended but optional).
3. And then run it 
```bash
conkeyscan -url 'https://example.atlassian.net'  --username 'ex@amp.le' --password 'ATAT...' -p 'socks5://127.0.0.1:1337' -d ./dict.txt 
```
4. Ask for further help `conkeyscan -h`

# Get Up And Running Manually

1. Install dependencies `pip install -r requirements.txt`

2. Update the `src/conkeyscan/config/dict.txt` file, containing keywords you want to search for. One per line.

3. run it `python3 -m conkeyscan.conkeyscan --url http://192.168.1.2:8090/ --username someUsr --password somePassOrAPIkey`

# Authentication

> It is possible to use a password or an API key.

To create an API key in the cloud go to: https://id.atlassian.com/manage-profile/security/api-tokens.

If testing against OnPrem instance you can create an API key in the user settings.

# Dictionary

The default `dict.txt` file was taken from from [Conf-Thief](https://raw.githubusercontent.com/antman1p/Conf-Thief/master/dictionaries/secrets-keywords.txt).

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