#!/usr/bin/env python3
"""v2.5 cleanliness filter (phase-2 fixes a/b/c included).

- normalize() FIRST: 2+ spaces -> 1, 3+ newlines -> 2
- (a) weird excludes math notation: _ ^ { } \\ ( ) [ ] $ = + - / < >
- (b) homoglyph detection instead of global nonlatin: a non-Latin letter
      INSIDE a word whose other letters are Latin (catches "Badacze" with
      Cyrillic a, passes a full Russian quote)
- (c) noend counted only over lines >= 40 chars (headings are short);
      the insulinoopornosc doc (noend 0.87, all short headings) now passes
"""
import re
import unicodedata

ENDMARK = set(".!?…")
PUNCT_OK = set(".,;:!?-–—()\"'„”‘’…%/+=*<>@#&_^~|$\\[]{}")
MATH_OK = set("_^{}\\" + "()[]$=+-/<>")
PL = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
RE_SLAJD = re.compile(r"slajd\s*\d", re.IGNORECASE)
RE_STRONA = re.compile(r"strona\s*\d+\s*z\s*\d+", re.IGNORECASE)
RE_NUMLINE = re.compile(r"^\d+$")
RE_DOTS = re.compile(r"\.{3,}|…{2,}")
RE_SP3 = re.compile(r" {3,}")
RE_WORD = re.compile(r"\w+", re.UNICODE)


def normalize(text):
    text = re.sub(r" {2,}", " ", text or "")
    return re.sub(r"\n{3,}", "\n\n", text)


def _script(ch):
    try:
        return unicodedata.name(ch).split()[0]
    except Exception:
        return "?"

# Scripts that legitimately mix with Latin in Polish edu text (math Greek,
# micro sign, typographic apostrophe). Everything else mixed into a Latin
# word is a homoglyph/mojibake/CJK-paste candidate. Ordinal indicators
# (º/ª) are fine next to digits (12ºC) but dirt inside words (przykªadowych).
_ALWAYS_OK = {"GREEK", "MICRO", "MODIFIER"}


def homoglyph_words(text):
    """Count words mixing Latin letters with suspicious-script letters."""
    n = 0
    for m in RE_WORD.finditer(text):
        w = m.group(0)
        hit = False
        for i, c in enumerate(w):
            if not c.isalpha():
                continue
            s = _script(c)
            if s == "LATIN":
                continue
            if s in _ALWAYS_OK:
                continue
            if s in ("MASCULINE", "FEMININE"):
                prev_letter = i > 0 and w[i - 1].isalpha()
                next_letter = i + 1 < len(w) and w[i + 1].isalpha()
                if not (prev_letter and next_letter):
                    continue
            hit = True
            break
        if hit and any(_script(c) == "LATIN" for c in w if c.isalpha()):
            n += 1
    return n


def metrics_v2(text):
    text = normalize(text)
    lines = text.split("\n")
    n_lines = max(len(lines), 1)
    long_lines = [l for l in lines if len(l.strip()) >= 40]
    n_long = max(len(long_lines), 1)
    short = sum(1 for l in lines if len(l.strip()) < 40)
    noend = sum(1 for l in long_lines if l.strip()[-1] not in ENDMARK)
    numline = sum(1 for l in lines if RE_NUMLINE.match(l.strip()))
    n_chars = max(len(text), 1)
    weird = sum(1 for c in text
                if not (c.isalnum() or c.isspace() or c in PUNCT_OK
                        or c in MATH_OK))
    runs = re.findall(r"\S+", text)
    longest = max((len(r) for r in runs), default=0)
    return {
        "short_line_share": short / n_lines,
        "noend_long_share": noend / n_long,
        "numline_share": numline / n_lines,
        "weird_share": weird / n_chars,
        "homoglyph_words": homoglyph_words(text),
        "slajd": len(RE_SLAJD.findall(text)),
        "strona": len(RE_STRONA.findall(text)),
        "dots": len(RE_DOTS.findall(text)),
        "sp3": len(RE_SP3.findall(text)),
        "longest_nospace": longest,
        "n_chars": len(text),
    }


# v2.5 rejection thresholds: reject doc if ANY fires
def reject_reasons(m):
    why = []
    if m["noend_long_share"] > 0.85:
        why.append("noend_long>0.85")
    if m["sp3"] > 50:
        why.append("sp3>50")
    if m["longest_nospace"] > 200:
        why.append("glue>200")
    if m["weird_share"] > 0.01:
        why.append("weird>0.01")
    if m["homoglyph_words"] > 2:
        why.append("homoglyph>2")
    if m["numline_share"] > 0.3:
        why.append("numline>0.3")
    if m["short_line_share"] > 0.9:
        why.append("short>0.9")
    return why
