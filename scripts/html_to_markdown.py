#!/usr/bin/env python3
"""Convert the text parts of docs/findings_atlas.html into an editable Markdown file.

Charts drawn by JavaScript and tables filled by JavaScript become labelled
placeholders; static base64 images are written out as PNG files next to the
Markdown and referenced normally.
"""
import base64
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"br", "img", "hr", "meta", "link", "input", "source"}
INLINE = {"span", "i", "em", "b", "strong", "code", "sub", "sup", "a", "br",
          "small", "abbr", "u", "s", "mark", "var", "kbd"}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = dict(attrs or {})
        self.children = []
        self.parent = parent

    @property
    def cls(self):
        return self.attrs.get("class", "").split()

    def __repr__(self):
        return f"<{self.tag} {self.attrs.get('class','')}>"


class Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs, self.cur)
        self.cur.children.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent
        if n is not self.root:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(data)


# ---------------------------------------------------------------- inline ----

WS = re.compile(r"\s+")


def sub_sup(txt, marker):
    txt = txt.strip()
    if not txt:
        return ""
    if len(txt) == 1 or re.fullmatch(r"[A-Za-z0-9]", txt):
        return marker + txt
    return marker + "{" + txt + "}"


def inline(node, math=False):
    """Render a node's contents as an inline Markdown string.

    `math` suppresses emphasis markers: inside class="m" the italics are
    typography, not emphasis, so they would only add noise to the Markdown.
    """
    if isinstance(node, str):
        return WS.sub(" ", node)
    out = []
    for ch in node.children:
        if isinstance(ch, str):
            out.append(WS.sub(" ", ch))
            continue
        t, cls = ch.tag, ch.cls
        mm = math or "m" in cls           # class="m" marks maths on any tag
        if t == "br":
            out.append("\n")
        elif t == "span" and ({"chip", "verdict"} & set(cls)):
            out.append(_emph(inline(ch, mm), "**"))
        elif t == "img":
            out.append("")
        elif t == "sub":
            out.append(sub_sup(inline(ch, mm), "_"))
        elif t == "sup":
            out.append(sub_sup(inline(ch, mm), "^"))
        elif t in ("i", "em", "var"):
            inner = inline(ch, mm)
            out.append(inner if mm else _emph(inner, "*"))
        elif t in ("b", "strong"):
            inner = inline(ch, mm)
            out.append(inner if mm else _emph(inner, "**"))
        elif t == "code":
            out.append("`" + inline(ch, mm).strip() + "`")
        elif t == "a":
            href = ch.attrs.get("href", "")
            text = inline(ch, mm).strip()
            out.append(f"[{text}]({href})" if href and not href.startswith("#")
                       else text)
        else:
            out.append(inline(ch, mm))
    return "".join(out)


def _emph(inner, mark):
    stripped = inner.strip()
    if not stripped:
        return ""
    lead = " " if inner[:1].isspace() else ""
    trail = " " if inner[-1:].isspace() else ""
    return f"{lead}{mark}{stripped}{mark}{trail}"


def text_of(node):
    return WS.sub(" ", inline(node)).strip()


def tidy(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" +([,.;:)])", r"\1", s)
    return s.strip()


# ----------------------------------------------------------------- blocks ---

IMG_DIR = None
IMG_REL = None
img_count = 0


def save_image(src):
    global img_count
    m = re.match(r"data:image/(\w+);base64,(.*)", src, re.S)
    if not m or IMG_DIR is None:
        return None
    ext, payload = m.group(1), m.group(2)
    img_count += 1
    name = f"figure_{img_count:02d}.{ext}"
    with open(os.path.join(IMG_DIR, name), "wb") as fh:
        fh.write(base64.b64decode(payload))
    return f"{IMG_REL}/{name}"


def cell_md(c):
    """One table cell; class="mono" cells become code spans, as in the page."""
    s = tidy(inline(c, math="m" in c.cls))
    return f"`{s}`" if s and "mono" in c.cls else s


def table_md(node):
    rows = []
    heads = []

    def walk(n, into):
        for ch in n.children:
            if isinstance(ch, str):
                continue
            if ch.tag == "tr":
                cells = [cell_md(c) for c in ch.children
                         if not isinstance(c, str) and c.tag in ("td", "th")]
                into.append(cells)
            else:
                walk(ch, into)

    for ch in node.children:
        if isinstance(ch, str):
            continue
        if ch.tag == "thead":
            walk(ch, heads)
        elif ch.tag in ("tbody", "tfoot"):
            walk(ch, rows)
        elif ch.tag == "tr":
            walk(node, rows)
            break

    if not heads and rows:
        heads, rows = [rows[0]], rows[1:]
    if not heads:
        return []
    ncol = max([len(r) for r in heads + rows] or [0])

    def line(cells):
        cells = [c.replace("|", "\\|") or " " for c in cells]
        cells += [" "] * (ncol - len(cells))
        return "| " + " | ".join(cells) + " |"

    out = [line(heads[0])]
    out.append("|" + "|".join([" --- "] * ncol) + "|")
    for extra in heads[1:]:
        out.append(line(extra))
    for r in rows:
        out.append(line(r))
    return ["\n".join(out)]


def blocks(node, depth=2):
    """Render a container node into a list of Markdown blocks.

    Runs of inline content (bare text, <b>, <span class="m">, ...) are gathered
    into a single paragraph rather than exploded one block per tag.
    """
    out = []
    run = []

    def flush():
        if run:
            s = tidy("".join(run))
            if s:
                out.append(s)
            run.clear()

    for ch in node.children:
        if isinstance(ch, str):
            run.append(WS.sub(" ", ch))
            continue
        if ch.tag in INLINE and not ({"chart", "tag"} & set(ch.cls)):
            run.append(inline(_wrap(ch)))
            continue
        flush()
        out.extend(block(ch, depth))
    flush()
    return [b for b in out if b]


def _wrap(node):
    """Wrap a single inline node so `inline()` renders it including its own tag."""
    holder = Node("#holder")
    holder.children = [node]
    return holder


def block(n, depth):
    t, cls = n.tag, n.cls

    if t in ("script", "style", "nav", "button", "svg"):
        return []
    if "fig-tools" in cls or "tblview" in cls or "tip" in cls:
        return []

    if t in ("h1", "h2", "h3", "h4", "h5"):
        lvl = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5}[t]
        return ["#" * lvl + " " + tidy(inline(n))]

    if t == "p":
        s = tidy(inline(n))
        if not s:
            return []
        if "src" in cls:
            return ["*Source: " + s + "*"]
        if "fnote" in cls:
            return [s]
        if "note" in cls:
            return ["> " + s.replace("\n", "\n> ")]
        return [s]

    if t in ("ul", "ol"):
        items = []
        for i, li in enumerate([c for c in n.children
                                if not isinstance(c, str) and c.tag == "li"], 1):
            bullet = "- " if t == "ul" else f"{i}. "
            body = blocks(li, depth)
            if not body:
                continue
            first, rest = body[0], body[1:]
            pad = " " * len(bullet)
            chunk = bullet + first.replace("\n", "\n" + pad)
            for r in rest:
                chunk += "\n\n" + pad + r.replace("\n", "\n" + pad)
            items.append(chunk)
        return ["\n".join(items)] if items else []

    if t == "table":
        return table_md(n)

    if t == "dl":
        items = []
        term = None
        def walk(container):
            nonlocal term
            for ch in container.children:
                if isinstance(ch, str):
                    continue
                if ch.tag == "dt":
                    term = tidy(inline(ch))
                elif ch.tag == "dd":
                    items.append(f"- **{term}** — {tidy(inline(ch))}")
                else:
                    walk(ch)
        walk(n)
        return ["\n".join(items)] if items else []

    if t == "img":
        path = save_image(n.attrs.get("src", ""))
        alt = n.attrs.get("alt", "")
        if path:
            return [f"![{alt}]({path})"]
        return ["*[image]*"]

    if t == "figure":
        return blocks(n, depth)

    if t == "figcaption":
        fno = ftitle = ""
        for ch in n.children:
            if isinstance(ch, str):
                continue
            if "fno" in ch.cls:
                fno = tidy(inline(ch))
            elif "ftitle" in ch.cls:
                ftitle = tidy(inline(ch))
        if fno or ftitle:
            return [f"**{fno} — {ftitle}**" if fno and ftitle else
                    f"**{fno}{ftitle}**"]
        return [f"**{tidy(inline(n))}**"]

    if t == "details":
        summary = ""
        rest = []
        for ch in n.children:
            if isinstance(ch, str):
                if ch.strip():
                    rest.append(tidy(ch))
                continue
            if ch.tag == "summary":
                summary = tidy(inline(ch))
            else:
                rest.extend(block(ch, depth))
        head = [f"**{summary}**"] if summary else []
        return head + rest

    if t == "aside":
        return aside_block(n)

    if t == "hr":
        return ["---"]

    if t == "section":
        return blocks(n, depth)

    if t == "header":
        return header_block(n)

    if t == "footer":
        body = blocks(n, depth)
        return ["---"] + body

    if t == "div":
        if "chart" in cls:
            return [f"*[interactive chart: `{n.attrs.get('id','')}`]*"]
        if "plate" in cls:
            return blocks(n, depth)
        if "aside" in cls or "takeaway" in cls:
            return aside_block(n)
        if "stage-head" in cls:
            return stage_head(n)
        if "story" in cls:
            return story(n)
        if "strip" in cls or "kpis" in cls:
            return stat_list(n)
        if "tbl-wrap" in cls:
            inner = blocks(n, depth)
            if not inner and n.attrs.get("id"):
                return [f"*[table generated in the page script: `{n.attrs['id']}`]*"]
            return inner
        if n.attrs.get("id") and not n.children:
            return [f"*[generated in the page script: `{n.attrs['id']}`]*"]
        if "panel" in cls or "panels" in cls or "inner" in cls or "prose" in cls \
                or "shell" in cls or "wide" in cls or not cls:
            return blocks(n, depth)
        return blocks(n, depth)

    if t == "main":
        return blocks(n, depth)

    if t in INLINE:
        s = tidy(inline(n))
        return [s] if s else []

    return blocks(n, depth)


def aside_block(n):
    """An <aside>/div.aside becomes a blockquote, its .tag pill a lead-in."""
    body = blocks(n)
    tag = ""
    for ch in n.children:
        if not isinstance(ch, str) and "tag" in ch.cls:
            tag = tidy(inline(ch))
    if tag:
        body = [b for b in body if b.strip("* ") != tag]
        body = [f"**{tag}.** " + body[0]] + body[1:] if body else [f"**{tag}**"]
    joined = "\n\n".join(body)
    return ["> " + joined.replace("\n", "\n> ")]


def stage_head(n):
    out = []
    eyebrow = h2 = None
    tail = []
    for ch in n.children:
        if isinstance(ch, str):
            continue
        if "eyebrow" in ch.cls:
            eyebrow = tidy(inline(ch))
        elif ch.tag == "h2":
            h2 = tidy(inline(ch))
        else:
            tail.extend(block(ch, 2))
    if eyebrow and h2:
        out.append(f"## {eyebrow} — {h2}")
    elif h2:
        out.append(f"## {h2}")
    elif eyebrow:
        out.append(f"## {eyebrow}")
    return out + tail


def header_block(n):
    out = []
    eyebrow = None
    for ch in n.children:
        if isinstance(ch, str):
            continue
        cls = ch.cls
        if "eyebrow" in cls:
            eyebrow = tidy(inline(ch))
        elif ch.tag == "h1":
            out.append("# " + tidy(inline(ch)))
            if eyebrow:
                out.append("*" + eyebrow + "*")
                eyebrow = None
        elif "dek" in cls:
            out.append(tidy(inline(ch)))
        elif "meta" in cls:
            spans = [tidy(inline(c)) for c in ch.children
                     if not isinstance(c, str)]
            out.append("\n".join("- " + s for s in spans if s))
        elif "kpis" in cls:
            out.extend(stat_list(ch, title="Headline numbers"))
        else:
            out.extend(block(ch, 2))
    return out


def stat_list(n, title=None):
    items = []
    for ch in n.children:
        if isinstance(ch, str):
            continue
        v = l = ""
        for c in ch.children:
            if isinstance(c, str):
                continue
            if "v" in c.cls:
                v = tidy(inline(c))
            elif "l" in c.cls:
                l = tidy(inline(c))
        if v or l:
            items.append(f"- **{v}** — {l}" if v and l else f"- {v}{l}")
        else:
            s = tidy(inline(ch))
            if s:
                items.append("- " + s)
    out = []
    if title:
        out.append(f"**{title}**")
    if items:
        out.append("\n".join(items))
    return out


def story(n):
    items = []
    for step in n.children:
        if isinstance(step, str):
            continue
        k = t = ""
        rest = []
        for c in step.children:
            if isinstance(c, str):
                if c.strip():
                    rest.append(tidy(c))
                continue
            if "k" in c.cls:
                k = tidy(inline(c))
            elif "t" in c.cls:
                t = tidy(inline(c))
            else:
                rest.append(tidy(inline(c)))
        body = " ".join(x for x in rest if x)
        items.append(f"- **{k} · {t}** — {body}".replace(" —  ", " — "))
    return ["\n".join(items)] if items else []


# ------------------------------------------------------------------ main ----

def main(src, dst, img_dir=None, img_rel=None):
    global IMG_DIR, IMG_REL
    IMG_DIR, IMG_REL = img_dir, img_rel
    if img_dir:
        os.makedirs(img_dir, exist_ok=True)
    html = open(src, encoding="utf-8").read()
    body = html[html.index("<main>"):html.index("</main>") + len("</main>")]
    b = Builder()
    b.feed(body)
    out = blocks(b.root)
    md = "\n\n".join(out) + "\n"
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = (f"<!-- Text of {os.path.basename(src)}, extracted for editing.\n"
          "     Interactive charts and script-built tables appear as *[...]* "
          "placeholders;\n"
          "     the four static figures were written out beside this file. -->\n\n"
          + md)
    open(dst, "w", encoding="utf-8").write(md)
    print(f"wrote {dst}  ({len(md)} chars, {md.count(chr(10))+1} lines, "
          f"{img_count} images)")


if __name__ == "__main__":
    main(*sys.argv[1:])
