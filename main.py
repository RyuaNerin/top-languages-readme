#!/bin/python
import base64
import datetime
import os
import re
import typing
from collections import defaultdict

import requests
from github import Github

import options

c_message = options.generate_commit_message(os.getenv("INPUT_COMMIT_MESSAGE"))

START_COMMENT = "<!--START_SECTION:top_language-->"
END_COMMENT = "<!--END_SECTION:top_language-->"
listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"

owner = os.getenv("INPUT_USERNAME")
ghtoken_default = os.getenv("INPUT_GH_TOKEN_DEFAULT")
ghtoken = os.getenv("INPUT_GH_TOKEN")

list_count = int(os.getenv("INPUT_LIST_COUNT"))

line_format = os.getenv("INPUT_LINE_FORMAT")
blocks = os.getenv("INPUT_BLOCKS")
bar_width = int(os.getenv("INPUT_BAR_WIDTH"))
show_total = os.getenv("INPUT_SHOW_TOTAL") == "true"
show_total_top = os.getenv("INPUT_TOP_TOTAL") == "true"
show_total_separator = os.getenv("INPUT_SHOW_TOTAL_SEPARATOR") == "true"

if blocks == "":
    blocks = os.getenv("INPUT_EMPTY_BLOCK") + os.getenv("INPUT_DONE_BLOCK")

one_block_percent = 100.0 / bar_width


def formatWithIEC(sz: float):
    iec = [
        "B  ",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ]

    i = 0
    while sz >= 1000 and i < len(iec) - 1:
        sz = sz / 1024.0
        i += 1

    return f"{sz:.2f} {iec[i]}"


def gen_bar(percent: int, blocks: str):
    fmt_bar_left = blocks[-1] * int(percent / one_block_percent)
    fmt_bar_mid = (blocks[0] if len(blocks) == 2 else blocks[int(
        (percent % one_block_percent) / (one_block_percent /
                                         (len(blocks) - 1)))])
    return (fmt_bar_left + fmt_bar_mid).ljust(bar_width, blocks[0])


def get_stats():
    repo_list: typing.List[str] = []

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "bearer " + ghtoken,
    }

    page = 0
    while True:
        page += 1
        res = requests.get(
            f"https://api.github.com/user/repos?visibility=all&per_page=100&page={page}",
            headers=headers,
        )
        if res.status_code != 200:
            res = requests.get(
                f"https://api.github.com/users/{owner}/repos?per_page=100&type=all&page={page}",
                headers=headers,
            )

        data = res.json()

        try:
            for repo in data:
                if repo["fork"]:
                    continue
                repo_list.append(repo["full_name"])

            if len(data) < 100:
                break
        except Exception as e:
            raise e

    langs: typing.Dict[str, int] = defaultdict(int)
    size_total = 0

    for repo in repo_list:
        data = requests.get(f"https://api.github.com/repos/{repo}/languages",
                            headers=headers).json()
        for lang in data:
            size = data[lang]
            langs[lang] += size
            size_total += size

    langs: typing.List[typing.Tuple[str, int]] = list(
        sorted(langs.items(), key=lambda x: x[1], reverse=True))[:list_count]

    if show_total:
        if show_total_top:
            langs.insert(0, ("TOTAL", size_total))
        else:
            langs.append(("TOTAL", size_total))

    pad_name = max([len(x[0]) for x in langs])
    pad_size = max([len(formatWithIEC(x[1])) for x in langs])

    data_list: typing.List[str] = []
    for lang, size in langs:
        """
        `````___``````````_`````````````````````_````````
        C#   |||153.00 MiB|===================  | 80.00 %
        Java ||| 22.50 KiB|==========           |  8.12 %
        ------------------|---------------------|-------
        TOTAL|||xxx.xx MiB|                     |100.00 %
        """
        percent = 100.0 * size / size_total

        fmt_name = lang.ljust(pad_name, " ")
        fmt_size = formatWithIEC(size).rjust(pad_size, " ")
        fmt_percent = format(percent, "0.2f").rjust(6) + " %"

        fmt_bar = gen_bar(percent, blocks)

        if lang == "TOTAL":
            if show_total_separator and not show_total_top:
                data_list.append("-" * max([len(x) for x in data_list]))
            fmt_bar = blocks[-1] * bar_width

        data_list.append(
            line_format.replace("$NAME",
                                fmt_name).replace("$SIZE", fmt_size).replace(
                                    "$BAR",
                                    fmt_bar).replace("$PERCENT", fmt_percent))

        if lang == "TOTAL":
            if show_total_separator and show_total_top:
                data_list.append("-" * max([len(x) for x in data_list]))

    if show_total:
        """
            ___           _                     __
        C#      153.00 MiB |||||||||||||||||||    80.00 %
        Java     22.50 KiB ||||||||||              8.12 %
        """

    print("Graph Generated")
    data = "\n".join(data_list)
    print(data)
    return "```text\n" + data + "\n```"


if __name__ == "__main__":
    g = Github(ghtoken_default)

    repo = g.get_repo(f"{owner}/{owner}")

    stat_str = get_stats()

    content = repo.get_readme()
    old_readme = str(base64.b64decode(content.content), "utf-8")
    new_readme = re.sub(listReg, f"{START_COMMENT}\n{stat_str}\n{END_COMMENT}",
                        old_readme)
    repo.update_file(
        branch="master",
        path=content.path,
        sha=content.sha,
        message=c_message,
        content=new_readme,
    )
