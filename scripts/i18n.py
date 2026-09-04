"""System UI language detection and local message catalogs. No network."""
import contextvars, json, locale, os, pathlib, platform, plistlib, subprocess
CURRENT=contextvars.ContextVar('pulsebeat_language',default=None)
CATALOG=json.loads((pathlib.Path(__file__).resolve().parents[1]/'locales/en.json').read_text(encoding='utf-8'))
def normalize(value):
    value=str(value or '').replace('_','-').lower()
    if value.startswith('zh'): return 'zh-CN'
    if value.startswith('en'): return 'en'
    return None

def system_language():
    try:
        if platform.system()=='Darwin':
            raw=subprocess.check_output(['defaults','export','NSGlobalDomain','-'],timeout=3,stderr=subprocess.DEVNULL)
            langs=plistlib.loads(raw).get('AppleLanguages',[])
            if langs: return normalize(langs[0]) or 'en'
        elif platform.system()=='Windows':
            raw=subprocess.check_output(['powershell','-NoProfile','-NonInteractive','-Command','[System.Globalization.CultureInfo]::CurrentUICulture.Name'],timeout=3,stderr=subprocess.DEVNULL,text=True)
            if raw.strip(): return normalize(raw.strip()) or 'en'
    except (OSError,subprocess.SubprocessError,ValueError): pass
    for key in ('LANGUAGE','LC_ALL','LC_MESSAGES','LANG'):
        value=os.environ.get(key,'').split(':')[0]
        if value and value not in ('C','POSIX','C.UTF-8'): return normalize(value) or 'en'
    return normalize(locale.getlocale()[0]) or 'en'

def resolve(requested='auto'):
    if requested and requested!='auto':
        lang=normalize(requested)
        if not lang: raise ValueError('Supported languages: en, zh-CN, auto')
        return lang
    return normalize(os.environ.get('PULSEBEAT_LANG')) or system_language()

def activate(requested='auto'):
    lang=resolve(requested);CURRENT.set(lang);return lang

def tr(message):
    if (CURRENT.get() or resolve())!='en':return message
    import re
    return re.sub('|'.join(re.escape(k) for k in sorted(CATALOG,key=len,reverse=True)),lambda m:CATALOG[m[0]],message)
