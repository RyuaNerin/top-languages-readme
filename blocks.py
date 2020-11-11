#!/bin/python

blocks_list = [
    " █",
    "░█",
    "░▒▓█",
    "⣀⣄⣤⣦⣶⣷⣿",
    "⣀⣄⣆⣇⣧⣷⣿",
    "▁▂▃▄▅▆▇█",
    "▏▎▍▌▋▊▉█",
    "○◔◐◕⬤",
    "□◱◧▣■",
    "□◱▨▩■",
    "□▨▩■",
    "□◱▥▦■",
]

bar_width = 10

one_block_percent = 100.0 / bar_width


def gen_bar(percent: int, blocks: str):
    fmt_bar_left = blocks[-1] * int(percent / one_block_percent)
    fmt_bar_mid = blocks[
        0
        if len(blocks) == 2
        else int(
            (percent % one_block_percent) / (one_block_percent / (len(blocks) - 1))
        )
    ]
    return (fmt_bar_left + fmt_bar_mid).ljust(bar_width, blocks[0])


for blocks in blocks_list:
    step = 10 if len(blocks) == 2 else bar_width / (len(blocks) - 1)
    print(format(0, "0.2f").rjust(5), blocks)
    for i in range(0, len(blocks)):
        percent = 50 + step * i
        print(format(percent, "0.2f").rjust(5), gen_bar(percent, blocks))
    print()

percent = 55.5
for blocks in blocks_list:
    fmt_bar = gen_bar(percent, blocks)

    print(f"|`{blocks}`||`{fmt_bar}`|")
