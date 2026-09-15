"""Edit Japanese and English while preserving the other published editions.

ORDER is the stable column order of existing translation tables. Never reorder
it when changing the active edition set. New messages may instead be keyed by
language code and need only cover the active editions.
"""
ORDER = ['en', 'ja', 'ko', 'zh-CN', 'zh-TW', 'es', 'pt', 'fr', 'de']
ACTIVE_LANGUAGES = ['ja', 'en']
VISIBLE_LANGUAGES = ['en', 'ja']
PAUSED_LANGUAGES = [language for language in ORDER if language not in ACTIVE_LANGUAGES]


def authored_translations(value, key):
    if isinstance(value, dict):
        if set(value) - set(ORDER):
            raise ValueError('Unknown language in authored message: ' + key)
        value = [value.get(language) for language in ORDER]
    if not isinstance(value, list) or len(value) != len(ORDER):
        raise ValueError('Use a language-keyed message or a stable translation table: ' + key)
    for language in ACTIVE_LANGUAGES:
        text = value[ORDER.index(language)]
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Missing ' + language + ' text: ' + key)
    return value
