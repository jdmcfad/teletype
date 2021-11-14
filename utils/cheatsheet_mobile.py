#!/usr/bin/env python3

import sys
import pytoml as toml
from pathlib import Path
from string import Template

from common import validate_toml, get_tt_version

if (sys.version_info.major, sys.version_info.minor) < (3, 6):
    raise Exception("need Python 3.6 or later")

CHEATSHEET_TEMPLATE = Template("""
<html>
<head>
<title>${version}</title>
</head>
<body>
</body>
</html>
""")

TT_VERSION = get_tt_version()
VERSION_STR = " ".join(["Teletype", TT_VERSION["tag"], "Documentation"])

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

def cheatsheet_mobile():
    template_dict = {
        'version': TT_VERSION['tag']
    }

    return CHEATSHEET_TEMPLATE.substitute(template_dict)


def main():
    # if len(sys.argv) != 2:
    #     sys.exit("Please supply an output filename")

    # p = Path(sys.argv[1]).resolve()
    # p.write_text(cheatsheet_mobile())

    print(cheatsheet_mobile())

if __name__ == "__main__":
    main()
