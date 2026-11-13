"""Generate offline work state using fake credentials and temporary data."""
import os
import sys
import json
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_A_REAL_TOKEN', PROVOD_API_KEY='test-only', DATA_DIR=tempfile.mkdtemp())
import app
user = app.get_user(123456)
user.update(lang='ru', world='realism', gender='female', style='warm', scene='phone')
Path(sys.argv[1]).write_text(json.dumps(app.serialize_work_state(user)))
