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
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@600&family=Roboto:wght@500&display=swap" rel="stylesheet">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style type="text/css">
body {
    background: #eeeef2; color: #222228;
}
a {
    color: inherit; text-decoration: inherit;
}
.links {
    /* style */
    font-family: 'Roboto Mono', monospace; writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); text-align: right; padding: 1%; font-size: larger;
    /* positioning */
    height: 100vh; width: 10vw; position: fixed; top: 0; left: 0;
}
.content {
    /* style */
    padding: 1%;
    /* positioning */
    height: 100vh; width; 90vw; position: fixed; top: 0; left: 10vw;
}
.fixturtle {
    /* I suffer for my art */
    transform: rotate(180deg); display: inline-block;
}
.prototype {
    font-family: 'Roboto Mono', monospace; 
}
.short {
    font-family: 'Roboto', sans-serif; font-size: smaller; margin-bottom: 0.5em;
}
.description {

}
</style>
</head>
<body>
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
    ("variables",     "Var"),
    ("hardware",      "H/W"),
    ("patterns",      "Pat"),
    ("controlflow",   "Flow"),
    ("maths",         "Math"),
    ("metronome",     "Metro"),
    ("delay",         "Del"),
    ("stack",         "Stack"),
    ("queue",         "Queue"),
    ("seed",          "Seed"),
    ("turtle",        "🐢"),
    # ("grid",          "Grid",          ),
    # ("midi_in",       "MIDI In",       ),
    # ("i2c",           "Generic I2C",   ),
    # ("ansible",       "Ansible",       ),
    # ("whitewhale",    "Whitewhale",    ),
    # ("meadowphysics", "Meadowphysics", ),
    # ("earthsea",      "Earthsea",      ),
    # ("orca",          "Orca",          ),
    # ("justfriends",   "Just Friends",  ),
    # ("wslash",        "W/",            ),
    # ("er301",         "ER-301",        ),
    # ("fader",         "Fader",         ),
    # ("matrixarchate", "Matrixarchate", ),
    # ("telex_i",       "TELEXi",        ),
    # ("telex_o",       "TELEXo",        ),
    # ("disting",       "Disting EX",    ),
    # ("wslashdelay",   "W/2.0 delay",   ),
    # ("wslashsynth",   "W/2.0 synth",   ),
    # ("wslashtape",    "W/2.0 tape",    ),
    # ("crow",          "Crow",          ),
]

def encode_favicon():
    encoded_image = base64.b64encode(open(FAVICON_FILE, "rb").read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_image}"

def section_links():
    output = ""
    for (section, title) in reversed(OPS_SECTIONS):
        section_text = title if section != "turtle" else f"""<span class="fixturtle">{title}</span>"""
        output += f"""<span class="section"><a href="#{section}">{section_text}</a></span>\n"""

    return output


def section_content():
    output = ""
    for (section, title) in OPS_SECTIONS:
        toml_file = Path(OP_DOCS_DIR, section + ".toml")
        ops = toml.loads(toml_file.read_text())
        validate_toml(ops)
        for op in ops.values():
            output += f"""<div class="prototype">{op["prototype"]}</div>\n"""
            output += f"""<div class="short">{op["short"]}</div>\n"""
    
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
