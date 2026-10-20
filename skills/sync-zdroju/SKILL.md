---
name: sync-zdroju
description: Použij tento skill VŽDY na začátku práce se second brainem a vždy, když se řeší „co je nového", „přibylo něco", „aktualizace znalostí", „doplnit second brain", „projít Alfu". Skill říká, JAK zjistit, co ve firemních zdrojích přibylo od posledního syncu, jak to vytěžit a co se do second brainu naopak nikdy nepřenáší. Spouštěj ho i sám od sebe — na začátku každé delší práce se second brainem a na konci session, kdy se zapisuje, co je vytěžené.
---

# Sync zdrojů — pravidelné dobírání nových podkladů

Second brain nemá největší hodnotu v tom, co v něm je. Má ji v tom,
**že nezaostává za realitou**. Zdroje ve firmě vznikají každý den:
projektové složky, přepisy hovorů, směrnice, vzory. Když se nedobírají,
báze se za měsíc změní z „mapy firmy" na „mapu firmy k srpnu".

> **Pravidlo:** ptej se na nové zdroje sám. Nečekej, až to někdo zadá.

## Kdy se to dělá

| Kdy | Co udělat |
|---|---|
| **Začátek delší práce se second brainem** | Spusť sync a nabídni, co je nového. Jednou větou, ne seznamem na obrazovku. |
| **Konec session, kdy se něco vytěžilo** | Zapiš stav (`--commit`) a doplň logy. |
| **Uživatel se zmíní o novém zdroji** | Přidej ho do konfigurace hlídaných zdrojů. |
| Uprostřed práce | Nespouštěj. Přerušuje to. |

## Jak zjistit, co je nového

```
cd C:\Users\habova\salutem-group-second-brain\skripty
python sync-zdroju.py                 # co pribylo od posledniho syncu
python sync-zdroju.py --root Alfa     # jen jeden zdroj
python sync-zdroju.py --dny 14        # rucne, bez ohledu na stav
python sync-zdroju.py --commit        # az kdyz je to VYTEZENE
```

Skript **nic nemění a nic nemaže.** Stav (datum posledního syncu a počet
souborů na zdroj) drží v `sync-zdroju.stav.json`. Hlídané zdroje jsou
v `sync-zdroju.config.json` — cesty se tam upravují, ne ve skriptu.

> 🔴 **Nejdůležitější pravidlo: `--commit` znamená „roztříděno", ne
> „vytěženo".** Commit řekne „tyhle soubory jsem viděl" — a od té chvíle je
> sync **už nikdy nepřipomene.** Takže se smí spustit **jen u zdroje, kde
> je každý vypsaný soubor rozhodnutý** (vytěžit / pracovní soubor / vědomě
> nechat) **a to rozhodnutí je zapsané v logu.**
>
> Když je roztříděný jen jeden zdroj, commitni **jen jeho**:
> `python sync-zdroju.py --root Alfa --commit`. Zdroj, na který jsi ještě
> nekoukl, nechej bez commitu — jinak z něj tiše zmizí desítky souborů,
> které nikdo neviděl.
>
> Doložený omyl (11. 8. 2026): commit proběhl přes všechny zdroje najednou
> a označil tím za viděných 1 162 souborů ve SReal a IT Governance, které
> nikdo neotevřel. Řešení: ty zdroje se ze stavu zase odebraly.

**Klesající počet souborů skript nahlásí** („něco zmizelo") — to je signál
k ručnímu pohledu, ne k panice; nejčastěji jde o přejmenování.

> ⚠️ **U nově přidaného zdroje je při prvním běhu „nové" všechno.** Nečti to
> — jen zkontroluj, že cesta míří na správnou složku, spusť `--commit`
> a od druhého běhu už uvidíš jen skutečné změny.

**Když zdroj hlásí přes 200 změn**, skript upozorní, že je zabraný moc
široko. **Nikdy nehlídej klientské složky ani zálohy** — jsou to tisíce
souborů a osobní data. Co se vědomě nehlídá, je vypsané v konfiguraci
v sekci `_nehlidat` (a je tam i důvod).

**Zúžení zdroje se dělá dvěma způsoby:** buď se v konfiguraci upraví `cesta`,
nebo se u zdroje vypíše `"ignorovat": ["Podslozka"]` — seznam relativních
prefixů, které se do zdroje nepočítají. Použij `ignorovat` tam, kde ve
sledované složce leží **osobní data nebo právní dokumenty** vedle znalosti,
a napiš důvod do `_nehlidat`.

> 🔴 **Past, na kterou se snadno narazí: přesun souboru do hlídané složky
> ho neudělá „novým".** Sync porovnává **mtime** a přesun mtime zachovává —
> takže dokument z května přesunutý dnes do `podklady` **se ve výpisu
> neobjeví**. Doloženo 13. 8. 2026 při úklidu kořene `AI - Dokumenty`,
> odkud se do archivu přesunulo šest zdrojů.
>
> Neujde to úplně: **počet souborů se změní** a skript to na dalším běhu
> nahlásí (`pocet souboru: +3 proti poslednimu syncu`). Je to ale jen
> signál, že se něco stalo — **který soubor to byl, ti nikdo neřekne.**
>
> **Pravidlo:** co sám přesuneš do hlídané složky, **zapiš rovnou do logu**
> (`_prehled.md`) jako `⬜`, včetně toho, co v tom čeká. Na sync se
> u přesunů nespoléhej — hlídá přírůstky, ne přesuny.

> 🔴 **Druhá past, doložená 8. 9. 2026: soubory s cestou nad ~260 znaků byly
> pro sync neviditelné.** Windows na nich vrátí z `os.stat` chybu a skript ji
> polykal v `except OSError: continue`. V Alfě se tak **tiše přeskakovalo
> 33 souborů**, mezi nimi popisy procesních kroků 017, 025, 055 a 081 — tedy
> ten nejcennější zdroj, jaký ve firmě je. Nešlo to poznat: počet souborů byl
> konzistentně o 33 menší a nový soubor s dlouhou cestou se ve výpisu **nikdy
> neobjevil**.
>
> Opraveno prefixem `\\?\` a tím, že se nečitelný soubor **vypíše** místo
> přeskočení. Kdyby se ve výpisu objevila řádka `!! nelze precist`, není to
> kosmetika — je to soubor, o kterém nikdo neví.
>
> **Obecné pravidlo:** hlídač, který vrátí méně a nic neřekne, je horší než
> hlídač, který spadne. Totéž byl nález ze 13. 8. o rekurzivním hledání, které
> minulo celou knihovnu `Salutem - Dokumenty`.

> 🔴 **Čtvrtá past, doložená 9. 9. 2026: sync hlídá přírůstky, ne úplnost.**
> Soubor, který se nikdy nezměnil, se ve výpisu neobjeví **nikdy** — a to
> není chyba, to je definice. Devět synců od 11. 8. proto devětkrát minulo
> celou složku `12 AI Roadmapa`, protože je ze 16. 6. 2026 a od té doby ji
> nikdo neupravil. Ležel v ní souhrnný service dokument s dvanácti use-casy
> za 2,5 milionu ročně, definice tří větví služby a tři otevřená compliance
> rozhodnutí se jmenovitými vlastníky. Vedle toho `Řídící principy.docx`
> projektu 17 (1. 7. 2026), který zavíral otázku otevřenou od 18. 8.,
> a **FAQ produktu se 43 odpověďmi**, o kterém báze měsíc psala „nevyužitý
> poklad", aniž ho někdo otevřel.
>
> **Pravidlo:** raz za kvartál projít hlídaný zdroj **celý, soubor po
> souboru** — `python inventura.py --slozky` (sloupec „posledni zmena" na
> první pohled ukáže složky, které stojí od června) a pak `inventura.py`
> bez parametrů proti logu vytěžení. Nový soubor je vidět v syncu; **starý
> soubor, který nikdo nečetl, je vidět jen v inventuře.**

> 🔴 **Třetí past: kořen `AI - Dokumenty` sync nehlídá.** Dokument položený do
> kořene se ve výpisu neobjeví nikdy — a co není zařazené, to pro bázi
> neexistuje. Doloženo 8. 9. 2026: předání katastrálního agenta leželo
> v kořeni od 31. 8. se šesti ověřenými kódy operací ČÚZK, a **4. 9. se do
> báze zapsalo, že ty kódy chybí.** Proto se na začátku každého syncu
> **podívej do kořene báze** (`ls` stačí) a co tam leží, zařaď týž den.
> Zařazení a vytěžení jsou dvě různé věci; to první stojí pět minut.

Aktuálně hlídané: **Alfa · zbytek `01 SG/Projekty` mimo Alfu (přidáno
9. 9. 2026) · přepisy · podklady · SReal (manuály a Sales) ·
IT Governance (AI, evidence softwaru, návody)**. Stav k 13. 8. 2026:
~1 000 souborů po zúžení dvou nejširších zdrojů (SReal Sales 296 → 42
bez vzorů smluv, IT Governance evidence 626 → 11 bez karet majetku lidí).

## Jak to interpretovat — tři koše

Ne všechno, co přibylo, se vytěžuje. Roztřiď to **než začneš čít**:

| Koš | Co to je | Co s tím |
|---|---|---|
| **Znalost** | hotový výstup, směrnice, popis procesu, akceptace, poučení, přepis rozhovoru | **vytěžit** |
| **Pracovní soubor** | zálohy dat, exporty, analýzy podílníků, rozpracované tabulky, nahrávky | **nevytěžovat**, jen zaznamenat, že existují |
| **Stav** | kdo co stihl, termíny, kdo byl na školení, počty hodin | **nikdy nepřenášet** — to žije ve Freelu |

Rychlý test: *„Kdyby autor odešel z firmy, ztratíme tím něco, co se nedá
znovu vyrobit?"* Když ano, je to znalost.

> 🔴 **Koš se nedá určit z názvu a cesty. Doloženo 9. 9. 2026.**
> `14 VBR úroky - Pohoda/20 Etapa 3 - Příprava/Příprava testování.docx`
> šel osm syncu do koše „stav projektu", protože tak zní. **Uvnitř je
> testovací strategie CML a konektoru do POHODY** — pět úrovní testů
> u dvou aplikací, které si firma staví, konkrétní příkazy a tři přiznané
> mezery. Nemá to s úroky nic společného.
>
> **Pravidlo:** u dokumentu, který má aspoň deset stran, se otevírá obsah,
> ne jen název. Trojice koší se přiřazuje po pohledu dovnitř.

> 🔴 **A druhá věc: „odškrtnuto" není „přečteno".** U dlouhého dokumentu se
> snadno vytěží ta část, která odpovídá na otázku, se kterou ho člověk
> otevřel, a zbytek zůstane ležet. Doloženo na metodice podpisového procesu
> (projekt 57): vzala se z ní **pravidla pořadí podpisů**, ale rozdělení
> odpovědností po třech rolích, pětibodová kontrola po podpisu klienta
> a hranice „co právní nepřipravuje" v bázi měsíc nebyly — přestože log
> projekt vedl jako vytěžený.
>
> **Pravidlo:** po vytěžení dlouhého dokumentu projdi jeho osnovu a odškrtni
> si kapitolu po kapitole, co z ní v záznamu je. Skript `osnova.py`
> (nadpisy podle stylu + zkrácené odstavce + hlavičky tabulek) na to stačí.

## Co se do second brainu nikdy nepřenáší

1. **Stavy a termíny projektů.** Freelo = co se právě děje. SharePoint = co jsme se naučili.
2. **Jmenná evidence lidí** — účast na školení, odpracované hodiny, plnění termínů. Agreguj („zapojeno ~29 lidí ve dvou rolích"), nejmenuj.
3. **Mezilidské citlivosti.** Postoj člověka k AI se zapisuje, „kdo je na koho naštvaný" ne. Píšeme tak, aby to snesl i ten, o kom to je.
4. **Osobní a klientská data.** Rodná čísla, ceny konkrétních případů, obsah smluv jednotlivých klientů.

## Kam se zapisuje, že je něco vytěžené

Bez logu se za měsíc čte totéž znovu. **Log je součást práce, ne úklid po ní.**

| Zdroj | Kam se zapisuje stav vytěžení |
|---|---|
| Přepisy hovorů | `99 Archiv zdrojů/prepisy/_prehled.md` — tabulka se značkami ✅ 🟡 ⬜ a odkazem, kam to šlo |
| Podklady | `99 Archiv zdrojů/podklady/_prehled.md` |
| Projekty Alfa | `02 Use casy/alfa-prehled-projektu.md` — rozcestník, ne kopie |
| Ostatní | do `zdroj:` v hlavičce záznamu, který z toho vznikl |

Do každého záznamu patří **`zdroj:`** s cestou a datem dokumentu. Bez toho
se za rok nedá ověřit, odkud číslo pochází.

## Jak vytěžovat efektivně

- **Nejdřív triáž, pak čtení.** Ze seznamu vyber to, co je znalost. U 20 souborů to bývá 5.
- **Velké dokumenty čti s otázkou**, ne od začátku. („Co z toho mění zadání? Co odpovídá na otevřenou otázku?")
- **Hledej odpovědi na „Co zatím nevíme"** v existujících záznamech. Nový zdroj často zavírá starou otázku — a to je cennější než nový záznam.
- **Doplňuj do existujících souborů**, když téma už existuje. Nový soubor zakládej, jen když jde o nové téma.
- **Nikdy nepřepisuj starý text** — připiš revizi s datem a důvodem (viz `prace-na-use-casu`).
- **Zkomolené přepisy označ.** Automatické přepisy z Teams mají chyby ve jménech, číslech i názvech nástrojů. Nikdy z nich neciteuj číslo ani jméno bez ověření jinde — a do textu napiš `⚠️ neověřeno`.
- **PDF bez textové vrstvy se čte přes render do PNG, ne přes OCR.** Když `pypdf` vrátí u čtyřstránkového dokumentu tři znaky, není to nutně sken — tisk z Microsoft Loopu nebo z webu vypadá stejně. Vyrenderuj stránky (`pymupdf`: `page.get_pixmap(dpi=170).save("s1.png")`) a přečti obrázek. Doloženo 8. 9. 2026 na `zapis_standup_ai_automatizace10_8.pdf`, který od 13. 8. ležel odepsaný jako „PDF agenti nepřečtou, chybí poppler". Poppler s tím nemá co dělat.
- **AI souhrny ze schůzek mají vlastní varování a platí pro ně stejné pravidlo jako pro zkomolené přepisy.** Poznámky z Microsoft Loopu nesou v hlavičce „Obsah v poznámkách generovaný pomocí AI může být nesprávný" a názvy nástrojů v nich bývají zkomolené („Clode AI" = Claude). Berou se jako doklad, že věc padla, ne jako citace.

## Jak o tom mluvit s uživatelem

Krátce a s návrhem, ne se seznamem:

> „Od posledního syncu přibylo 19 souborů, z toho vytěžit bych doporučil dva:
> popsané procesní kroky a specifikaci VBR úroků. Zbytek jsou zálohy dat.
> Mám se do toho pustit?"

Když je nového hodně, **navrhni pořadí podle hodnoty**, ne podle abecedy.
Když nepřibylo nic podstatného, řekni to jednou větou a pokračuj v práci.

## Konec session

1. Zapiš logy (viz tabulka výše)
2. `python sync-zdroju.py --commit` — až když je to opravdu vytěžené
3. Ve zprávě uživateli uveď, **co zbývá** a v jakém pořadí

## Proč to vzniklo

11. 8. 2026 se dobral celý archiv přepisů — 24 zdrojů, ~14 nových záznamů.
Při kontrole projektové složky Alfa se ukázalo, že **za pět dní od
předchozího průchodu přibylo 11 souborů a dva nové projekty**, a jeden
z přírůstků (popsané procesní kroky) byl nejcennější podklad
k automatizaci, jaký ve firmě je: ukázal, že **51 % kroků obchodního
procesu jsou transfery** a že e-mail je systémem 66 kroků ze 150, zatímco
CRM pěti.

Bez pravidelného syncu by se to našlo náhodou, nebo vůbec.
