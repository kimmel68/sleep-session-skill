# -*- coding: utf-8 -*-
"""Werkzeug der Schlaf-Sitzung: das dateibasierte Gedaechtnis pruefen und Ersetztes archivieren. Nur Standardbibliothek.

    python gedaechtnis.py inventar <memory-ordner> [--json]     Befund: Index, Dateien, Verweise, Kopf, offene Urteile
    python gedaechtnis.py archiv <memory-ordner> <datei.md> --grund "<warum>"   nach _archiv/<datum>_<datei>, Index-Zeile raus

Nichts wird geloescht. Das Archiv liegt im Gedaechtnisordner unter _archiv/ (wird nicht geladen, bleibt umkehrbar).
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys

INDEX = 'MEMORY.md'
ZEILE_MAX = 150                 # Zeichen je Index-Zeile; darueber gehoert der Inhalt in die Datei
OFFEN = re.compile(r'(Urteil (steht )?aus|steht aus|Urteil offen|noch nicht geh[oö]rt)', re.I)


def lesen(pfad):
    with open(pfad, encoding='utf-8-sig') as f:
        return f.read()


def kopf(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return None, text
    felder = {}
    for zeile in m.group(1).splitlines():
        if ':' in zeile and not zeile.startswith(' '):
            k, _, v = zeile.partition(':')
            felder[k.strip()] = v.strip()
    typ = re.search(r'^\s+type:\s*(\S+)', m.group(1), re.M)
    if typ:
        felder['type'] = typ.group(1)
    return felder, text[m.end():]


def inventar(ordner):
    idx_pfad = os.path.join(ordner, INDEX)
    idx = lesen(idx_pfad) if os.path.exists(idx_pfad) else ''
    eintraege = re.findall(r'^- \[([^\]]+)\]\(([^)]+)\)(.*)$', idx, re.M)
    im_index = {d for _, d, _ in eintraege}
    dateien = sorted(f for f in os.listdir(ordner) if f.endswith('.md') and f != INDEX)
    namen, befund = {}, {'dateien': len(dateien), 'index_zeilen': len(eintraege), 'index_zeichen': len(idx)}
    lang = [(d, len('- [%s](%s)%s' % (t, d, r))) for t, d, r in eintraege if len('- [%s](%s)%s' % (t, d, r)) > ZEILE_MAX]
    befund['index_zu_lang'] = sorted(lang, key=lambda x: -x[1])
    befund['index_ohne_datei'] = sorted(d for d in im_index if not os.path.exists(os.path.join(ordner, d)))
    befund['datei_ohne_index'] = [d for d in dateien if d not in im_index]
    ohne_kopf, offen, groesse, links = [], [], {}, {}
    for d in dateien:
        t = lesen(os.path.join(ordner, d))
        k, rumpf = kopf(t)
        groesse[d] = len(t)
        if not k or not k.get('name') or not k.get('description') or not k.get('type'):
            ohne_kopf.append(d)
        else:
            namen[k['name']] = d
        if OFFEN.search(t):
            offen.append(d)
        links[d] = set(re.findall(r'\[\[([^\]]+)\]\]', rumpf))
    befund['ohne_vollen_kopf'] = ohne_kopf
    befund['offene_urteile'] = offen
    befund['tote_verweise'] = sorted({(d, l) for d, ls in links.items() for l in ls if l not in namen})
    befund['groesste'] = sorted(groesse.items(), key=lambda x: -x[1])[:8]
    befund['typen'] = {}
    for d in dateien:
        k, _ = kopf(lesen(os.path.join(ordner, d)))
        typ = (k or {}).get('type', '?')
        befund['typen'][typ] = befund['typen'].get(typ, 0) + 1
    return befund


def archiv(ordner, datei, grund):
    quelle = os.path.join(ordner, datei)
    if not os.path.exists(quelle):
        sys.exit('fehlt: %s' % quelle)
    ziel_dir = os.path.join(ordner, '_archiv')
    os.makedirs(ziel_dir, exist_ok=True)
    ziel = os.path.join(ziel_dir, '%s_%s' % (datetime.date.today().isoformat(), datei))
    shutil.move(quelle, ziel)
    with open(os.path.join(ziel_dir, 'ARCHIV.md'), 'a', encoding='utf-8') as f:
        f.write('- %s %s: %s\n' % (datetime.date.today().isoformat(), datei, grund))
    idx_pfad = os.path.join(ordner, INDEX)
    idx = lesen(idx_pfad)
    neu = '\n'.join(z for z in idx.splitlines() if '](%s)' % datei not in z) + '\n'
    with open(idx_pfad, 'w', encoding='utf-8') as f:
        f.write(neu)
    print('archiviert: %s -> %s' % (datei, ziel))


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    a = argparse.ArgumentParser()
    u = a.add_subparsers(dest='befehl', required=True)
    i = u.add_parser('inventar')
    i.add_argument('ordner')
    i.add_argument('--json', action='store_true')
    r = u.add_parser('archiv')
    r.add_argument('ordner')
    r.add_argument('datei')
    r.add_argument('--grund', required=True)
    o = a.parse_args()
    if o.befehl == 'archiv':
        return archiv(o.ordner, o.datei, o.grund)
    b = inventar(o.ordner)
    if o.json:
        print(json.dumps(b, ensure_ascii=False, indent=1, default=list))
        return
    print('Dateien %d, Index-Zeilen %d (%d Zeichen), Typen %s' % (b['dateien'], b['index_zeilen'], b['index_zeichen'], b['typen']))
    for k in ('index_zu_lang', 'index_ohne_datei', 'datei_ohne_index', 'ohne_vollen_kopf', 'tote_verweise', 'offene_urteile'):
        print('%s (%d): %s' % (k, len(b[k]), ', '.join(str(x) for x in b[k][:12]) + (' ...' if len(b[k]) > 12 else '')))


if __name__ == '__main__':
    main()
