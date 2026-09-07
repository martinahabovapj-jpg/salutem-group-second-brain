# -*- coding: utf-8 -*-
"""Obnovi sekci Funnel na AI Hubu (/prioritizacni-mapa).

Jeden prikaz udela cely retez:
  1. stahne zive ukoly z Freela (projekt 561017, 5 listu)
  2. vytezi z popisu sablonu v2 (tolerantni parser, hodnota i z dalsiho radku)
  3. spocita faze funnelu, business case a "na cem to stoji"
  4. vlozi/prepise blok <script id="fn-data"> a sekci Funnel v prioritizacni-mapa.html
  5. overi, ze vsechna cisla sedi (Python zrcadlo logiky ve fn.js, Node tu neni)

Pouziti:
    python funnel-ai-hub.py             # cely retez
    python funnel-ai-hub.py --nahled    # spocita a vypise, do stranky NEZAPISE
    python funnel-ai-hub.py --overit    # jen overi cisla uz nasazene stranky

Po zapisu je jeste potreba zmenu commitnout a pushnout v repu salutem-ai-hub
(deploy = git push origin main) a POTOM OVERIT, ze deploy ve Vercelu neskoncil
jako Blocked - push sam nasazeni nezaruci.

Vsechny ceske texty jsou ve funnel-ai-hub.popisky.json, aby v .py nebyla
diakritika (viz poznamka o mojibake v pameti projektu).

Nastaveni: FREELO_EMAIL a FREELO_API_KEY v ~/.claude/settings.json (env).
"""
import argparse
import base64
import datetime
import html
import io
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
SETTINGS = os.path.join(HOME, '.claude', 'settings.json')
HUB = os.path.join(HOME, 'salutem-ai-hub', 'prioritizacni-mapa.html')
L = json.load(open(os.path.join(HERE, 'funnel-ai-hub.popisky.json'), encoding='utf-8'))

PID = 561017
LISTY = {                       # jen listy, ktere do funnelu patri
    1946848: L['listy']['produkcni'],
    1946850: L['listy']['vzdelavaci'],
    1931437: L['listy']['compliance'],
    1943888: L['listy']['udrzovani'],
    1946851: L['listy']['parkoviste'],
}
LIST_UDRZOVANI, LIST_PARKOVISTE = 1943888, 1946851
PIPE = L['pipe']
KEY = L['keys']
V2 = list(KEY.values())
V1 = L['v1_zarazky']            # klice stare sablony: jen zarazky, do vysledku nejdou
ALL_KEYS = sorted(set(V2 + V1), key=len, reverse=True)


# ---------------------------------------------------------------- Freelo
def _auth():
    env = json.load(open(SETTINGS, encoding='utf-8'))['env']
    raw = env['FREELO_EMAIL'] + ':' + env['FREELO_API_KEY']
    return base64.b64encode(raw.encode()).decode()


def freelo_get(path, auth, params=None):
    url = 'https://api.freelo.io/v1' + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'Authorization': 'Basic ' + auth,
        'User-Agent': 'salutem-ai-hub-funnel',
        'Content-Type': 'application/json'})
    for pokus in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and pokus < 4:
                time.sleep(1 + 3 * pokus)        # Freelo umi rate-limitovat
                continue
            raise
        except Exception:
            if pokus < 4:
                time.sleep(1 + 3 * pokus)
                continue
            raise


def stahni():
    auth = _auth()
    ukoly = []
    for lid, nazev in LISTY.items():
        r = freelo_get('/project/%d/tasklist/%d/tasks' % (PID, lid), auth, {'limit': 200})
        tasks = r.get('data', {}).get('tasks') or r.get('tasks') or [] if isinstance(r, dict) else r
        top = [t for t in tasks if not t.get('parent_task_id')]
        print('  list %d %-34s %2d zadani (%d ukolu vcetne podukolu)'
              % (lid, nazev, len(top), len(tasks)))
        for t in top:
            d = freelo_get('/task/%d' % t['id'], auth)
            popis = ''
            for c in (d.get('comments') or []):
                if c.get('is_description'):
                    popis = c.get('content') or ''
                    break
            ukoly.append(dict(
                id=t['id'], name=t['name'], list=nazev, list_id=lid,
                labels=[x['name'] for x in (t.get('labels') or [])],
                vlastnik=(t.get('worker') or {}).get('fullname', ''),
                subtasks=t.get('count_subtasks'), desc=popis))
            time.sleep(0.35)                     # setrne k API
    return ukoly


# ---------------------------------------------------------------- parser sablony v2
def _text(h):
    h = re.sub(r'(?i)<br\s*/?>', '\n', h)
    h = re.sub(r'(?i)</(p|div|li|h[1-6]|tr|td)>', '\n', h)
    h = re.sub(r'(?i)<hr\s*/?>', '\n@@HR@@\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    return html.unescape(h).replace('\xa0', ' ')


def _klic(radek):
    for k in ALL_KEYS:
        if re.match(r'^' + re.escape(k) + r'\s*:', radek, re.I):
            return k
    return None


def parsuj(raw):
    """HTML popisu -> {pole: hodnota}. Hodnota muze byt i na dalsich radcich.
    Blok stare sablony pod <hr> se ignoruje, pokud je nad carou aspon jedno pole v2."""
    pole, cur, buf, pod_carou, videno = {}, None, [], False, False

    def uloz():
        nonlocal cur, buf
        if cur in V2 and not (pod_carou and videno):
            v = ' '.join(x for x in buf if x).strip()
            if v and cur not in pole:
                pole[cur] = v
        cur, buf = None, []

    for radek in _text(raw).split('\n'):
        radek = radek.strip()
        if radek == '@@HR@@':
            uloz()
            pod_carou = True
            continue
        if not radek:
            continue
        k = _klic(radek)
        if k:
            uloz()
            cur = k
            buf = [re.sub(r'^' + re.escape(k) + r'\s*:', '', radek, flags=re.I).strip()]
            if k in V2 and not pod_carou:
                videno = True
        elif cur:
            buf.append(radek)
        # radek bez klice a bez rozdelaneho pole se zahazuje
    uloz()
    return pole


# ---------------------------------------------------------------- zarazeni do funnelu
def faze_ukolu(u, f):
    labs = set(u['labels'])
    if u['list_id'] == LIST_UDRZOVANI:
        if f.get(KEY['vysledek']) and f.get(KEY['overeno'], '').lower().startswith('ano'):
            return 'vyhodnoceno'
        return 'pilot' if PIPE['pilot'] in labs else 'provoz'
    if u['list_id'] == LIST_PARKOVISTE:
        return 'parkoviste'
    for stitek, faze in (('pilot', 'pilot'), ('process', 'realizace'),
                         ('hold', 'schvaleni'), ('backlog', 'zadani'), ('nova', 'napad')):
        if PIPE[stitek] in labs:
            return faze
    return 'bez_stavu'


def business_case(f):
    if f.get(KEY['prinos']):
        return 'plny'
    if f.get(KEY['hodiny']) or f.get(KEY['investice']) or f.get(KEY['typ']):
        return 'castecny'
    return 'zadny'


def na_cem_stoji(u, f):
    labs = set(u['labels'])
    ceka = (f.get(KEY['ceka']) or '').strip()
    prekazka = (f.get(KEY['prekazka']) or '').strip().strip('-').strip()
    chybi = (f.get(KEY['chybi']) or '').strip()
    text = ceka or prekazka or chybi
    if PIPE['backlog'] in labs or chybi:
        return 'zadavatel', text or L['nezapsano_na_co']
    if ceka or prekazka:
        return 'vstup', text
    if PIPE['hold'] in labs:
        return 'rozhodnuti', L['nezapsano_na_koho']
    if PIPE['process'] in labs:
        return 'ai_tym', L['odbavuje_ai']
    return 'nezapsano', '-'


def postav(ukoly, stranka_html):
    items = []
    for u in ukoly:
        f = parsuj(u['desc'])
        blok, blok_text = na_cem_stoji(u, f)
        stitky = [x for x in u['labels'] if x in PIPE.values()]
        items.append(dict(
            id=u['id'], nazev=u['name'], vetev=u['list'], faze=faze_ukolu(u, f),
            bc=business_case(f), blok=blok, blok_text=blok_text,
            vlastnik=u.get('vlastnik', ''),                 # kdo to drzi ve Freelu (worker)
            zadavatel=f.get(KEY['zadavatel'], ''),          # kdo si o to rekl (sablona v2)
            zadani=bool(f.get(KEY['popis']) or f.get(KEY['zadavatel'])),
            prinos=f.get(KEY['prinos'], ''), investice=f.get(KEY['investice'], ''),
            hodiny=f.get(KEY['hodiny'], ''), navratnost=f.get(KEY['navratnost'], ''),
            overeno=f.get(KEY['overeno'], ''), dalsi_krok=f.get(KEY['krok'], ''),
            v_provozu_od=f.get(KEY['odkdy'], ''), podukoly=u['subtasks'],
            dve_stitky=len(stitky) > 1, stitky=stitky))

    # zasobnik podnetu bereme z pm-data na tez strance, aby cisla nemela dva zdroje
    B = json.loads(re.search(r'<script id="pm-data" type="application/json">(.*?)</script>',
                             stranka_html, re.S).group(1))['bolesti']

    def hodin(sub):
        return sum((b.get('cas_h_tyden') or 0) for b in sub)

    zasobnik = []
    for z in L['zasobnik']:
        sub = [b for b in B if b['ai'] == z['ai']]
        zasobnik.append(dict(key=z['key'], nazev=z['nazev'], popis=z['popis'],
                             pocet=len(sub), hodin=hodin(sub)))
    faze = [dict(key=f['key'], nazev=f['nazev'], popis=f['popis'],
                 pocet=sum(1 for i in items if i['faze'] == f['key'])) for f in L['faze']]

    # kdo co drzi. Bez vlastnika je vzdy posledni radek, i kdyz je nejvetsi.
    jmena = sorted(set(i['vlastnik'] for i in items if i['vlastnik']))
    vlastnici = []
    for jm in jmena + ['']:
        moje = [i for i in items if i['vlastnik'] == jm]
        if not moje:
            continue
        vlastnici.append(dict(
            jmeno=jm or L['bez_vlastnika'], je_prazdny=(jm == ''), pocet=len(moje),
            aktivni=sum(1 for i in moje if i['faze'] in ('realizace', 'pilot')),
            ceka=sum(1 for i in moje if i['faze'] in ('schvaleni', 'zadani')),
            bez_cisla=sum(1 for i in moje if i['bc'] == 'zadny')))

    return dict(
        aktualizovano=datetime.date.today().isoformat(), zdroj=L['zdroj'],
        faze=faze, bc_popisky=L['bc'], blok_popisky=L['blok'], zasobnik=zasobnik,
        vlastnici=vlastnici,
        bolesti_celkem=len(B), bolesti_hodin=hodin(B), items=items)


# ---------------------------------------------------------------- vlozeni do stranky
BLOKY = [('        /* ===== Funnel ===== */', '\n        /* ===== END Funnel ===== */\n'),
         ('    <!-- ============ 0. FUNNEL ============ -->',
          '\n    <!-- ============ END FUNNEL ============ -->\n\n'),
         ('    <!-- funnel data -->', '\n    <!-- END funnel data -->\n')]
FUNNEL_LINK = '<a href="#funnel" class="main">' + L['odkaz'] + '</a>'
ODKAZ_MAIN = '<a href="#tabulka" class="main">' + L['odkaz_tabulka'] + '</a>'
ODKAZ_PLAIN = '<a href="#tabulka">' + L['odkaz_tabulka'] + '</a>'
KOTVA = '    <!-- ============ 1. LOGIKA ============ -->'


def vloz(h, data):
    sablony = os.path.join(HERE, 'funnel-ai-hub')
    css = open(os.path.join(sablony, 'funnel.css'), encoding='utf-8').read()
    sekce = open(os.path.join(sablony, 'funnel.html'), encoding='utf-8').read()
    js = open(os.path.join(sablony, 'funnel.js'), encoding='utf-8').read()
    json_radek = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    assert '</script' not in json_radek, 'data obsahuji </script'

    for a, b in BLOKY:                                   # idempotence: vyriznout stare
        i = h.find(a)
        if i != -1:
            j = h.find(b, i)
            assert j != -1, 'nasel jsem zacatek bloku, ne konec: ' + a.strip()[:40]
            h = h[:i] + h[j + len(b):]

    i = h.rindex('    </style>')
    h = h[:i] + css.rstrip('\n') + '\n        /* ===== END Funnel ===== */\n' + h[i:]

    h = h.replace(FUNNEL_LINK + '\n                ', '')
    if h.count(ODKAZ_MAIN) == 1:
        h = h.replace(ODKAZ_MAIN, FUNNEL_LINK + '\n                ' + ODKAZ_PLAIN)
    elif h.count(ODKAZ_PLAIN) == 1:
        h = h.replace(ODKAZ_PLAIN, FUNNEL_LINK + '\n                ' + ODKAZ_PLAIN)
    else:
        raise AssertionError('odkaz na tabulku v pm-jump nenalezen')

    assert h.count(KOTVA) == 1, 'kotva LOGIKA nenalezena prave jednou'
    h = h.replace(KOTVA, sekce.rstrip('\n')
                  + '\n    <!-- ============ END FUNNEL ============ -->\n\n' + KOTVA)

    blok = ('    <!-- funnel data -->\n    <script id="fn-data" type="application/json">'
            + json_radek + '</script>\n' + js.rstrip('\n') + '\n    <!-- END funnel data -->\n')
    i = h.rindex('</body>')
    return h[:i] + blok + h[i:]


# ---------------------------------------------------------------- kontrola cisel
def over(data, hlasite=True):
    """Python zrcadlo logiky ve fn.js. Vraci seznam nesrovnalosti (prazdny = OK)."""
    items, faze, bcl, bll = data['items'], data['faze'], data['bc_popisky'], data['blok_popisky']
    chyby = []

    def chk(co, podminka):
        if not podminka:
            chyby.append(co)
        if hlasite:
            print('  %-56s %s' % (co, 'OK' if podminka else 'NESEDI'))

    chk('soucet fazi = pocet zadani', sum(f['pocet'] for f in faze) == len(items))
    chk('kazde zadani ma znamou fazi', all(i['faze'] in [f['key'] for f in faze] for i in items))
    chk('soucet zasobniku = bolesti_celkem',
        sum(z['pocet'] for z in data['zasobnik']) == data['bolesti_celkem'])
    chk('soucet hodin zasobniku = bolesti_hodin',
        sum(z['hodin'] for z in data['zasobnik']) == data['bolesti_hodin'])
    chk('kategorie business casu se scitaji',
        sum(Counter(i['bc'] for i in items).values()) == len(items))
    chk('kategorie "na cem to stoji" se scitaji',
        sum(Counter(i['blok'] for i in items).values()) == len(items))
    for f in faze:
        if f['pocet']:
            radek = sum(1 for i in items if i['faze'] == f['key'])
            chk('radek krize "%s"' % f['nazev'][:30], radek == f['pocet'])
    chk('vsechny klice business casu jsou popsane',
        set(i['bc'] for i in items) <= set(b['key'] for b in bcl))
    chk('vsechny klice blokace jsou popsane',
        set(i['blok'] for i in items) <= set(b['key'] for b in bll))
    chk('vlastnici se scitaji na pocet zadani',
        sum(v['pocet'] for v in data.get('vlastnici', [])) == len(items))
    return chyby


def prehled(data):
    items = data['items']
    print('\nFAZE')
    for f in data['faze']:
        print('  %-26s %3d' % (f['nazev'], f['pocet']))
    print('\nBUSINESS CASE')
    naz = {b['key']: b['nazev'] for b in data['bc_popisky']}
    for k, v in Counter(i['bc'] for i in items).most_common():
        print('  %-26s %3d' % (naz[k], v))
    print('\nNA CEM TO STOJI')
    naz = {b['key']: b['nazev'] for b in data['blok_popisky']}
    for k, v in Counter(i['blok'] for i in items).most_common():
        print('  %-40s %3d' % (naz[k], v))
    print('\nKDO CO DRZI (vlastnik = worker ve Freelu)')
    for v in data.get('vlastnici', []):
        print('  %-24s %3d zadani | aktivnich %2d | ceka %2d | bez cisla %2d'
              % (v['jmeno'], v['pocet'], v['aktivni'], v['ceka'], v['bez_cisla']))
    dve = [i for i in items if i['dve_stitky']]
    if dve:
        print('\nDVA STITKY NARAZ (porusuje "prave jeden stitek"):')
        for i in dve:
            print('  ', i['id'], i['nazev'][:56], i['stitky'])
    bez = [i for i in items if i['faze'] == 'bez_stavu']
    if bez:
        print('\nBEZ STITKU PIPELINE (funnel je neumi zaradit):')
        for i in bez:
            print('  ', i['id'], i['nazev'][:56])


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description='Obnovi sekci Funnel na AI Hubu.')
    ap.add_argument('--nahled', action='store_true', help='spocitat a vypsat, do stranky nezapisovat')
    ap.add_argument('--overit', action='store_true', help='jen overit cisla uz nasazene stranky')
    a = ap.parse_args()

    if a.overit:
        h = open(HUB, encoding='utf-8').read()
        m = re.search(r'<script id="fn-data" type="application/json">(.*?)</script>', h, re.S)
        if not m:
            print('Na strance zadny blok fn-data neni. Spust skript bez --overit.')
            return 1
        data = json.loads(m.group(1))
        print('Stav na strance k', data['aktualizovano'])
        prehled(data)
        print('\nKONTROLA CISEL')
        chyby = over(data)
        print('\n' + ('VSE OK' if not chyby else 'NESEDI: ' + ', '.join(chyby)))
        return 1 if chyby else 0

    print('1/5 stahuji zive ukoly z Freela (projekt %d)' % PID)
    ukoly = stahni()
    print('    celkem %d zadani' % len(ukoly))

    print('2/5 + 3/5 vytezuji sablonu v2 a pocitam faze')
    h = open(HUB, encoding='utf-8').read()
    data = postav(ukoly, h)
    prehled(data)

    print('\n4/5 kontrola cisel')
    chyby = over(data)
    if chyby:
        print('\nNESEDI: %s - do stranky NEZAPISUJI.' % ', '.join(chyby))
        return 1

    if a.nahled:
        out = os.path.join(HERE, 'funnel-ai-hub.nahled.json')
        json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('\n5/5 nahled - do stranky se nezapisovalo. Data:', out)
        return 0

    print('5/5 zapisuji do stranky')
    novy = vloz(h, data)
    shutil.copyfile(HUB, HUB + '.bak')
    open(HUB, 'w', encoding='utf-8', newline='').write(novy)
    print('    %s: %d -> %d bajtu' % (os.path.basename(HUB), len(h), len(novy)))
    print('    zaloha:', HUB + '.bak')
    print('\nHOTOVO. Jeste je potreba v repu salutem-ai-hub:')
    print('    git add prioritizacni-mapa.html && git commit && git push origin main')
    print('  a POTOM overit, ze deploy ve Vercelu neskoncil jako Blocked.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
