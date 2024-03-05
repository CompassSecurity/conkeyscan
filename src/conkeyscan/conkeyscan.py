from datetime import datetime
from pathlib import Path
import re
import sys
import requests
import signal
import readchar
import json
import os
from importlib.resources import files

from clize import run
from loguru import logger
from atlassian import Confluence
from bs4 import BeautifulSoup
from requests_ratelimiter import LimiterSession
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# disable annoying insecure requests warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Hook Ctrl-C
def exit_handler(signum, frame):
    msg = "Do you really want to exit? y/n"
    logger.warning(msg)
    res = readchar.readchar()
    if res == "y":
        exit(1)
    else:
        logger.warning(msg)


signal.signal(signal.SIGINT, exit_handler)


def extract_keyword_hits(
    url: str, title: str, html: str, keyword: str, log_file_name: str
):
    text = html
    try:
        text = BeautifulSoup(html, features="html.parser").get_text()
    except:
        logger.warning("Failed converting HTML to text")
    try:
        occurences = [m.start() for m in re.finditer(keyword, text)]
        for occurence in occurences:
            log_line = (
                "[Keyword: "
                + keyword
                + "] "
                + "[URL: "
                + url
                + "] [Title: "
                + title
                + "] ["
                + color_result_log_line(
                    keyword,
                    cleanup_result_log_line(
                        extract_surrounding_string(keyword, text, occurence)
                    ),
                )
                + "]"
            )
            append_to_log_file(log_line, log_file_name)
            logger.opt(colors=True).info(log_line)
    except Exception as e:
        logger.error("Extraction failed due to: " + str(e))


def extract_surrounding_string(keyword: str, content: str, start: int, length=50):
    return (
        content[start - length : start] + content[start : start + len(keyword) + length]
    )


def cleanup_result_log_line(text: str):
    return text.replace("\n", " ")


def color_result_log_line(keyword: str, log_line: str, color="yellow"):
    return log_line.replace(keyword, "<" + color + ">" + keyword + "</" + color + ">")


def get_all_pages(keyword, search_result, confluence_client):
    start = search_result["start"]
    data = search_result["results"]
    size = search_result["size"]
    page_limit = search_result["limit"]
    total_size = search_result["totalSize"]
    if size >= page_limit:
        logger.debug("Fetching " + str(total_size) + " items for keyword " + keyword)
        while start <= total_size:
            start += page_limit
            try:
                next = confluence_client.cql(
                    '{text~"' + keyword + '"}',
                    start=start,
                    limit=None,
                    expand=None,
                    include_archived_spaces=True,
                    excerpt=None,
                )
                data = data + next["results"]
            except Exception as e:
                logger.error(
                    "Failed to fetch page offset at " + str(next) + " due to " + str(e)
                )
    return data


def append_to_log_file(text: str, log_file_name: str):
    log_file = open(log_file_name, "a")
    log_file.write(text + " \n")
    log_file.close()


def store_result_to_disk(id: int, content: dict, path: str):
    file_path = path + "/page_" + id + ".json"
    os.makedirs(path, exist_ok=True)
    if os.path.exists(file_path):
        logger.debug("file for id: " + id + " already exists")
    else:
        with open(file_path, "w") as fp:
            # uncomment if you want empty file
            fp.write(json.dumps(content, indent=4))


def main(
    *,
    url: "u",
    username: "usr",
    password: "pwd",
    dict_path: "d" = str(files("conkeyscan.config").joinpath("dict.txt")),
    disable_ssl_checks: "k" = True,
    rate_limit: "r" = 100,
    proxy: "p" = "",
    user_agent: "a" = "",
    cql: "c" = '{text~"KEYWORD_PLACEHOLDER"}',
    log_level: "l" = "INFO"
):
    """Scan Confluence for keywords using CQL search queries

    :param url: URL of the Confluence instance
    :param username: The username of the account to be used
    :param password: The according password OR an API key!
    :param dict_path: The path to the dictionary file containing the keywords to search for, falls back to included dict
    :param cql: A custom CQL query which must include KEYWORD_PLACEHOLDER at least once in the string which will be repalced by the keyword
    :param disable_ssl_checks: Specify whether to verify SSL/TLS certificates
    :param rate_limit: Max requests per second
    :param proxy: The HTTP or SOCKS proxy to be used (examples: socks5://127.0.0.1:1337 or http://127.0.0.1:8080 )
    :param user_agent: Custom user agent string (default randomly selected)
    :param log_level: Custom loguru log level, one of: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
    """

    logger.remove()
    logger.add(sys.stderr, level=log_level)

    # Strip trailing / from URL if it has one
    if url.endswith("/"):
        url = url[:-1]

    logger.info("Applying rate limit of " + str(rate_limit) + " requests per second")
    rate_limited_session = LimiterSession(per_second=rate_limit)

    if not user_agent:
        user_agent = UserAgent(
            software_names=SoftwareName.CHROME.value, limit=100
        ).get_random_user_agent()
    logger.debug("Using User Agent: " + user_agent)
    rate_limited_session.headers.update({"User-Agent": user_agent})

    if proxy:
        logger.info("Using proxy " + proxy)
        rate_limited_session.proxies.update({"http": proxy, "https": proxy})

    if "KEYWORD_PLACEHOLDER" not in cql:
        logger.error(
            "Your CQL query must inculde the string KEYWORD_PLACEHOLDER where it will be replced by the actual keyword"
        )
        exit(1)

    log_file_name = (
        "conkeyscan_results_" + datetime.now().strftime("%Y_%m_%d_%H_%M") + ".log"
    )

    confluence_client = Confluence(
        url=url,
        username=username,
        password=password,
        verify_ssl=not disable_ssl_checks,
        session=rate_limited_session,
    )

    keywords = []
    try:
        with open(dict_path) as f:
            keywords = f.readlines()
    except:
        logger.error("Keywords could not be loaded from file " + dict_path)
        exit(1)

    logger.info("Searching as user " + username)
    logger.info("Searching for " + str(len(keywords)) + " keywords")
    logger.info("Logging to " + log_file_name + " and stdout")
    logger.info("Storing results to ./results")

    for keyword in keywords:
        keyword = keyword.strip()
        cql_query = cql.replace("KEYWORD_PLACEHOLDER", keyword)
        logger.debug("CQL query: " + cql_query)
        try:
            results = confluence_client.cql(
                cql=cql_query,
                start=0,
                limit=None,
                expand=None,
                include_archived_spaces=True,
                excerpt=None,
            )
        except Exception as e:
            logger.error("Failed searching Confluence: " + str(e))
            break

        try:
            search_results = get_all_pages(keyword, results, confluence_client)
        except Exception as e:
            logger.error("Failed loading result pages: " + str(e))

        for result in search_results:
            if "content" in result:
                id = None
                try:
                    id = result["content"]["id"]
                    pageContent = confluence_client.get_page_by_id(
                        page_id=id, expand="body.view"
                    )
                    store_result_to_disk(id, pageContent, "./results")
                    html = pageContent["body"]["view"]["value"]
                    title = pageContent["title"]
                    url = pageContent["_links"]["base"] + pageContent["_links"]["webui"]
                    extract_keyword_hits(url, title, html, keyword, log_file_name)
                except Exception as e:
                    logger.error(
                        "Failed getting content for id " + id + " due to: " + str(e)
                    )


def entry_point():
    run(main)


if __name__ == "__main__":
    entry_point()
