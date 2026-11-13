import json
from pathlib import Path
import sys
from ui_fixture import constants, state
keys = ['APP_PAGE_HTML', 'SFX_JS', 'APP_THEME_CSS', 'APP_TEXTS']
Path(sys.argv[1]).write_text(json.dumps({'constants': {key: constants[key] for key in keys}, 'state': state}, ensure_ascii=False))
