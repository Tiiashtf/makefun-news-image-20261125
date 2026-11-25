# makefun-news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Tiiashtf/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Tiiashtf/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper front page that sums up Wednesday 25 November 2026 in one image: drone strikes reported at three Russian refineries in the Samara region, the Zaporizhzhia toll rising to 50 injured, Russia recruiting Indonesian and Filipino citizens with civilian job offers, Iran's fresh tanker claims in the Strait of Hormuz, and the day's briefs — hunger, Gaza, and sport. Every story on the page was reported on 25 November 2026.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is pure Python 3.13 standard library: it draws the whole front page — masthead, headlines, illustrations — with a small pixel canvas and a hand-authored 5x7 dot-matrix face, then writes `entry.png` (1024x1024, under 1 MiB). It needs no network and no input files, and every run writes the exact same bytes. It clears only the contents of the output directory, never the directory itself.

---

<sub>Entered on [make.fun](https://make.fun/?ref=635rx196&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
