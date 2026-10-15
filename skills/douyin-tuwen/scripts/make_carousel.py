#!/usr/bin/env python3
"""把一组图片打包成自包含的左右滑动 HTML carousel（单文件，可 ::preview 展示）。

用法:
    python3 make_carousel.py --title "标题" --out widget.html img1.png img2.jpg ...

支持 png/jpg/webp，图片 base64 内嵌；滚动吸附 + 指针拖拽 + 圆点 + 键盘翻页。
CSS 使用宿主主题变量(--foreground/--card/--border/--accent)，聊天框内自动适配暗色。
"""
import argparse
import base64
import mimetypes
import pathlib

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
.app{width:430px;font-family:var(--font-family,-apple-system,'PingFang SC',sans-serif);color:var(--foreground)}
.hd{display:flex;align-items:baseline;justify-content:space-between;margin:2px 0 8px}
.hd .t{font-size:13px;font-weight:700;letter-spacing:.04em}
.hd .c{font-size:12px;color:var(--muted-foreground);font-variant-numeric:tabular-nums}
.wrap{position:relative;border-radius:14px;overflow:hidden;background:var(--card);border:1px solid var(--border);touch-action:pan-y}
.track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;cursor:grab}
.track::-webkit-scrollbar{display:none}
.track.dragging{cursor:grabbing;scroll-snap-type:none}
.slide{flex:0 0 100%;scroll-snap-align:center;display:flex;justify-content:center;padding:10px}
.slide img{max-height:MAXHpx;width:auto;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,.12);-webkit-user-drag:none;user-select:none;pointer-events:none}
.nav{position:absolute;top:50%;transform:translateY(-50%);width:32px;height:32px;border-radius:50%;background:color-mix(in srgb,var(--card) 82%,transparent);border:1px solid var(--border);color:var(--foreground);font-size:15px;line-height:1;display:flex;align-items:center;justify-content:center;cursor:pointer;opacity:.55;transition:opacity .15s}
.nav:hover{opacity:1}
.nav.prev{left:8px}.nav.next{right:8px}
.nav[disabled]{opacity:.15;cursor:default}
.dots{display:flex;gap:6px;justify-content:center;padding:10px 0 2px}
.dot{width:6px;height:6px;border-radius:50%;background:var(--border);cursor:pointer;transition:all .2s}
.dot.on{background:var(--accent);width:16px;border-radius:3px}
.tip{font-size:11px;color:var(--muted-foreground);text-align:center;margin-top:2px}
</style></head>
<body><div class="app">
  <div class="hd"><span class="t">TITLE</span><span class="c"><span class="cur">1</span>/N</span></div>
  <div class="wrap">
    <div class="track">SLIDES</div>
    <button class="nav prev" disabled>&#8249;</button><button class="nav next">&#8250;</button>
  </div>
  <div class="dots">DOTS</div>
  <div class="tip">TIP</div>
</div>
<script>
const track=document.querySelector('.track'),slides=[...document.querySelectorAll('.slide')],
cur=document.querySelector('.cur'),prev=document.querySelector('.prev'),next=document.querySelector('.next'),
dots=[...document.querySelectorAll('.dot')];let idx=0;
const go=k=>{idx=Math.max(0,Math.min(slides.length-1,k));
track.scrollTo({left:slides[idx].offsetLeft-track.offsetLeft,behavior:'smooth'});
cur.textContent=idx+1;prev.disabled=idx===0;next.disabled=idx===slides.length-1;
dots.forEach((d,j)=>d.classList.toggle('on',j===idx));};
prev.onclick=()=>go(idx-1);next.onclick=()=>go(idx+1);
dots.forEach(d=>d.onclick=()=>go(+d.dataset.k));
document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')go(idx-1);if(e.key==='ArrowRight')go(idx+1);});
let down=null,startX=0,startL=0,moved=false;
track.addEventListener('pointerdown',e=>{down=true;moved=false;startX=e.clientX;startL=track.scrollLeft;track.classList.add('dragging');track.setPointerCapture(e.pointerId);});
track.addEventListener('pointermove',e=>{if(!down)return;const dx=e.clientX-startX;if(Math.abs(dx)>4)moved=true;track.scrollLeft=startL-dx;});
const up=()=>{if(!down)return;down=false;track.classList.remove('dragging');
if(moved){const w=slides[0].offsetWidth;go(Math.round(track.scrollLeft/w));}else go(idx);};
track.addEventListener('pointerup',up);track.addEventListener('pointercancel',up);
track.addEventListener('scroll',()=>{if(down)return;const w=slides[0].offsetWidth;
const k=Math.round(track.scrollLeft/w);if(k!==idx){idx=k;cur.textContent=idx+1;
prev.disabled=idx===0;next.disabled=idx===slides.length-1;dots.forEach((d,j)=>d.classList.toggle('on',j===idx));}}});
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--title', default='图片浏览')
    ap.add_argument('--tip', default='拖拽 / ← → 键 / 点击圆点翻页')
    ap.add_argument('--max-height', type=int, default=640, help='单图最大显示高度 px')
    ap.add_argument('--out', required=True)
    ap.add_argument('images', nargs='+')
    a = ap.parse_args()

    slides = []
    for p in a.images:
        path = pathlib.Path(p)
        if not path.is_file():
            sys_exit(f'not found: {path}')
        mime = mimetypes.guess_type(path.name)[0] or 'image/png'
        b64 = base64.b64encode(path.read_bytes()).decode()
        slides.append(f'<div class="slide"><img src="data:{mime};base64,{b64}"></div>')
    if not slides:
        sys_exit('no images given')

    dots = ''.join(f'<span class="dot{" on" if k == 0 else ""}" data-k="{k}"></span>'
                   for k in range(len(slides)))
    html = (TPL
            .replace('TITLE', a.title)
            .replace('TIP', a.tip)
            .replace('MAXH', str(a.max_height))
            .replace('SLIDES', '\n'.join(slides))
            .replace('DOTS', dots)
            .replace('/N<', f'/{len(slides)}<'))
    out = pathlib.Path(a.out)
    out.write_text(html)
    print(f'{out}: {len(slides)} slides, {out.stat().st_size // 1024}KB')


def sys_exit(msg):
    raise SystemExit(f'error: {msg}')


if __name__ == '__main__':
    main()
