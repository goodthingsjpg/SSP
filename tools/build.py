"""建置伸手排。

產出：
  index.html         網頁版（GitHub Pages 用）。字型切成小塊放在 assets/，瀏覽器只下載用得到的字。
  ssp-offline.html   離線單檔版。字型全部內嵌，下載後雙擊就能用。

用法（在專案根目錄）：
    pip install fonttools brotli
    npm install
    npm run build
"""
import base64, glob, os, subprocess, sys
from fontTools.ttLib import TTFont
from fontTools import subset

os.makedirs('build', exist_ok=True)
os.makedirs('assets', exist_ok=True)
SRC_FONT = 'fonts/HanWangKaiMediumChuIn.ttf'

def is_cjk(u):
    return 0x3400 <= u <= 0x9FFF or 0xF900 <= u <= 0xFAFF or 0x20000 <= u <= 0x2FFFF

# 字頻順序（由 jieba 詞頻轉繁體統計而來，常用字在前）
FREQ = [ord(c) for c in open('tools/char_freq_tw.txt', encoding='utf-8').read().strip()]

def chunk_plan(cmap_codes):
    """依字頻把字分組：第 0 組放所有非漢字（標點、英數、注音符號），
    接著最常用的 800 字一組，之後每 250 字一組，冷僻字每 600 字一組。"""
    codes = set(cmap_codes)
    base = sorted(u for u in codes if not is_cjk(u))
    cjk_ordered = [u for u in FREQ if u in codes]
    seen = set(cjk_ordered)
    cjk_ordered += sorted(u for u in codes if is_cjk(u) and u not in seen)
    chunks = [base]
    i = 0
    sizes = [800] + [250] * 16 + [600] * 1000
    for n in sizes:
        if i >= len(cjk_ordered): break
        chunks.append(cjk_ordered[i:i + n]); i += n
    return [c for c in chunks if c]

def unicode_range(codes):
    codes = sorted(codes); out = []; s = p = codes[0]
    for u in codes[1:] + [None]:
        if u is not None and u == p + 1: p = u; continue
        out.append(f'U+{s:X}' if s == p else f'U+{s:X}-{p:X}')
        if u is not None: s = p = u
    return ', '.join(out)

def make_chunks(src_path, family, prefix, local_names=()):
    # 快取：字型與字頻表都沒變就沿用上次切好的檔案（切割很花時間）
    import hashlib, json
    key = hashlib.md5(open(src_path, 'rb').read() + open('tools/char_freq_tw.txt', 'rb').read()
                      + json.dumps([family, list(local_names)]).encode()).hexdigest()
    cache = f'build/faces-{prefix}.css'
    if os.path.exists(cache) and open(cache, encoding='utf-8').readline().strip() == f'/* {key} */':
        print(f'  {family}: 沿用快取')
        return open(cache, encoding='utf-8').read().split('\n', 1)[1]
    for old in glob.glob(f'assets/{prefix}-*.woff2'): os.remove(old)
    cmap = TTFont(src_path).getBestCmap()
    plan = chunk_plan(cmap.keys())
    css = []
    local = ''.join(f"local('{n}'), " for n in local_names)
    for idx, codes in enumerate(plan):
        f = TTFont(src_path)
        opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = []; opts.name_IDs = ['*']; opts.notdef_outline = True
        sub = subset.Subsetter(opts); sub.populate(unicodes=codes); sub.subset(f)
        out = f'assets/{prefix}-{idx:02d}.woff2'
        f.flavor = 'woff2'; f.save(out)
        css.append(f"""        @font-face {{
            font-family: '{family}';
            src: {local}url('{out}') format('woff2');
            font-display: block;
            unicode-range: {unicode_range(codes)};
        }}""")
    total = sum(os.path.getsize(p) for p in glob.glob(f'assets/{prefix}-*.woff2'))
    print(f'  {family}: {len(plan)} 塊，共 {total/1e6:.1f} MB')
    out_css = '\n'.join(css)
    open(cache, 'w', encoding='utf-8').write(f'/* {key} */\n' + out_css)
    return out_css

# 1) 完整注音字型（離線版用）
f = TTFont(SRC_FONT); f.flavor = 'woff2'; f.save('build/hw.woff2')
# 2) 去掉注音的楷體子集（破音字校正用）
subprocess.run([sys.executable, 'tools/build_plain.py'], check=True)

# 3) 共同內容
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

# 4) 網頁版：字型切塊
print('切割字型…')
faces = make_chunks(SRC_FONT, 'CustomPhoneticFont', 'hanwang-zhuyin', ('王漢宗中楷體注音', 'HanWangKaiMediumChuIn'))
faces += '\n' + make_chunks('build/plain.woff2', 'HWKaiPlain', 'hanwang-plain')
for old in ('assets/hanwang-zhuyin.woff2', 'assets/hanwang-plain.woff2'):
    if os.path.exists(old): os.remove(old)
web = t.replace('__FONT_FACES__', faces)
open('index.html', 'w', encoding='utf-8').write(web)
print(f'index.html          {len(web.encode()) / 1e6:.2f} MB')

# 5) 離線版：整套字型內嵌
off_faces = f"""        @font-face {{
            font-family: 'CustomPhoneticFont';
            src: local('王漢宗中楷體注音'), local('HanWangKaiMediumChuIn'), url('data:font/woff2;base64,{b64('build/hw.woff2')}') format('woff2');
            font-display: block;
        }}
        @font-face {{
            font-family: 'HWKaiPlain';
            src: url('data:font/woff2;base64,{b64('build/plain.woff2')}') format('woff2');
            font-display: block;
        }}"""
off = t.replace('__FONT_FACES__', off_faces)
open('ssp-offline.html', 'w', encoding='utf-8').write(off)
print(f'ssp-offline.html    {len(off.encode()) / 1e6:.2f} MB')
