# -*- coding: utf-8 -*-
"""把「双手交叉站立.png」（真·奶龙素材）抠图，做成校徽中心和站点图标。

产出：
  core.png / core.webp   校徽中心（720×720，透明背景，白盘由页面 CSS 画）
  favicon.png            站点图标（512×512，白底圆盘 + 奶龙，iOS/安卓主屏用）
  favicon.ico            浏览器页签图标（16/32/48 三档）
  tools/preview-core.png 白底预览，用来肉眼检查抠图边缘

素材没有 alpha 通道，背景是浅灰渐变 + 地面阴影；奶龙是饱和的黄色，
所以用 HSV 饱和度做抠图：背景 R≈G≈B（饱和度极低），奶龙和肚皮都明显偏黄。

抠完还要做一步「只留最大连通域」：原图右下角的地面阴影饱和度略高于阈值，
会残留几块十几个像素的碎片。它们本身看不见，但会把 alpha 包围盒撑大
（实测右边界从 413 被撑到 504），而 place() 是拿包围盒来算居中的 ——
结果奶龙整只会偏左半格。所以必须先把这些孤岛清掉。

跑法： python tools/prepare_nailong.py
"""
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "双手交叉站立.png"

CANVAS = 720               # 和 ring.svg 的 viewBox 一致
FIT = 486                  # 校徽中心：奶龙最长边占的像素数
FIT_ICON = 524             # 图标：可以占得更满一点
S_LO, S_HI = 0.055, 0.16   # 饱和度阈值：低于 LO 判为背景，高于 HI 判为奶龙
KEEP_T = 64                # 「算连通域」用的阈值：低于它的像素不参与判定
ALPHA_MIN = 40             # 最终 alpha 低于它的直接抹成 0（清掉大片极淡的阴影）


def saturation(rgb: np.ndarray) -> np.ndarray:
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    return (mx - mn) / np.maximum(mx, 1e-6)


def keep_largest_blob(a: Image.Image) -> Image.Image:
    """只保留最大的一块连通区域，其余孤岛一律抹掉（4 邻接，广度优先）。

    这一步是为了修「奶龙不居中」：残留阴影碎片会把包围盒撑大，而居中用的是包围盒。
    """
    al = np.asarray(a).copy()
    h, w = al.shape
    mask = al >= KEEP_T                 # 只有够实的像素才算「奶龙的一部分」
    seen = np.zeros((h, w), bool)

    # 先把不达标的像素的 alpha 归零，剩下的再按连通域筛
    al[~mask] = 0

    best: list[tuple[int, int]] = []
    for sy in range(h):
        row = mask[sy]
        for sx in range(w):
            if not row[sx] or seen[sy, sx]:
                continue
            # 从 (sy, sx) 泛洪，收集这一整块
            seen[sy, sx] = True
            queue = deque([(sy, sx)])
            blob = [(sy, sx)]
            while queue:
                y, x = queue.popleft()
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
                        blob.append((ny, nx))
            if len(blob) > len(best):
                best = blob

    keep = np.zeros((h, w), bool)
    for y, x in best:
        keep[y, x] = True
    al[~keep] = 0
    return Image.fromarray(al, "L")


def cutout() -> Image.Image:
    """按饱和度抠出奶龙，返回带 alpha 的 RGBA 图。"""
    src = Image.open(SRC).convert("RGB")
    rgb = np.asarray(src).astype(np.float32)
    alpha = np.clip((saturation(rgb) - S_LO) / (S_HI - S_LO), 0.0, 1.0)

    a = Image.fromarray((alpha * 255).astype(np.uint8), "L")
    a = a.filter(ImageFilter.MedianFilter(5))      # 干掉孤立噪点
    a = a.filter(ImageFilter.GaussianBlur(0.8))    # 轻微羽化，边缘不生硬
    a = a.point(lambda v: 0 if v < ALPHA_MIN else (255 if v > 200 else int((v - ALPHA_MIN) * 255 / (200 - ALPHA_MIN))))
    a = keep_largest_blob(a)

    out = src.convert("RGBA")
    out.putalpha(a)
    return out


def place(cut: Image.Image, fit: int = FIT, canvas: int = CANVAS) -> Image.Image:
    """裁掉 alpha 之外的空白，等比缩放到 fit 像素，居中放进 canvas。

    居中用的是 alpha 包围盒，所以 cutout() 必须先把残留噪点清干净，否则会偏。
    """
    bbox = cut.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    body = cut.crop(bbox)
    scale = fit / max(body.size)
    body = body.resize((max(1, round(body.width * scale)), max(1, round(body.height * scale))),
                       Image.LANCZOS)
    layer = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    layer.paste(body, ((canvas - body.width) // 2, (canvas - body.height) // 2), body)
    return layer


def build_icon(cut: Image.Image) -> Image.Image:
    """白底圆盘 + 奶龙，缩到 512×512。"""
    disc = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse((8, 8, CANVAS - 8, CANVAS - 8), fill=(255, 255, 255, 255))
    disc.alpha_composite(place(cut, fit=FIT_ICON))
    return disc.convert("RGB").resize((512, 512), Image.LANCZOS)


def main() -> None:
    cut = cutout()
    core = place(cut)
    icon = build_icon(cut)

    core.save(ROOT / "core.png", optimize=True)
    core.save(ROOT / "core.webp", quality=88, method=6)   # 页面实际用的是这个，小一个数量级
    icon.save(ROOT / "favicon.png", optimize=True)        # apple-touch-icon / 安卓主屏
    icon.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])  # 浏览器页签

    preview = Image.new("RGB", core.size, (255, 255, 255))
    preview.paste(core, (0, 0), core)
    preview.save(ROOT / "tools" / "preview-core.png")

    for f in ("core.png", "core.webp", "favicon.png", "favicon.ico"):
        print(f"{f}: {(ROOT / f).stat().st_size / 1024:.1f} KB")

    # 自检：包围盒必须和画布同心，否则页面上奶龙会偏
    box = core.getbbox()
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    print(f"奶龙包围盒: {box}  尺寸 {box[2]-box[0]}x{box[3]-box[1]}")
    print(f"包围盒中心: ({cx:.1f}, {cy:.1f})   画布中心: ({CANVAS/2:.1f}, {CANVAS/2:.1f})"
          f"   偏移: ({cx - CANVAS/2:+.1f}, {cy - CANVAS/2:+.1f})")
    assert abs(cx - CANVAS / 2) <= 1 and abs(cy - CANVAS / 2) <= 1, "奶龙没居中！检查 keep_largest_blob"


if __name__ == "__main__":
    main()
