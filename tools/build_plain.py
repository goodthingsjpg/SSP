# 從王漢宗中楷體注音抽出「不含注音」的字形，用於破音字校正
import json, sys
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen

src = 'fonts/HanWangKaiMediumChuIn.ttf'
chars = open('tools/plain_chars.txt', encoding='utf-8').read()
bopo = ''.join(chr(c) for c in range(0x3105, 0x312A)) + 'ˊˇˋ˙'
keep = sorted(set(c for c in chars + bopo if not c.isspace()))

f = TTFont(src)
cm = f.getBestCmap()
missing = [c for c in keep if ord(c) not in cm]
keep = [c for c in keep if ord(c) in cm]
opts = subset.Options(); opts.name_IDs = ['*']; opts.notdef_outline = True; opts.layout_features = []
sub = subset.Subsetter(opts); sub.populate(unicodes=[ord(c) for c in keep]); sub.subset(f)

gs = f.getGlyphSet(); glyf = f['glyf']; hmtx = f['hmtx']; cm = f.getBestCmap()
bopo_set = set(ord(c) for c in bopo)
for u, gn in cm.items():
    rec = RecordingPen(); gs[gn].draw(rec)
    # 依 closePath 切出每個輪廓
    contours, cur = [], []
    for op in rec.value:
        cur.append(op)
        if op[0] in ('closePath', 'endPath'):
            contours.append(cur); cur = []
    def minx(c):
        xs = [p[0] for op in c for p in op[1]]
        return min(xs) if xs else 0
    if u in bopo_set:
        kept = contours
        bp = BoundsPen(gs); [ [getattr(bp, op[0])(*op[1]) for op in c] for c in kept ]
        x0, _, x1, _ = bp.bounds
        dx = round((1024 - (x1 - x0)) / 2 - x0)
    else:
        kept = [c for c in contours if minx(c) < 1000]   # 右側 >1000 為注音
        dx = 0
    pen = TTGlyphPen(None)
    for c in kept:
        for op, args in c:
            args = tuple((x + dx, y) for x, y in args)
            getattr(pen, op)(*args)
    g = pen.glyph(); g.recalcBounds(glyf)
    glyf[gn] = g
    hmtx[gn] = (1024, g.xMin if hasattr(g, 'xMin') else 0)

for rec in f['name'].names:
    if rec.nameID in (1, 3, 4, 6):
        rec.string = 'HWKaiPlain' if rec.platformID != 3 or rec.nameID != 6 else 'HWKaiPlain'
f.flavor = 'woff2'
f.save('build/plain.woff2')
print('chars', len(keep), 'missing', ''.join(missing))
