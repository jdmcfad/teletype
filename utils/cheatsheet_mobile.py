#!/usr/bin/env python3

import base64
import sys
import pytoml as toml
from pathlib import Path
from string import Template

from common import validate_toml, get_tt_version

if (sys.version_info.major, sys.version_info.minor) < (3, 6):
    raise Exception("need Python 3.6 or later")

# TODOs:
#  - parse backticks as code

# notes on template:
#  - wipe style from anchors https://stackoverflow.com/a/8919740
#  - viewport & media queries https://stackoverflow.com/a/32155505
#  - viewport units discussion https://alligator.io/css/viewport-units/

CHEATSHEET_PAGE_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<title>${version}</title>
<link id="favicon" rel="shortcut icon" type="image/png" href="${encoded_favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@600;700&family=Roboto:wght@500&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style type="text/css">
body {
    background: #eeeef2; color: #222228;
}
a {
    color: inherit; text-decoration: inherit;
}
code {
    font-family: 'Roboto Mono', monospace;
}
h1 {
    margin: 0px 0px 0.3em 0px; padding: 0.3em 0px 0px 0px; font-family: 'Roboto Mono', monospace; border-bottom: 1px solid #aaaab0;
}
.links {
    /* style */
    font-family: 'Roboto Mono', monospace; padding: 0% 0% 3% 0%; font-size: larger; font-weight: bolder; overflow: hidden; padding-top: 1em;
    /* positioning */
    height: 100vh; width: 10vw; position: fixed; top: 0; left: 0;
}
.content {
    /* style */
    padding: 1%; border-left: 1px solid #aaaab0; overflow: hidden;
    /* positioning */
    height: 100vh; width: 85vw; position: fixed; top: 0; left: 10vw;
}
.content-scrollable {
    overflow-y: scroll; height: 100%; width: 100%; box-sizing: content-box; padding-right: 3em;
}
.links-scrollable {
    overflow-x: hidden; overflow-y: scroll; height: 100%; width: 100%; box-sizing: content-box; white-space: nowrap; padding-top: 1em; padding-right: 1em; writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); text-align: right; 
    -ms-overflow-style: none; /* for Internet Explorer, Edge */
    scrollbar-width: none; /* for Firefox */
    overflow-y: scroll; 
}
.links-scrollable::-webkit-scrollbar {
    display: none; /* for Chrome, Safari, and Opera */
}
.fixturtle {
    /* I suffer for my art */
    transform: rotate(180deg); display: inline-block;
}
.prototype {
    font-family: 'Roboto Mono', monospace; margin-bottom: 0.1em; font-weight: bolder;
}
.short {
    font-family: 'Roboto', sans-serif; margin-bottom: 0.75em;
}
.description {
    font-family: 'Roboto', sans-serif; font-size: smaller; letter-spacing: -0.05em;
}
</style>
<script>
function scrollLinksToTop() {
    document.getElementById("variables-link").scrollIntoView()
}
</script>
</head>
<body onload="scrollLinksToTop()">
<div class="links">${section_links}</div>
<div class="content">${section_content}</div>
</body>
</html>
""")

THIS_FILE = Path(__file__).resolve()
ROOT_DIR = THIS_FILE.parent.parent
TEMPLATE_DIR = ROOT_DIR / "utils" / "templates"
DOCS_DIR = ROOT_DIR / "docs"
OP_DOCS_DIR = DOCS_DIR / "ops"
FONTS_DIR = ROOT_DIR / "utils" / "fonts"
TT_VERSION = get_tt_version()
FAVICON_FILE = DOCS_DIR / "img" / "cheatsheet-favicon.png"
VERSION_STR = " ".join(["Teletype", TT_VERSION["tag"], "Cheatsheet"])

OPS_SECTIONS = [
    ("variables",     "Var",        "Variables"),
    ("hardware",      "H/W",        "Hardware"),
    ("patterns",      "Pat",        "Patterns"),
    ("controlflow",   "Flow",       "Control Flow"),
    ("maths",         "Math",       "Math"),
    ("metronome",     "Metro",      "Metronome"),
    ("delay",         "Del",        "Delay"),
    ("stack",         "Stack",      "Stack"),
    ("queue",         "Queue",      "Queue"),
    ("seed",          "Seed",       "Seed"),
    ("turtle",        "🐢",         "Turtle 🐢"),
    ("grid",          "Grid",       "Grid"),
    ("midi_in",       "MIDI",       "MIDI In"),
    ("i2c",           "I2C",        "Generic I2C"),
    ("ansible",       "Ansible",    "Ansible"),
    ("whitewhale",    "Whale",      "Whitewhale"),
    ("meadowphysics", "Meadow",     "Meadowphysics"),
    ("earthsea",      "Earth",      "Earthsea"),
    ("orca",          "Orca",       "Orca"),
    ("justfriends",   "Friends",    "Just Friends"),
    ("wslash",        "W/",         "W/"),
    ("er301",         "ER-301",     "ER-301"),
    ("fader",         "Fader",      "Fader"),
    ("matrixarchate", "Matrix",     "Matrixarchate"),
    ("telex_i",       "TXi",        "TELEXi"),
    ("telex_o",       "TXo",        "TELEXo"),
    ("disting",       "Disting",    "Disting EX"),
    ("wslashdelay",   "W/delay",    "W/2.0 delay",),
    ("wslashsynth",   "W/synth",    "W/2.0 synth",),
    ("wslashtape",    "W/tape",     "W/2.0 tape",),
    ("crow",          "Crow",       "Crow"),
]

def encode_favicon():
    encoded_image = base64.b64encode(open(FAVICON_FILE, "rb").read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_image}"

def parse_toml_text_to_html(text):
    # (I started doing this with regex and realized I was going to actually die)
    if "`" in text:
        joined = ""
        substrings = text.split("`")
        for ii, substr in enumerate(substrings):
            joined += substr
            is_last = ii == len(substrings) - 1
            if is_last: continue
            if ii % 2 == 0:
                joined += "<code>"
            else:
                joined += "</code>"
        text = joined
    return text

def section_links():
    output = """<div class="links-scrollable">\n"""
    for (section, abbrev, _title) in reversed(OPS_SECTIONS):
        link_text = abbrev if section != "turtle" else f"""<span class="fixturtle">&nbsp;{abbrev}&nbsp;&nbsp;</span>"""
        output += f"""<span class="section"><a href="#{section}" id="{section}-link">{link_text}</a></span>\n"""
    output += "</div>" # close scrollable
    return output


def section_content():
    output = """<div class="content-scrollable">\n"""
    for (section, _abbrev, title) in OPS_SECTIONS:
        toml_file = Path(OP_DOCS_DIR, section + ".toml")
        ops = toml.loads(toml_file.read_text())
        validate_toml(ops)
        output += f"""<h1 id="{section}">{title}</h1>"""
        for op in ops.values():
            output += f"""<div class="prototype">{op["prototype"]}</div>\n"""
            short_text = parse_toml_text_to_html(op["short"])
            output += f"""<div class="short">{short_text}</div>\n"""
    output += "</div>" # close scrollable
    return output

def cheatsheet_mobile():
    template_dict = {
        'encoded_favicon':  encode_favicon(),
        'version':          VERSION_STR,
        'section_links':    section_links(),
        'section_content':  section_content(),
    }

    return CHEATSHEET_PAGE_TEMPLATE.substitute(template_dict)


def main():
    if len(sys.argv) != 2:
        sys.exit("Please supply an output filename")

    page_text = cheatsheet_mobile()

    p = Path(sys.argv[1]).resolve()
    p.write_text(page_text, 'utf-8')

    print(page_text)

if __name__ == "__main__":
    main()
