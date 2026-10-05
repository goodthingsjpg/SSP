"""建置 index.html：把字型、Tailwind CSS、PDF 套件全部內嵌成單一檔案。
用法（在專案根目錄）：
    pip install fonttools brotli
    npm install
    npm run build
"""
import base64, os, subprocess, sys
from fontTools.ttLib import TTFont

os.makedirs('build', exist_ok=True)
SRC_FONT = 'fonts/HanWangKaiMediumChuIn.ttf'

# 1) 完整注音字型 → WOFF2
f = TTFont(SRC_FONT); f.flavor = 'woff2'; f.save('build/hw.woff2')

# 2) 去掉注音的楷體子集（給破音字校正用）
subprocess.run([sys.executable, 'tools/build_plain.py'], check=True)

# 3) 組合
t = open('src/template.html', encoding='utf-8').read()
plain = TTFont('build/plain.woff2')
chars = ''.join(chr(u) for u in plain.getBestCmap() if u >= 0x3400)
TAGS = ('script', 'body', 'html', 'head', 'style', 'iframe', 'meta', 'title', '!DOCTYPE')
def js(p):
    # 套件裡有一些 HTML 字串（例如 '<body>'），在 JS 字串中把 < 改寫成 \x3c，
    # 執行結果完全相同，但不會被 HTML 檢查工具誤判成多出來的標籤。
    code = open(p, encoding='utf-8').read()
    for tag in TAGS:
        code = code.replace('</' + tag, '\\x3c/' + tag).replace('<' + tag, '\\x3c' + tag)
    return code
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
t = (t.replace('__PLAIN_CHARS__', chars)
      .replace('__TW_CSS__', open('build/tw.css', encoding='utf-8').read())
      .replace('__SHOT__', js('node_modules/modern-screenshot/dist/index.js'))
      .replace('__JSPDF__', js('node_modules/jspdf/dist/jspdf.umd.min.js')))

# 網頁版（GitHub Pages）：字型放在 assets/，只有打開注音模式才會下載，首頁秒開
import shutil
os.makedirs('assets', exist_ok=True)
shutil.copy('build/hw.woff2', 'assets/hanwang-zhuyin.woff2')
shutil.copy('build/plain.woff2', 'assets/hanwang-plain.woff2')
web = (t.replace('data:font/woff2;base64,__HW_FONT__', 'assets/hanwang-zhuyin.woff2')
        .replace('data:font/woff2;base64,__PLAIN_FONT__', 'assets/hanwang-plain.woff2'))
open('index.html', 'w', encoding='utf-8').write(web)
print(f'index.html          {len(web.encode()) / 1e6:.2f} MB（字型另外載入）')

# 離線版：全部內嵌成單一檔案，下載後雙擊就能用
off = (t.replace('__HW_FONT__', b64('build/hw.woff2'))
        .replace('__PLAIN_FONT__', b64('build/plain.woff2')))
open('ssp-offline.html', 'w', encoding='utf-8').write(off)
print(f'ssp-offline.html    {len(off.encode()) / 1e6:.2f} MB（離線單檔版）')
