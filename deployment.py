"""Explicit staging credentials and storage. Importing this module makes no network calls."""
import os
from pathlib import Path

def configure(environ=None):
 env=os.environ if environ is None else environ
 mode=env.get('RD_DEPLOYMENT','production')
 if mode not in ('production','staging'):raise ValueError('RD_DEPLOYMENT must be production or staging')
 if mode!='staging':return False
 token=env.get('STAGING_BOT_TOKEN','').strip()
 url=env.get('STAGING_WEBAPP_URL','').strip().rstrip('/')
 directory=Path(env.get('STAGING_DATA_DIR','data-staging')).resolve()
 if not token:raise ValueError('Staging requires its own STAGING_BOT_TOKEN')
 if token==env.get('BOT_TOKEN'):raise ValueError('Staging and production bot tokens must differ')
 if not url.startswith('https://'):raise ValueError('Staging requires a separate HTTPS STAGING_WEBAPP_URL')
 if url==env.get('WEBAPP_URL','').rstrip('/'):raise ValueError('Staging and production Mini App URLs must differ')
 if 'staging' not in directory.name.lower():raise ValueError('Staging storage directory name must include staging')
 if directory==Path(env.get('DATA_DIR','data')).resolve():raise ValueError('Staging storage must be isolated')
 env.update(BOT_TOKEN=token,WEBAPP_URL=url,DATA_DIR=str(directory))
 return True
