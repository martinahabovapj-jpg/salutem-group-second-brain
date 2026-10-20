#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Krok 1 / Test 1A - rozhodovaci test Raynet API.

Zjistuje jedinou vec: umi Raynet API zalozit ROZEPSANY e-mail (status NEW)
navazany na obchodni pripad, ktery obchodnik otevre v modulu Posta?

Pouziva jen standardni knihovnu Pythonu 3.8+. Nic se neinstaluje.

POUZITI (PowerShell)
--------------------
  $env:RAYNET_LOGIN  = "martina.habova@pj-capital.cz"
  $env:RAYNET_API_KEY = "..."            # Raynet -> profil uzivatele -> API klic
  # $env:RAYNET_INSTANCE = "salutem"     # nepovinne, vychozi je salutem

  python raynet-krok1-test-konceptu.py probe
  python raynet-krok1-test-konceptu.py op --kod OP-26-4342
  python raynet-krok1-test-konceptu.py najdi --email jan.novak@firma.cz
  python raynet-krok1-test-konceptu.py pripady --firma 12345
  python raynet-krok1-test-konceptu.py koncept --pripad 6789 --prijemce ja@firma.cz --dry-run
  python raynet-krok1-test-konceptu.py koncept --pripad 6789 --prijemce ja@firma.cz

BEZPECNOST
----------
  * Jako --prijemce zadavej VYHRADNE vlastni adresu. Nikdy realneho klienta.
  * Pouzij testovaci obchodni pripad, ne zivy case.
  * Nejdriv spust s --dry-run a podivej se, co by se poslalo.
  * probe / najdi / pripady jsou jen cteni. Zapisuje pouze prikaz koncept.

VYSTUP
------
  Vse se loguje do krok1-vysledky.json - ten soubor je vysledek testu,
  posli ho zpatky k vyhodnoceni.

POZNAMKA K NEJISTOTE
--------------------
  Presne nazvy endpointu a poli entity `email` je potreba overit v API
  dokumentaci nasi instance (/api/doc/). Skript je napsany tak, aby ti to
  rekl sam: pri chybe vypise CELE telo odpovedi, ve kterem Raynet obvykle
  uvadi, ktera pole ceka. Podle toho uprav sekci PAYLOAD nize.

HISTORIE OPRAV
--------------
  13. 8. 2026 - opravena API adresa. Puvodni verze (v komentari u Freelo
  podukolu 18190966) mela API_BASE "https://{instance}.raynetcrm.com/api/v2".
  Zivy scenar v Make pouziva "https://app.raynet.cz/api/v2" s hlavickou
  X-Instance-Name: salutem. Puvodni adresa by spadla na spojeni a vypadalo
  by to jako problem s pristupy.
  13. 8. 2026 - opraveno odsazeni. Pri ulozeni skriptu do Freelo komentare
  se na osmi mistech ztratilo odsazeni (telo funkci call, cmd_probe,
  cmd_koncept, main) a skript by skoncil na IndentationError.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

LOG_FILE = "krok1-vysledky.json"
_log = []

# ---------------------------------------------------------------------------
# KONFIGURACE - tady se upravuje, kdyz API odmitne payload
# ---------------------------------------------------------------------------

# Overeno 10. 8. 2026 proti zivemu scenari v Make. Instance se predava
# hlavickou X-Instance-Name, ne v adrese.
API_BASE = "https://app.raynet.cz/api/v2"
DEFAULT_INSTANCE = "salutem"

# Entity, ktere probe zkusi. Ktera vrati 200, ta existuje.
ENTITY_CANDIDATES = [
    "company",
    "person",
    "businessCase",
    "activity",
    "email",
    "emailMessage",
    "task",
]

# Kandidati na nazev pole s vazbou na obchodni pripad.
# Pokud API odmitne prvni, zkus dalsi (skript je vyzkousi poporade).
CASE_FIELD_CANDIDATES = ["businessCase", "businessCaseId", "case", "relatedBusinessCase"]

# Kandidati na nazev pole s prijemcem.
TO_FIELD_CANDIDATES = ["to", "toAddress", "recipient", "emailTo"]


def build_payload(pripad_id, prijemce, predmet, telo, case_field, to_field, vlastnik=None):
    """Sestavi telo requestu pro zalozeni e-mailu."""
    payload = {
        "status": "NEW",
        "title": predmet,
        "description": telo,
        to_field: prijemce,
        case_field: int(pripad_id),
    }
    if vlastnik:
        payload["owner"] = int(vlastnik)
    return payload


# ---------------------------------------------------------------------------
# HTTP vrstva
# ---------------------------------------------------------------------------

def _cfg():
    instance = os.environ.get("RAYNET_INSTANCE") or DEFAULT_INSTANCE
    login = os.environ.get("RAYNET_LOGIN")
    key = os.environ.get("RAYNET_API_KEY")
    missing = [n for n, v in (("RAYNET_LOGIN", login), ("RAYNET_API_KEY", key)) if not v]
    if missing:
        sys.exit("Chybi promenne prostredi: " + ", ".join(missing))
    return instance, login, key


def call(method, path, params=None, body=None, quiet=False):
    """Zavola Raynet API. Vraci (status, data). Nikdy nevyhazuje vyjimku na 4xx/5xx."""
    instance, login, key = _cfg()
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)

    token = base64.b64encode("{}:{}".format(login, key).encode("utf-8")).decode("ascii")
    req.add_header("Authorization", "Basic " + token)
    req.add_header("X-Instance-Name", instance)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except Exception as e:  # sit, DNS, timeout
        _record(method, url, body, None, str(e))
        if not quiet:
            print("  CHYBA SPOJENI: {}".format(e))
        return None, None

    try:
        parsed = json.loads(raw)
    except ValueError:
        parsed = raw

    _record(method, url, body, status, parsed)

    if not quiet:
        print("  {} {} -> HTTP {}".format(method, path, status))
        if status >= 400:
            # Toto je nejcennejsi vystup celeho skriptu: validacni chyba
            # obvykle vypise, ktera pole API ceka.
            print("  --- telo odpovedi (precti si ho, rika co API chce) ---")
            print(json.dumps(parsed, ensure_ascii=False, indent=2)[:3000])
            print("  ------------------------------------------------------")

    return status, parsed


def _record(method, url, body, status, response):
    _log.append({
        "cas": datetime.now().isoformat(timespec="seconds"),
        "method": method,
        "url": url,
        "request_body": body,
        "http_status": status,
        "response": response,
    })


def save_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(_log, f, ensure_ascii=False, indent=2)
    print("\nZaznam ulozen do {} ({} volani).".format(LOG_FILE, len(_log)))


# ---------------------------------------------------------------------------
# Kroky testu
# ---------------------------------------------------------------------------

def cmd_probe(args):
    """A0 + A1: overi spojeni a zjisti, ktere entity API zna. Jen cteni."""
    print("\n=== A0: overeni spojeni ===")
    status, _ = call("GET", "/company/", params={"limit": 1})
    if status is None:
        print("\nNedostal jsem se na API vubec. Zkontroluj instanci a sit.")
        return
    if status in (401, 403):
        print("\nAutentizace neprosla. Zkontroluj login a API klic.")
        print("Tip: zkopiruj presne ty hodnoty, ktere pouzivaji existujici Make scenare.")
        return
    if status != 200:
        print("\nCteci volani nevratilo 200. Dal nema smysl pokracovat.")
        return
    print("  Spojeni OK.")

    print("\n=== A1: ktere entity API zna ===")
    found = []
    for entity in ENTITY_CANDIDATES:
        st, _ = call("GET", "/{}/".format(entity), params={"limit": 1}, quiet=True)
        mark = "ANO" if st == 200 else "ne ({})".format(st)
        print("  {:16s} {}".format(entity, mark))
        if st == 200:
            found.append(entity)

    print("\n  Dostupne: {}".format(", ".join(found) if found else "zadne"))
    if "email" not in found and "emailMessage" not in found:
        print("\n  POZOR: endpoint pro e-mail se nenasel pod ocekavanym nazvem.")
        print("  Otevri /api/doc/ na nasi instanci a najdi spravny nazev,")
        print("  pak uprav ENTITY_CANDIDATES a CASE_FIELD_CANDIDATES v tomto skriptu.")


def cmd_najdi(args):
    """Najde kontaktni osobu podle e-mailu a jeji firmu. Jen cteni."""
    print("\n=== Hledani kontaktu podle e-mailu: {} ===".format(args.email))
    # Raynet obvykle podporuje fulltext. Pokud ne, zkusi se filtr na pole.
    status, data = call("GET", "/person/", params={"fulltext": args.email, "limit": 5})
    if status != 200:
        print("  Fulltext neprosel, zkousim filtr na pole contactInfo.email...")
        call("GET", "/person/", params={"contactInfo.email": args.email, "limit": 5})
    else:
        _print_hits(data)


def cmd_pripady(args):
    """Vypise obchodni pripady dane firmy. Jen cteni."""
    print("\n=== Obchodni pripady firmy {} ===".format(args.firma))
    status, data = call("GET", "/businessCase/", params={"company": args.firma, "limit": 50})
    if status == 200:
        _print_hits(data)


def cmd_op(args):
    """Prelozi lidsky kod OP (napr. OP-26-4342) na ciselne ID, nebo naopak. Jen cteni.

    Kod je to, co se zobrazuje uzivateli. API pracuje s ciselnym ID a to je
    to, co potrebuje prikaz `koncept --pripad`. Nejde je z kodu spocitat.

    S --id jde smerem opacnym: precte pripad podle ID a vypise jeho kod.
    Tim se overi, ze cislo z adresniho radku patri opravdu tomu pripadu,
    ktery chceme - dela se to VZDY pred prvnim zapisem.
    """
    if not args.id and not args.kod:
        sys.exit("Zadej bud --kod OP-26-4342, nebo --id 15070.")

    if args.id:
        print("\n=== Overeni obchodniho pripadu id={} ===".format(args.id))
        status, data = call("GET", "/businessCase/{}/".format(args.id))
        if status != 200:
            print("\n  Pripad se necetl. Bud to ID neexistuje, nebo na nej nevidis.")
            print("  ZAPIS NESPOUSTEJ, dokud tohle nevrati 200.")
            return
        rec = data.get("data") if isinstance(data, dict) else None
        if isinstance(rec, list):
            rec = rec[0] if rec else None
        if not isinstance(rec, dict):
            rec = data if isinstance(data, dict) else {}
        print("  nazev: {}".format(rec.get("name") or "(bez nazvu)"))
        print("  kod:   {}".format(rec.get("code") or rec.get("codeNumber") or "(nenasel jsem pole s kodem)"))
        print("  firma: {}".format((rec.get("company") or {}).get("name")
                                   if isinstance(rec.get("company"), dict) else rec.get("company")))
        if args.ocekavany_kod:
            skutecny = rec.get("code") or rec.get("codeNumber")
            if skutecny == args.ocekavany_kod:
                print("\n  *** SEDI. id={} je opravdu {}. Zapis je bezpecny. ***".format(
                    args.id, args.ocekavany_kod))
            else:
                print("\n  *** NESEDI. Cekal jsem {}, API vratilo {}. ***".format(
                    args.ocekavany_kod, skutecny))
                print("  ZAPIS NESPOUSTEJ. Dohledej spravne ID prikazem: op --kod {}".format(
                    args.ocekavany_kod))
        return

    print("\n=== Hledani obchodniho pripadu podle kodu: {} ===".format(args.kod))
    status, data = call("GET", "/businessCase/", params={"fulltext": args.kod, "limit": 20})
    if status == 200 and _print_hits(data):
        return
    print("  Fulltext nic nenasel, zkousim filtr na pole code...")
    status, data = call("GET", "/businessCase/", params={"code": args.kod, "limit": 20})
    if status == 200 and _print_hits(data):
        return
    print("\n  Nenasel jsem to ani jednou cestou. Dve mozne priciny:")
    print("   a) tvuj ucet na ten obchodni pripad nevidi,")
    print("   b) pole s kodem se v API jmenuje jinak nez 'code'.")
    print("  Podivej se v Raynetu do adresniho radku - ciselne ID je v adrese.")


def _print_hits(data):
    """Vypise nalezene zaznamy. Vraci True, kdyz neco naslo."""
    if not isinstance(data, dict):
        return False
    items = data.get("data") or data.get("items") or []
    if not items:
        print("  Nic nenalezeno.")
        return False
    print("  Nalezeno {} zaznamu:".format(len(items)))
    for it in items[:20]:
        if isinstance(it, dict):
            kod = it.get("code") or it.get("codeNumber")
            print("    id={}  {}{}".format(
                it.get("id"),
                it.get("name") or it.get("fullName") or it.get("title") or "",
                "   (kod {})".format(kod) if kod else ""))
    print("\n  Cislo za 'id=' je to, co patri do --pripad.")
    return True


def cmd_koncept(args):
    """A2: pokusi se zalozit rozepsany e-mail. TOHLE ZAPISUJE."""
    stamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    predmet = args.predmet or "TEST KONCEPT - Krok 1 - {}".format(stamp)
    telo = args.telo or (
        "Dobry den,\n\n"
        "dekuji za dnesni call. Posilam slibeny odkaz:\n"
        "https://example.com/test\n\n"
        "S pozdravem"
    )

    print("\n=== A2: zakladam koncept ===")
    print("  Prijemce: {}".format(args.prijemce))
    print("  Pripad:   {}".format(args.pripad))

    if "@" not in args.prijemce:
        sys.exit("  --prijemce nevypada jako e-mail. Zastavuji.")

    # Projde kombinace nazvu poli, dokud neco neprojde.
    for case_field in CASE_FIELD_CANDIDATES:
        for to_field in TO_FIELD_CANDIDATES:
            payload = build_payload(
                args.pripad, args.prijemce, predmet, telo,
                case_field, to_field, args.vlastnik)

            print("\n  --- pokus: vazba='{}', prijemce='{}' ---".format(case_field, to_field))
            print(json.dumps(payload, ensure_ascii=False, indent=2))

            if args.dry_run:
                print("  (dry-run, neposilam)")
                continue

            status, data = call("POST", "/email/", body=payload)
            if status in (200, 201):
                new_id = None
                if isinstance(data, dict):
                    new_id = data.get("id") or (data.get("data") or {}).get("id")
                print("\n  *** ZALOZENO. id = {} ***".format(new_id))
                print("\n  Ted rucne dokonci test:")
                print("   1. Prihlas se jako testovaci obchodnik (NE jako admin).")
                print("   2. Otevri Posta -> Rozepsane.")
                print("   3. Je tam ten zaznam? Jde otevrit v editoru?")
                print("   4. Je predplneny prijemce, predmet a telo vcetne odkazu?")
                print("   5. Je videt vazba na obchodni pripad?")
                print("   6. Jde odeslat?")
                print("\n  Odpovedi zapis do zaznamoveho listu 1A v protokolu.")
                return
            if status == 404:
                print("  Endpoint /email/ neexistuje - spust nejdriv 'probe'.")
                return

    if args.dry_run:
        print("\n  Dry-run hotovy. Spust znovu bez --dry-run.")
    else:
        print("\n  Zadna kombinace poli neprosla.")
        print("  Precti si validacni chyby vyse - rikaji, ktera pole API ceka -")
        print("  a uprav CASE_FIELD_CANDIDATES / TO_FIELD_CANDIDATES v hlavicce skriptu.")
        print("  Kdyby to neslo vubec, je to vysledek: jdeme variantou A.")


# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Krok 1 / Test 1A - rozhodovaci test Raynet API.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("probe", help="A0+A1: overi spojeni a zjisti dostupne entity")

    sp = sub.add_parser("op", help="kod OP -> ciselne ID, nebo s --id overi ID proti kodu")
    sp.add_argument("--kod", help="lidsky kod, napr. OP-26-4342")
    sp.add_argument("--id", help="ciselne ID k overeni (z adresniho radku)")
    sp.add_argument("--ocekavany-kod", dest="ocekavany_kod",
                    help="kod, ktery ma na tom ID sedet - pouziva se s --id")

    sp = sub.add_parser("najdi", help="najde kontakt podle e-mailu")
    sp.add_argument("--email", required=True)

    sp = sub.add_parser("pripady", help="vypise obchodni pripady firmy")
    sp.add_argument("--firma", required=True)

    sp = sub.add_parser("koncept", help="A2: zalozi rozepsany e-mail")
    sp.add_argument("--pripad", required=True, help="ID testovaciho obchodniho pripadu")
    sp.add_argument("--prijemce", required=True, help="VYHRADNE vlastni adresa")
    sp.add_argument("--vlastnik", help="raynet user id testovaciho obchodnika")
    sp.add_argument("--predmet")
    sp.add_argument("--telo")
    sp.add_argument("--dry-run", action="store_true",
                    help="jen vypise, co by poslal")

    args = p.parse_args()
    try:
        {"probe": cmd_probe, "op": cmd_op, "najdi": cmd_najdi,
         "pripady": cmd_pripady, "koncept": cmd_koncept}[args.cmd](args)
    finally:
        save_log()


if __name__ == "__main__":
    main()
