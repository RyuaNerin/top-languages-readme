import base64
import os
import re
import typing
from collections import defaultdict

import requests
from github import Github

START_COMMENT = "<!--START_SECTION:top_language-->"
END_COMMENT = "<!--END_SECTION:top_language-->"
listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"

owner = os.getenv("INPUT_USERNAME")
ghtoken = os.getenv("INPUT_GH_TOKEN")

commit_message = os.getenv("INPUT_COMMIT_MESSAGE")

done_block = os.getenv("INPUT_DONE_BLOCK")
empty_block = os.getenv("INPUT_EMPTY_BLOCK")
list_count = int(os.getenv("INPUT_LIST_COUNT"))


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
        data = requests.get(
            f"https://api.github.com/repos/{repo}/languages", headers=headers
        ).json()
        for lang in data:
            size = data[lang]
            langs[lang] += size
            size_total += size

    langs: typing.List[typing.Tuple[str, int]] = list(
        sorted(langs.items(), key=lambda x: x[1], reverse=True)
    )[:list_count]

    pad_name = len(max([x[0] for x in langs], key=len))
    pad_size = len(max([formatWithIEC(x[1]) for x in langs], key=len))

    data_list = []
    for (lang, size) in langs:
        """
            ___           _                     _
        C#      153.00 MiB |||||||||||||||||||   80.00 %
        Java     22.50 KiB ||||||||||             8.12 %
        """
        percent = 100.0 * size / size_total

        fmt_name = lang + (" " * (pad_name - len(lang)))
        fmt_size = formatWithIEC(size)
        fmt_size = (" " * (pad_size - len(fmt_size))) + fmt_size
        fmt_bar = round(percent)
        fmt_bar = (
            f"{done_block * int(fmt_bar / 4)}{empty_block * int(25 - int(fmt_bar / 4))}"
        )
        fmt_percent = format(percent, "0.2f").rjust(5)

        data_list.append(f"{fmt_name}   {fmt_size} {fmt_bar} {fmt_percent} %")

    print("Graph Generated")
    data = "\n".join(data_list)
    print(data)
    return "```text\n" + data + "\n```"


if __name__ == "__main__":
    g = Github(ghtoken)

    repo = g.get_repo(f"{owner}/{owner}")

    stat_str = get_stats()

    content = repo.get_readme()
    old_readme = str(base64.b64decode(content.content), "utf-8")
    new_readme = re.sub(
        listReg, f"{START_COMMENT}\n{stat_str}\n{END_COMMENT}", old_readme
    )
    if new_readme != old_readme:
        repo.update_file(
            branch="master",
            path=content.path,
            sha=content.sha,
            message=commit_message,
            content=new_readme,
        )
