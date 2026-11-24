"""Persisted, independent model routes. Selecting a model never sends a completion."""
import re

KEY = 'ai_model_routes_v1'
DEFAULT_MODEL = 'deepseek-v3.2'
ROUTES = ('ai', 'intim')


def initialize(settings, legacy_hot=''):
    """One migration pins normal chat to the requested tested model.

    Keep an explicitly configured legacy scene model; otherwise scenes follow chat.
    Later deployments must never overwrite an administrator's saved selections.
    """
    current = settings.get(KEY)
    if isinstance(current, dict) and all(isinstance(current.get(k), str) and current[k] for k in ROUTES):
        return False
    settings[KEY] = {'ai': DEFAULT_MODEL, 'intim': legacy_hot.strip() or 'same'}
    return True


def selected(settings, route):
    if route not in ROUTES:
        raise ValueError('Unknown model route')
    routes = settings.get(KEY) or {}
    chat = routes.get('ai') or DEFAULT_MODEL
    scene = routes.get('intim') or 'same'
    return chat if route == 'ai' or scene == 'same' else scene


def update(settings, route, model):
    if route not in ROUTES or not isinstance(model, str) or not model.strip():
        raise ValueError('Invalid model selection')
    if model == 'same' and route != 'intim':
        raise ValueError('Only the scene route can follow chat')
    initialize(settings)
    settings[KEY] = {**settings[KEY], route: model}


def catalog_id(entries, requested):
    """Resolve only an exact ID or canonical slug, never a fuzzy version match."""
    if not isinstance(requested, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./:+\-]{0,159}', requested):
        raise ValueError('Укажи точный ID модели из каталога.')
    matches = {e['id'] for e in entries if isinstance(e.get('id'), str)
               and e.get('available', True) is not False
               and requested in (e['id'], e.get('canonical_slug'))}
    if len(matches) != 1:
        raise ValueError('Модель недоступна, не найдена или ID неоднозначен. Открой /ai_models и выбери точный вариант.')
    return matches.pop()
