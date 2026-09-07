# -*- coding: utf-8 -*-
"""Doplni business vlastnika ke kazde ze 125 bolesti v prioritizacni mape.

Cte vlastnici-bolesti.json (vazby z Airtable, cteno pres MCP konektor) a zapisuje
do bloku <script id="pm-data"> na prioritizacni-mapa.html tri nova pole:

    vlastnik        jmeno cloveka, nebo prazdne
    vlastnik_role   role toho cloveka, nebo role bez jmena
    vlastnik_zdroj  dolozeny | pravdepodobny | role | nedohledano

Pri prvnim spusteni prida i sloupec Vlastnik do tabulky vsech 125 bolesti
a filtr podle vlastnika. Skript je idempotentni - da se pustit znovu.

Pouziti:
    python vlastnici-bolesti.py            # zapise
    python vlastnici-bolesti.py --nahled   # jen vypise, nezapisuje

POZOR: Airtable tu nema API klic (jde jen pres MCP konektor v Claude Code),
takze vazby se nedaji stahnout automaticky. vlastnici-bolesti.json JE ten zaznam;
kdyz se v Airtable neco zmeni, musi se rucne dopsat tam.
"""
import argparse
import io
import json
import os
import re
import shutil
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.join(os.path.expanduser('~'), 'salutem-ai-hub', 'prioritizacni-mapa.html')
M = json.load(open(os.path.join(HERE, 'vlastnici-bolesti.json'), encoding='utf-8'))

SH = M['stakeholders']
PAIN = M['pain_stakeholder']
PAIN_KEY = M['pain_stakeholder_key']
ROLE_OK = M['role_na_cloveka']
ROLE_NO = M['role_bez_cloveka']
ALFA = M['alfa_vlastnik']


def vlastnik_bolesti(b):
    """Vraci (jmeno, role, zdroj). Poradi je zamerne: klic pred Pain ID,
    protoze Pain ID neni unikatni (P-098 sedmkrat)."""
    key = b.get('key') or ''
    pid = b.get('pain_id') or ''

    # 1. dolozeny: clovek to sam vyslovil v rozhovoru
    sid = PAIN_KEY.get(key)
    if sid is None:
        sid = PAIN.get(key) or PAIN.get(pid)
    if sid:
        s = SH.get(sid)
        if s:
            return s['jmeno'], s['role'], 'dolozeny'

    # 2. bolesti z Alfy: vlastnik z role, kterou jmenuje rozbor
    role = ALFA.get(key)
    if role:
        sid2 = ROLE_OK.get(role)
        if sid2:
            s = SH[sid2]
            return s['jmeno'], s['role'], 'pravdepodobny'
        if role in ROLE_NO:
            return '', role, 'role'
        return '', role, 'role'

    return '', '', 'nedohledano'


def obohat(B):
    zmen = 0
    for b in B:
        jm, role, zdroj = vlastnik_bolesti(b)
        if (b.get('vlastnik'), b.get('vlastnik_role'), b.get('vlastnik_zdroj')) != (jm, role, zdroj):
            zmen += 1
        b['vlastnik'] = jm
        b['vlastnik_role'] = role
        b['vlastnik_zdroj'] = zdroj
    return zmen


# ------------------------------------------------------------------ uprava stranky
# Pozor: kratsi varianta hlavicky je i v shortTable() v JS, proto je v kotve i Dopad.
TH_OLD = ('<th>ID</th><th>Bolest</th><th class="num">h/týd</th>'
          '<th class="num">Dopad</th>')
TH_NEW = ('<th>ID</th><th>Bolest</th><th>Vlastník</th><th class="num">h/týd</th>'
          '<th class="num">Dopad</th>')

TD_OLD = """                  + '<td class="num">' + (r.cas_h_tyden || '—') + '</td>'"""
TD_NEW = """                  + '<td>' + vlTd(r) + '</td>'
                  + '<td class="num">' + (r.cas_h_tyden || '—') + '</td>'"""

COLSPAN_OLD = '<tr class="pm-detail" hidden><td colspan="10">'
COLSPAN_NEW = '<tr class="pm-detail" hidden><td colspan="11">'

BLOB_OLD = """                    var blob = [r.key, r.nazev, r.popis, r.dg, DGNAME[r.dg], r.slabe, r.zasah, r.note,
                        (r.systemy || []).join(' ')].join(' ').toLowerCase();"""
BLOB_NEW = """                    var blob = [r.key, r.nazev, r.popis, r.dg, DGNAME[r.dg], r.slabe, r.zasah, r.note,
                        r.vlastnik, r.vlastnik_role,
                        (r.systemy || []).join(' ')].join(' ').toLowerCase();"""

FILTR_OLD = """                <span class="pm-count" id="f-count"></span>"""
FILTR_NEW = """                <select id="f-vl"><option value="">vlastník: všichni</option></select>
                <span class="pm-count" id="f-count"></span>"""

FILTR_JS_OLD = """                if (fsrc && (r.zdroj_sberu || 'rozhovor') !== fsrc) return false;"""
FILTR_JS_NEW = """                if (fsrc && (r.zdroj_sberu || 'rozhovor') !== fsrc) return false;
                if (fvl) {
                    if (fvl === '__nedohledano' && r.vlastnik_zdroj !== 'nedohledano') return false;
                    if (fvl !== '__nedohledano' && (r.vlastnik || r.vlastnik_role) !== fvl) return false;
                }"""

VAR_OLD = """            var fsrc = document.getElementById('f-src').value;"""
VAR_NEW = """            var fsrc = document.getElementById('f-src').value;
            var fvl = document.getElementById('f-vl').value;"""

HOOK_OLD = """        ['f-q', 'f-dg', 'f-ai', 'f-z', 'f-l', 'f-src'].forEach(function (id) {"""
HOOK_NEW = """        ['f-q', 'f-dg', 'f-ai', 'f-z', 'f-l', 'f-src', 'f-vl'].forEach(function (id) {"""

# vlTd + naplneni roletky vlastniku. Vklada se pred funkci render().
POMOCNE = """        // ---- Vlastník bolesti ----
        var VLZ = {
            dolozeny: ['vl-dolozeny', 'řekl to sám'],
            pravdepodobny: ['vl-pravdepodobny', 'pravděpodobný'],
            role: ['vl-role', 'jen role'],
            nedohledano: ['vl-nedohledano', 'nedohledáno']
        };
        function vlTd(r) {
            var z = VLZ[r.vlastnik_zdroj] || VLZ.nedohledano;
            if (r.vlastnik) {
                return '<strong>' + esc(r.vlastnik) + '</strong>'
                     + '<span class="vl-sub">' + esc(r.vlastnik_role || '') + '</span>'
                     + '<span class="vl ' + z[0] + '">' + z[1] + '</span>';
            }
            if (r.vlastnik_role) {
                return '<em>' + esc(r.vlastnik_role) + '</em>'
                     + '<span class="vl ' + z[0] + '">' + z[1] + '</span>';
            }
            return '<span class="vl vl-nedohledano">nedohledáno</span>';
        }
        (function () {
            var sel = document.getElementById('f-vl');
            var jm = {};
            B.forEach(function (r) {
                var k = r.vlastnik || r.vlastnik_role;
                if (k) { jm[k] = (jm[k] || 0) + 1; }
            });
            Object.keys(jm).sort(function (a, b) { return a.localeCompare(b, 'cs'); })
                .forEach(function (k) {
                    var o = document.createElement('option');
                    o.value = k; o.textContent = k + ' (' + jm[k] + ')';
                    sel.appendChild(o);
                });
            var bez = B.filter(function (r) { return r.vlastnik_zdroj === 'nedohledano'; }).length;
            if (bez) {
                var o2 = document.createElement('option');
                o2.value = '__nedohledano'; o2.textContent = 'nedohledáno (' + bez + ')';
                sel.appendChild(o2);
            }
        })();

"""

CSS = """        .vl { display: inline-block; margin-top: 4px; padding: 1px 7px; border-radius: 20px;
            font-size: .7rem; font-weight: 600; white-space: nowrap; }
        .vl-dolozeny { background: #DCFCE7; color: #166534; }
        .vl-pravdepodobny { background: #FEF3C7; color: #92400E; }
        .vl-role { background: #E0E7FF; color: #3730A3; }
        .vl-nedohledano { background: var(--gray-200); color: var(--gray-600); }
        .vl-sub { display: block; font-size: .76rem; color: var(--gray-500); line-height: 1.4; }
"""

LEAD_OLD = ('Sloupec <strong>Zdroj</strong> říká, ze kterého sběru bolest je: '
            '<span class="tag tag-src-rozhovor">rozhovor</span> nebo '
            '<span class="tag tag-src-alfa">popis kroku</span>.')
LEAD_NEW = (LEAD_OLD + ' Sloupec <strong>Vlastník</strong> je business vlastník: '
            '<span class="vl vl-dolozeny">řekl to sám</span> člověk, který tu bolest '
            'vyslovil v rozhovoru · <span class="vl vl-pravdepodobny">pravděpodobný</span> '
            'odvozeno z role, která to má rozhodnout, a ta role patří jednomu člověku · '
            '<span class="vl vl-role">jen role</span> roli v bázi neodpovídá právě jeden '
            'člověk, takže vlastníkem je role, ne jméno.')


def uprav_stranku(h):
    zmeny = []

    def swap(old, new, co, kolik=1):
        nonlocal h
        if new in h and old not in h:
            return                                  # uz vlozeno
        assert h.count(old) == kolik, '%s: cekal jsem %dx, naslo %dx' % (co, kolik, h.count(old))
        h = h.replace(old, new)
        zmeny.append(co)

    swap(TH_OLD, TH_NEW, 'hlavicka sloupce Vlastnik')
    swap(TD_OLD, TD_NEW, 'bunka Vlastnik v radku')
    swap(COLSPAN_OLD, COLSPAN_NEW, 'colspan detailu 10 -> 11')
    swap(BLOB_OLD, BLOB_NEW, 'vlastnik do fulltextu')
    swap(FILTR_OLD, FILTR_NEW, 'roletka filtru vlastnika')
    swap(FILTR_JS_OLD, FILTR_JS_NEW, 'filtrovani podle vlastnika')
    swap(VAR_OLD, VAR_NEW, 'promenna fvl')
    swap(HOOK_OLD, HOOK_NEW, 'napojeni f-vl na render')
    swap(LEAD_OLD, LEAD_NEW, 'vysvetleni sloupce v uvodu tabulky')

    if 'function vlTd(r)' not in h:
        anchor = '        function render() {'
        assert h.count(anchor) == 1, 'kotva render()'
        h = h.replace(anchor, POMOCNE + anchor)
        zmeny.append('funkce vlTd + naplneni roletky')

    if '.vl-dolozeny' not in h:
        i = h.rindex('    </style>')
        h = h[:i] + CSS + h[i:]
        zmeny.append('styly pro vlastnika')

    return h, zmeny


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nahled', action='store_true')
    a = ap.parse_args()

    h = open(HUB, encoding='utf-8').read()
    m = re.search(r'(<script id="pm-data" type="application/json">)(.*?)(</script>)', h, re.S)
    data = json.loads(m.group(2))
    B = data['bolesti']

    zmen = obohat(B)
    poc = Counter(b['vlastnik_zdroj'] for b in B)
    print('bolesti: %d | zmeneno: %d' % (len(B), zmen))
    print('\nODKUD JE VLASTNIK')
    for k in ('dolozeny', 'pravdepodobny', 'role', 'nedohledano'):
        print('  %-16s %3d' % (k, poc.get(k, 0)))

    print('\nKDO KOLIK BOLESTI VYSLOVIL (dolozeni)')
    for jm, n in Counter(b['vlastnik'] for b in B if b['vlastnik_zdroj'] == 'dolozeny').most_common():
        hod = sum((b.get('cas_h_tyden') or 0) for b in B
                  if b['vlastnik'] == jm and b['vlastnik_zdroj'] == 'dolozeny')
        print('  %-22s %3d bolesti  %3d h/tyden' % (jm, n, hod))

    print('\nVLASTNIK JE ROLE, NE JMENO')
    for role, n in Counter(b['vlastnik_role'] for b in B if b['vlastnik_zdroj'] == 'role').most_common():
        print('  %-30s %d  (%s)' % (role, n, ROLE_NO.get(role, '')[:60]))

    nedo = [b for b in B if b['vlastnik_zdroj'] == 'nedohledano']
    if nedo:
        print('\nNEDOHLEDANO')
        for b in nedo:
            print('  %-12s %s' % (b.get('key'), b.get('nazev', '')[:64]))

    # kontroly
    chyby = []
    if not all(b.get('vlastnik_zdroj') for b in B):
        chyby.append('nekde chybi vlastnik_zdroj')
    neznamy = [s for s in list(PAIN.values()) + list(PAIN_KEY.values()) if s and s not in SH]
    if neznamy:
        chyby.append('neznamy stakeholder: ' + ', '.join(sorted(set(neznamy))))
    nepouzity = sorted(set(PAIN) - set(b.get('pain_id') or '' for b in B)
                       - set(b.get('key') or '' for b in B))
    if nepouzity:
        print('\nPozn.: v mapovani je %d Pain ID, ktera v prioritizacni mape nejsou: %s'
              % (len(nepouzity), ', '.join(nepouzity)))
    print('\nKONTROLA:', 'OK' if not chyby else 'NESEDI - ' + '; '.join(chyby))
    if chyby:
        return 1

    if a.nahled:
        print('\n--nahled: do stranky se nezapisovalo')
        return 0

    novy_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    h = h[:m.start(2)] + novy_json + h[m.end(2):]
    h, zmeny = uprav_stranku(h)
    shutil.copyfile(HUB, HUB + '.bak')
    open(HUB, 'w', encoding='utf-8', newline='').write(h)
    print('\nzapsano do', os.path.basename(HUB))
    for z in zmeny:
        print('  +', z)
    if not zmeny:
        print('  (struktura stranky uz byla hotova, aktualizovala se jen data)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
