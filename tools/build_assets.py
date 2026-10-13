# -*- coding: utf-8 -*-
"""生成 宇宙奶龙大学.com 的矢量资源：ring.svg（文字环）+ tools/og.html（分享卡片）

跑法： python tools/build_assets.py
（奶龙本体的 core.png / core.webp / favicon.* 由 tools/prepare_nailong.py 生成）
"""
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent.parent

# 分工：
#   tools/prepare_nailong.py  奶龙抠图 → core.png / core.webp / favicon.ico / favicon.png
#   tools/build_assets.py     文字环 → ring.svg，分享卡片 → tools/og.html
# 两个都跑一遍即可从零重建全部资源：
#     python tools/prepare_nailong.py && python tools/build_assets.py

# ---------------------------------------------------------------- 调色板
YELLOW = "#ffd84d"      # 奶龙身体
YELLOW_DARK = "#e8a800"  # 描边
BELLY = "#fff3b0"       # 肚皮
INK = "#3a2c00"         # 文字
GOLD = "#fece0e"        # 主题黄（进度条）
SEP = "#d99a00"         # 文字环里的间隔点：底色永远是校徽白盘，用深一点的琥珀色才看得清
WHITE = "#ffffff"


# ---------------------------------------------------------------- 文字环
def build_ring(slots: int = 35, radius: int = 252, size: int = 32,
               text: str = "宇宙奶龙大学", sep: str = "·") -> str:
    """沿着圆均分 slots 个字符位，按 文字 + 分隔符 循环排布。"""
    pattern = list(text) + [sep]
    step = 360.0 / slots
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" '
        'width="720" height="720" role="img" aria-label="宇宙奶龙大学">',
        '<g font-family="Microsoft YaHei, PingFang SC, Hiragino Sans GB, Noto Sans SC, sans-serif" '
        f'font-size="{size}" font-weight="800" text-anchor="middle">',
    ]
    for i in range(slots):
        ch = pattern[i % len(pattern)]
        color = SEP if ch == sep else INK
        angle = round(i * step, 4)
        parts.append(
            f'<g transform="rotate({angle} 360 360)">'
            f'<text x="360" y="{360 - radius + size * 0.35:.1f}" fill="{color}">{ch}</text>'
            f'</g>'
        )
    parts.append('</g></svg>')
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------- 分享卡片
def build_og_html() -> str:
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>og</title>
<style>
  * {{ margin: 0; box-sizing: border-box; }}
  html, body {{ width: 1200px; height: 630px; overflow: hidden; }}
  body {{
    display: flex; align-items: center; gap: 64px; padding: 0 84px;
    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    color: #eef1ff;
    background:
      radial-gradient(760px 620px at 88% 12%, rgba(254, 206, 14, .18), transparent 62%),
      radial-gradient(900px 700px at 6% 96%, rgba(76, 120, 255, .3), transparent 60%),
      linear-gradient(140deg, #070a18 0%, #0d1330 52%, #060814 100%);
    position: relative;
  }}
  body::before {{
    content: ""; position: absolute; inset: 0; opacity: .85;
    background-image:
      radial-gradient(2px 2px at 12% 22%, #fff, transparent),
      radial-gradient(1.5px 1.5px at 31% 74%, #dfe8ff, transparent),
      radial-gradient(2.4px 2.4px at 47% 15%, #fff, transparent),
      radial-gradient(1.4px 1.4px at 62% 55%, #cfe0ff, transparent),
      radial-gradient(2px 2px at 74% 27%, #fff, transparent),
      radial-gradient(1.6px 1.6px at 88% 71%, #e6ecff, transparent),
      radial-gradient(1.9px 1.9px at 8% 88%, #fff, transparent),
      radial-gradient(1.4px 1.4px at 68% 90%, #cfe0ff, transparent),
      radial-gradient(1.7px 1.7px at 36% 41%, #fff, transparent),
      radial-gradient(2.2px 2.2px at 95% 9%, #fff, transparent);
  }}
  .badge {{ position: relative; width: 420px; flex: 0 0 auto; aspect-ratio: 1; z-index: 1; }}
  .badge::before {{ content: ""; position: absolute; inset: 1.4%; border-radius: 50%; background: #fff; }}
  .badge img {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
  .badge picture {{ position: absolute; inset: 0; display: block; }}
  .txt {{ position: relative; z-index: 1; display: flex; flex-direction: column; gap: 22px; }}
  h1 {{ font-size: 76px; font-weight: 800; letter-spacing: .1em; white-space: nowrap; }}
  p {{ font-size: 32px; color: #c9d2f0; }}
  .tag {{ font-size: 24px; letter-spacing: .28em; color: {GOLD}; font-weight: 700; }}
</style>
</head>
<body>
  <div class="badge">
    <picture><source srcset="../core.webp" type="image/webp"><img src="../core.png" alt=""></picture>
    <img src="../ring.svg" alt="">
  </div>
  <div class="txt">
    <div class="tag">NAILONG UNIVERSITY</div>
    <h1>宇宙奶龙大学</h1>
    <p>奶龙正在护送你前往 广州大学</p>
  </div>
</body>
</html>
'''


def main() -> None:
    (ROOT / "ring.svg").write_text(build_ring(), encoding="utf-8")
    (ROOT / "tools" / "og.html").write_text(build_og_html(), encoding="utf-8")
    for f in ("ring.svg", "tools/og.html"):
        print(f"{f}: {(ROOT / f).stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
