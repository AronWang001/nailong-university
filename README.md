# 宇宙奶龙大学.com

打开 `宇宙奶龙大学.com` → 先播一段「奶龙护送你入学」的动画 → 动画播完自动跳到 **广州大学**官网（https://www.gzhu.edu.cn/）。

纯静态，没有任何构建步骤和外部依赖，丢到任意静态托管上就能跑 ——
**推荐 [Cloudflare Pages](#方案-acloudflare-pages推荐但要迁-ns) 或 [GitHub Pages](#方案-bgithub-pages不用动-ns最省事)，两个都不需要买服务器、也不需要 ICP 备案。**

```
index.html                  页面 + 动画 + 跳转逻辑（CSS/JS 全部内联）
ring.svg                    校徽外圈：旋转的「宇宙奶龙大学·」文字环（矢量，3.5KB）
core.webp / core.png        校徽中心：奶龙（站在文字环底下，所以只有上半身露出来）
favicon.ico                 浏览器页签图标（16/32/48）
favicon.png                 iOS / 安卓主屏图标（512×512）
og.png                      微信、QQ、Twitter 分享卡片图（1200×630）
CNAME                       GitHub Pages 绑定自定义域名用（已填好）
双手交叉站立.png            奶龙原图素材 ← 保留着，方便以后重做抠图
tools/prepare_nailong.py    奶龙抠图 → core.png / core.webp / favicon.*
tools/build_assets.py       文字环 ring.svg + 分享卡片 tools/og.html
tools/preview-core.png      抠图效果的白底预览
```

从零重建全部资源：

```powershell
python tools/prepare_nailong.py && python tools/build_assets.py
```

本地已经是一个初始化好的 git 仓库（分支 `main`，首次提交已完成），推送即可发布：

```powershell
git remote add origin https://github.com/<你的用户名>/nailong-university.git
git push -u origin main
```

---

## 1. 本地先看效果

**方式一：直接双击 `index.html`** —— 最省事，图片能正常显示（想看演示模式就在地址栏末尾补 `?stay`）

**方式二：起个本地服务** —— 更贴近线上，方便测 `?stay` 之类的参数

```powershell
python -m http.server 8801 --directory .
```

* <http://127.0.0.1:8801/index.html?stay> —— **演示模式**，不跳转，动画循环播放
* <http://127.0.0.1:8801/index.html> —— 真跳转，约 3.1 秒后离开

> 页面里所有资源都写成**相对路径**（`core.webp`，而不是 `/core.webp`），所以三种打开方式都正常：
> 双击本地打开（`file://`）、部署在域名根目录、部署在子目录（如 `example.com/nailong/`）。
> ⚠️ 别改回 `/core.webp` 这种根路径：双击打开时它会去找 `D:\core.webp`，页面上图片会全变成碎图标。

## 2. 动画与跳转时序（重点）

时序全部集中在 `index.html` 底部那几个常量里：

| 常量 | 默认值 | 含义 |
| --- | --- | --- |
| `DELAY` | 2600ms | 入场动画 + 停留，进度条走到头的时刻 |
| `EXIT` | 450ms | 离场动画时长（放大 + 淡出，和 CSS 里 `.wrap` 的 `transition` 保持一致） |
| `BUFFER` | 80ms | 余量，等离场动画的最后一帧真正画完 |
| `TOTAL` | `DELAY + EXIT` | 进度条动画时长，正好在跳转那一刻走满 |
| `SPIN` | 4000ms | 文字环转一圈 |

执行流程（默认一共约 3.1 秒）：

1. 页面加载 → `.badge` 弹出、文字环匀速旋转、外圈进度条从 0 走到 100%；
2. `DELAY`（2.6s）后进入离场：徽章放大淡出、标题下移淡出、文字环**越转越快**；
3. 再等 `EXIT + BUFFER`（0.53s），**离场动画播完**，才 `location.replace(TARGET)`。
   —— 用 `replace` 而不是 `href`，跳过去之后按浏览器后退不会又弹回这一页。

> **要改「动画播完才跳转」的等待时长，只改 `DELAY` 和 `EXIT`**：
> 跳转时刻 = `DELAY + EXIT`，进度条也是按这个总时长走的，所以进度条永远在跳转那一瞬间走满。
> `EXIT` 一定要和 CSS 里 `.wrap { transition: ... .45s }` 的时长一致，否则会「动画没播完就跳」或者「播完了还愣一下」。

想让动画更长（比如 6 秒），只改一行即可：

```js
const DELAY = 6000;   // 6 秒后才开始离场
```

其它交互：

* 点击页面任意处 / 按任意键 → 立即离场并跳转（不用等）；
* 右下角「关于」→ 暂停倒计时和进度条，关掉后从剩余时间继续（防止用户看说明时被跳走）；
* 键盘依次按 `c` `y` → 彩蛋，校名会变成「陈宇龙大学」；
* 系统开了「减少动态效果」时，自动降级成 1.2 秒直达、不做动画。

## 3. 想要改的地方

| 想改什么 | 改哪里 |
| --- | --- |
| 跳转目标 | `index.html` 里 `const TARGET = 'https://www.gzhu.edu.cn/';` |
| 文案里的校名 | `const NAME = '广州大学';` |
| 停留/动画时长 | `DELAY`、`EXIT` |
| 配色 | `index.html` 顶部 `:root` 里的 CSS 变量 |
| 文字环上的字 | `tools/build_assets.py` → `build_ring(text=...)`，重跑脚本 |
| 奶龙的样子 | 换掉 `双手交叉站立.png`，重跑 `tools/prepare_nailong.py` |
| 抠图边缘 | `tools/prepare_nailong.py` 里的 `S_LO` / `S_HI` 阈值，配合 `tools/preview-core.png` 调 |
| 分享卡片 | `tools/build_assets.py` → `build_og_html()`，重跑后用 Edge 无头截图 |

重新生成图形：

```powershell
python tools/prepare_nailong.py    # 奶龙抠图 → core.* / favicon.*
python tools/build_assets.py       # 文字环 → ring.svg + tools/og.html
```

`og.png` 是用 Edge 无头模式把 `tools/og.html` 截出来的：

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 `
  --window-size=1200,630 --screenshot="og.png" "file:///<绝对路径>/tools/og.html"
```

## 4. 部署：GitHub Pages 或 Cloudflare Pages（都不用买服务器）

两个都**不需要 ICP 备案**（服务器在境外），免费额度对这么一个小页面来说完全用不完。
唯一要注意的是国内访问速度：GitHub Pages 在国内时快时慢，Cloudflare 一般更稳。

| | GitHub Pages | Cloudflare Pages |
| --- | --- | --- |
| 根域名（apex） | ✅ 4 条 A 记录 | ⚠️ **必须把 NS 迁到 Cloudflare** |
| 子域名（www.） | ✅ CNAME | ✅ CNAME（NS 不用动） |
| HTTPS | ✅ 自动，可开 Enforce HTTPS | ✅ 自动 |
| 部署方式 | git push | git push 或拖拽上传 |
| 国内访问 | 一般（可能被墙/很慢） | 较好 |

> ⚠️ **最重要的一条**：Cloudflare Pages 的**根域名**（`宇宙奶龙大学.com` 本身）要求这个域名是 Cloudflare 上的一个 zone，
> 也就是要把 NS 从 DNSPod 改成 Cloudflare 的。Cloudflare 官方文档原文就是这么写的：
> *"To use a custom apex domain with your Pages project, configure your nameservers to point to Cloudflare's nameservers."*
> 如果不想动 NS，那 Cloudflare Pages 只能挂 `www.宇宙奶龙大学.com` 这种子域名。

### 方案 A：Cloudflare Pages（推荐，但要迁 NS）

1. **迁 NS**：Cloudflare 控制台 → Add a site → 填 `宇宙奶龙大学.com` → 选 Free 计划 → 它会给你两个 NS（形如 `xxx.ns.cloudflare.com`）。
   去 DNSPod 把域名的 NS 改成这两个（腾讯云域名控制台 → 域名 → DNS 修改）。等生效，一般几分钟到几小时。
   ⚠️ 迁 NS 前先在 Cloudflare 里把原有解析记录补齐（或让它自动扫描导入），否则邮件等其它服务会断。
2. **建 Pages 项目**：Workers & Pages → Create → Pages → Connect to Git → 选仓库。
   构建命令**留空**，输出目录填 `/`（纯静态，没有构建步骤）。
3. **绑域名**：项目 → Custom domains → Set up a domain → 填 `xn--psszg58cydsdq780c.com`（punycode；因为已经是 Cloudflare 的 zone，CNAME 会自动创建）。
   顺手把 `www` 也加上，或者在 Rules → Redirect Rules 里把 `www` 302 到根域名。
4. HTTPS 证书自动签发，不用管。国内访问如果遇到慢/被墙，可以在 DNS 里换优选 IP（进阶玩法，非必需）。

### 方案 B：GitHub Pages（不用动 NS，最省事）

1. **建仓库**：GitHub 上新建一个 **public** 仓库（免费账号的 Pages 只支持公开仓库），比如 `nailong-university`。
2. **推代码**：本地已经初始化好 git 仓库并提交了（分支 `main`），只要加个远程地址推上去：

   ```powershell
   git remote add origin https://github.com/<你的用户名>/nailong-university.git
   git push -u origin main
   ```
3. **开 Pages**：仓库 → Settings → Pages → Source 选 `Deploy from a branch` → 分支 `main`、目录 `/ (root)` → Save。
4. **绑域名**：同页面 Custom domain 填 `宇宙奶龙大学.com`。仓库里的 `CNAME` 文件我已经放好了（内容就是这个域名），
   注意 GitHub 要求**国际化域名必须填 punycode**，也就是 `xn--psszg58cydsdq780c.com`；两种写法 GitHub 都能识别，但建议填 punycode 更保险。
5. **加解析**（DNSPod，NS 不用动）：

   | 主机记录 | 类型 | 记录值 |
   | --- | --- | --- |
   | `@` | A | `185.199.108.153` |
   | `@` | A | `185.199.109.153` |
   | `@` | A | `185.199.110.153` |
   | `@` | A | `185.199.111.153` |
   | `www` | CNAME | `<你的用户名>.github.io` |

   （A 记录是 GitHub 官方给的四个 IP；`www` 那条 CNAME 让 `www` 自动 302 到根域名。）
6. **HTTPS**：回到 Settings → Pages，等证书签发完（一般几分钟，最多 24 小时），勾上 **Enforce HTTPS**。

### 方案 C：腾讯云 COS + CDN（也不买服务器，但国内节点要备案）

1. **实名认证**：域名先完成实名认证，否则 DNSPod 不给解析。
2. **建桶**：对象存储 COS → 创建存储桶，地域选就近（如 `ap-guangzhou`），权限选「公有读私有写」。
3. **传文件**：把 `index.html`、`ring.svg`、`core.webp`、`core.png`、`favicon.ico`、`favicon.png`、`og.png` **传到桶的根目录**（`tools/` 和奶龙原图不用传）。
4. **开静态网站**：桶 → 基础配置 → 静态网站 → 开启，索引文档 `index.html`，**错误文档也填 `index.html`**（这样访问不存在的路径也会回到这一页）。
   ⚠️ 但要注意：页面用的是相对路径，所以访问 `域名/a/b` 这种深层路径时，页面能出来、图片会找不到（它会去找 `/a/core.webp`）。
   想彻底干净，就在 CDN 里加一条重定向规则：**路径不含扩展名 → 302 到 `/`**。平时只访问根域名的话可以不管。
5. **绑自定义域名**：桶 → 域名管理 → 添加自定义 CDN 加速域名，加速域名填 `xn--psszg58cydsdq780c.com`（= 宇宙奶龙大学.com），源站类型「默认源站」。
6. **上 HTTPS**：腾讯云 SSL 证书 → 申请免费 DV 证书（DNS 验证，DNSPod 可一键添加验证记录）→ 在 CDN 域名里部署证书 → 打开「强制 HTTPS」。
7. **加解析**：DNSPod 里给 `@` 加一条 **CNAME**，记录值填第 5 步给出的 CNAME 域名。
   （`@` 的 CNAME 和 MX 记录会冲突；DNSPod 的免费版支持根域名 CNAME，但部分解析商会拒绝。）
8. **设缓存**：CDN → 缓存配置里给 `index.html` 设「不缓存」或很短，图片设 7 天，避免改完文案看不到效果。

> 静态网站里中文域名会自动按 punycode（`xn--psszg58cydsdq780c.com`）填写，控制台里显示成中文是正常的。

### 方案 D：轻量应用服务器 / CVM + Nginx

```nginx
# HTTP 全量跳 HTTPS
server {
  listen 80;
  listen [::]:80;
  server_name xn--psszg58cydsdq780c.com www.xn--psszg58cydsdq780c.com;
  return 301 https://$host$request_uri;
}

server {
  listen 443 ssl;
  listen [::]:443 ssl;
  http2 on;
  server_name xn--psszg58cydsdq780c.com www.xn--psszg58cydsdq780c.com;

  ssl_certificate     /etc/nginx/ssl/fullchain.pem;   # 腾讯云免费 DV 证书
  ssl_certificate_key /etc/nginx/ssl/privkey.pem;

  root /var/www/nailong;
  index index.html;
  location / { try_files $uri $uri/ /index.html; }   # 访问不存在的路径也回这一页

  location = /index.html { add_header Cache-Control "no-cache"; }   # 改文案要能立刻生效
  location ~* \.(svg|png|webp|ico)$ { expires 7d; add_header Cache-Control "public"; }
}
```

DNSPod 给 `@` 和 `www` 各加一条 **A 记录**指向服务器公网 IP。

> ⚠️ 只有这个方案（和方案 C 的国内节点）需要 **ICP 备案**（腾讯云备案控制台，约 1～20 个工作日），否则 80/443 会被阻断。
> **GitHub Pages 和 Cloudflare Pages 都在境外，不需要备案** —— 这也是建议你用它们的原因。
> 代价是国内访问速度：GitHub Pages 时快时慢，Cloudflare 相对稳一些，但都不会比备案过的国内节点快。

## 5. 上线自检

- [ ] `https://宇宙奶龙大学.com/?stay` 能看到完整动画，进度条走满、奶龙和文字环都在
- [ ] 不带 `?stay` 时，约 3.1 秒后落到 `https://www.gzhu.edu.cn/`，地址栏不残留本站
- [ ] 手机上打开正常（徽章按 `min(64vw, 44vh, 340px)` 自适应，横竖屏都不溢出）
- [ ] 深色模式下文字环和「宇宙」星空背景正常（系统切深色即可看到）
- [ ] 微信里发链接，卡片图正常显示（`og:image` 用的是绝对地址 `https://xn--psszg58cydsdq780c.com/og.png`；**换了域名记得改这一行**，微信抓不到图会退化成纯文字卡片）
- [ ] 浏览器页签显示奶龙图标（`favicon.ico` + `favicon.png`）
- [ ] 关掉浏览器 JS 也能跳（页面里有 `<noscript>` 的 meta refresh 兜底）
- [ ] **双击本地 `index.html` 时图片也正常**（资源是相对路径，不该出现碎图标）
- [ ] `http://` 能自动跳 `https://`（GitHub Pages 记得勾 Enforce HTTPS；Cloudflare 自动有）
- [ ] 从国内网络实测打开一次（GitHub Pages 偶尔会慢到十几秒，能接受就行）

## 6. 改了东西怎么重新发布

```powershell
git add -A
git commit -m "改了 xxx"
git push
```

GitHub Pages 和 Cloudflare Pages 都会在推上去之后自动重新发布，一般 1 分钟内生效。

> 页面资源里的 `og.png`、`core.webp` 这些文件名没变，浏览器/CDN 可能缓存旧版本。
> 如果改完看不到效果，硬刷新（Ctrl+F5）或者给文件名加版本号（如 `core.v2.webp`）。

## 7. 说明

* 本站与广州大学**没有任何官方关联**，纯属网友自制的整活跳转页，页面里的「关于」弹窗已注明。
* 参考站 `中国奶龙大学.com` 的做法是：域名在 Squarespace 上做 **302** 跳到 `nailong.dykey.net` 落地页，再由落地页的 JS 跳到学校官网（大连理工大学）。本站把它简化成「一个静态页 + 前端跳转」，少一跳、更快，也不需要第二个域名。
* 需要的话也可以给主域名加一条 DNSPod 的「显性 URL 转发」当第一跳，但没必要，多一跳只会更慢。
* 奶龙素材是你提供的 `双手交叉站立.png`（原图是 WebP 贴图、没有透明通道），`tools/prepare_nailong.py` 按饱和度抠的背景；如果发现边缘有灰边或肚皮被啃掉，调 `S_LO` / `S_HI` 两个阈值再重跑即可。
* 文字环上的「宇宙奶龙大学·」是 SVG 里一个个定位的 `<text>`，靠系统字体渲染（微软雅黑 / 苹方），所以不会因为加载字体而闪一下。
