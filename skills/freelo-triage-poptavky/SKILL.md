---
name: freelo-triage-poptavky
description: Použij tento skill VŽDY, když máš vyhodnotit, kvalifikovat nebo posoudit JEDNU NEBO VÍCE poptávek / požadavků / use-casů na AI automatizaci — typicky existující úkoly ve Freelu. Spouštěj ho, když uživatel řekne něco jako "vyhodnoť tuhle poptávku", "projeď triage", "kvalifikuj požadavek", "co s tímhle use-casem", "patří to nám?", "spočítej business case", "jakou dráhou to má jít", ale i "projeď těchhle 5 poptávek", "vyhodnoť backlog", "srovnej tyhle požadavky podle priority" apod. — i když to neřekne přesně takhle. Skill provede poptávku celou kvalifikací podle operačního modelu produkční větve: checklist, devět otázek, compliance brána, ROI výpočet, verdikt dráhy a případná analýza podílníků. Skill určuje JAK vyhodnotit; čtení a zápis do Freela řeší existující skript přes Freelo REST API.
---

# Triage poptávky — od zadání ke kvalifikovanému verdiktu

Tento skill říká, jak vzít **jednu nebo více poptávek** (typicky existující úkoly ve Freelu; obvykle 4–5 najednou, maximálně ~10) a provést každou celou kvalifikací podle dokumentu „Operační model – produkční větev": checklist → devět otázek → compliance brána → business case → verdikt dráhy → (u projektů) analýza podílníků. Výstupem je **triage report ke každé poptávce** — a při více poptávkách navíc **souhrnná prioritizační tabulka** seřazená podle skóre. Po schválení člověkem skončí report u poptávky ve Freelu jako podúkol „Kvalifikace požadavku", který skill sám založí.

Sdílí filozofii se skilly `freelo-projekt-z-prepisu` a `freelo-rozpracovat-ukol-z-prepisu`: věrnost podkladům, lidské názvosloví, transparentní nejasnosti, **nic se nezapisuje bez schválení**.

## Hlavní princip: rádce je brána, ne známkovač

AI tým má tendenci začít poptávku hned řešit, i když chybí informace pro prioritizaci. Tento skill tomu brání:

- **Bez kompletních povinných údajů nevydáváš verdikt.** Místo verdiktu vrátíš seznam „co chybí a koho se zeptat" — konkrétní otázky formulované tak, aby je šlo poslat zadavateli.
- **Navrhuješ, nerozhoduješ.** Rychlou dráhu potvrzuje AI tým, standardní dráhu prioritizuje Evolution, use-case schvaluje jeho vlastník. Tvůj výstup je podklad, ne rozhodnutí.
- **Nic si nedomýšlíš.** Co v zadání, komentářích nebo přílohách není, do reportu nepatří jako fakt — patří to do sekce „Chybí".

## Zdroje pravidel (princip jednoho originálu)

Obsahová pravidla NEJSOU v tomto skillu — čteš je při každém spuštění z živých masterů v tomto repozitáři, aby triage vždy běžela podle aktuální verze:

| Co potřebuješ | Kde to je (docs/ v kořeni repa) |
| --- | --- |
| Checklist „Patří to nám?", devět otázek, dráhy, stavy backlogu | `docs/Operacni_model_-_produkcni_vetev.html` |
| 12 produkčních use-casů (kontrola duplicity), SLO, governance | `docs/01_Souhrnny_service_dokument_-_AI_Roadmapa__v2_.html` (kap. 3) |
| Compliance brána: 4 úrovně rizika, checklist systému | `docs/Klasifikace_rizik_a_checklist.html` |
| Aktivita vs. projekt (~10 h), fáze Start–Provoz, analýza podílníků | `docs/01_Souhrnny_service_dokument_-_AI_Roadmapa__v2_.html` (kap. 7.3) |

Pokud soubor nenajdeš nebo se pravidla v masterech liší od tohoto skillu, **řekni to nahlas a zeptej se** — nikdy si sám nevybírej verzi, která se hodí.

## Vstupy

1. **Jeden nebo více úkolů ve Freelu** (odkazy, ID, nebo „všechny poptávky v seznamu X"). Úkoly typicky mají jen **název a podklady v popisu** — žádné podúkoly, žádnou strukturu. Přes existující Freelo skript ke každému načti: název, popis, **všechny komentáře** (často obsahují doplnění od zadavatele) a **přílohy** (zadání, přepisy callů). Pozn.: přílohy u poznámek (notes) přes API nejdou — pokud na ně narazíš, vyžádej si je od uživatele.
2. Případně podklady vložené přímo do konverzace (přepis, dokument).

Než začneš hodnotit, **přečti ke každé poptávce všechno**. Komentář ze včerejška může měnit zadání z minulého týdne — při rozporu platí novější, ale rozpor pojmenuj.

## Dávkové zpracování (více poptávek najednou)

- **Pravidla z `docs/` načti jednou** na začátku běhu a použij pro všechny poptávky — nečti mastery opakovaně.
- Každou poptávku zpracuj **celou a nezávisle** (kroky 1–7 níže; brány platí pro každou zvlášť). Nekompletní poptávka nesráží ostatní — dostane verdikt „POTŘEBUJE DOPTAT" a otázky zadavateli, ostatní jedou dál.
- Víc než ~10 poptávek najednou: řekni to, navrhni rozdělení do dávek a nech uživatele vybrat pořadí.
- Výstup dávky má dvě patra:
  1. **Souhrnná prioritizační tabulka** seřazená sestupně podle skóre: `poptávka · dráha · typ (aktivita/projekt) · skóre · návratnost · compliance příznaky · kompletní? (OK / doptat)`. Poptávky bez benefitu jdou na konec s „—" místo skóre.
  2. **Plné triage reporty** ke každé poptávce pod tabulkou.
- Pořadí v tabulce je podklad pro prioritizaci (backlog se řadí podle skóre — Operační model), ale rozhodnutí o pořadí je na lidech / Evolution.

## Postup triage (kroky a brány)

### Krok 1 — Identifikace
Název poptávky, zadavatel, oddělení, kanál příjmu, datum, odkaz na úkol.

### Krok 2 — Checklist „Patří to nám a máme vše?"
Projdi checklist z Operačního modelu (kanonické znění čti z masteru). U každé položky uveď ANO / NE / NEVÍME + jednu větu důkazu (odkud to víš).
- **NE u AI/automatizační komponenty** → poptávka nepatří produkční větvi; navrhni, kam patří (typicky projekt Alfa / IT), a skonči reportem „mimo rozsah".
- **NE u interního zadavatele** → mimo hranici služby; skonči reportem „mimo rozsah".
- **Duplicita**: porovnej s 12 produkčními use-casy z masteru (jmenovitě!) i s ostatními úkoly v backlogu, pokud je máš načtené. Odpovídej formátem „NE" nebo „ANO — překryv s [co konkrétně]" (nikdy „ANO, řešit" — v ano/ne checklistu je to matoucí). Blízkost k existujícímu use-casu není stopka — navrhni přiřazení pod něj.

### Krok 3 — Devět otázek
Projdi devět otázek z Operačního modelu. U každé: odpověď z podkladů (s odkazem, odkud), nebo „CHYBÍ" + navržená doplňující otázka pro zadavatele.

### Krok 4 — Compliance brána
Projdi checklist z „Klasifikace rizik a checklist":
- **Zakázané praktiky** (sociální scoring, manipulace, emoce na pracovišti) → 🛑 STOP, okamžitě ukonči s vysvětlením a doporučením eskalace.
- **Bonita fyzických osob / nábor a řízení lidí** → vysoké riziko → příznak + povinná eskalace na compliance (Svatošová) před realizací.
- **Chatbot / generovaný obsah směrem k lidem** → povinnost transparentnosti („jednáte s AI").
- **Osobní nebo klientská data** → GDPR příznak, posoudit potřebu DPIA.
- **Nástroj třetí strany** → příznak „řešit smlouvu".
Výstup: úroveň rizika (zakázané / vysoké / limitované / minimální) + seznam příznaků. Citlivá data vždy propiš do kroku 5 (parametr `--citliva-data`).

### Krok 5 — Business case (ROI)
**Nikdy nepočítej z hlavy.** Výpočet smí provést **výhradně `scripts/business_case.py`** — jediný výpočetní engine služby. Pokud na stroji není Python, **zastav se a požádej uživatele o instalaci** (např. `winget install Python.Python.3.12`); skript **nikdy nereimplementuj v jiném jazyce** (PowerShell, JS, …) ani výpočet neprováděj ručně — replika je druhý originál a tichý zdroj rozdílných verdiktů. Postup:
1. Z podkladů urči typ přínosu (čas / vyhnutá nákladovost / výnos / risk avoidance) a vstupy.
2. Chybí-li vstupy, použij pomocné odhady skriptu (`--odhad-hodin`, `--odhad-investice`, `--odhad-vynosu`, `--odhad-rizika`) — ale **jen s čísly z podkladů nebo od uživatele**, nikdy s vymyšlenými. Každý odhad v reportu označ „(odhad — vstupy: …)".
3. Bez odhadu benefitu skript vrátí „POTŘEBUJE DOPTAT" — to je verdikt, respektuj ho.

### Krok 6 — Verdikt a semafor
Slož dohromady:
- **Semafor** (první řádek reportu): 🟢 zralé k rozhodnutí / 🟡 potřebuje doptat / 🔴 stop (zakázaná praktika nebo mimo rozsah služby) + verdikt jednou lidskou větou.
- **Dráha** (ze skriptu): rychlá / standardní / ⚠ nejdřív compliance brána. U 🟡 vždy označ „(předběžně)" — dokud chybí čísla, dráha je odhad, ne verdikt; report nesmí zároveň tvrdit „nelze rozhodnout" a „dráha standardní" bez tohoto označení.
- **Typ dle pracnosti** (master, kap. 7.3): odhad pracnosti ≤ ~10 h = aktivita; víc = projekt. Odhad pracnosti podlož (z čeho vychází).
- **Skóre a návratnost** ze skriptu — pro řazení v backlogu.
Stavy úkolů ve Freelu neměníš ani nenavrhuješ — o stavech rozhoduje AI tým mimo tento skill.

### Krok 6b — „Zbývá vyjasnit" (párovací pravidlo)
Sestav otázky pro zadavatele/vlastníka. Platí tvrdé pravidlo úplnosti: **každé CHYBÍ / NEVÍME / ČÁSTEČNĚ z kroků 2–5 musí mít právě jednu otázku** — na konci ověř párování oběma směry (žádné CHYBÍ bez otázky, žádná otázka bez podkladu v reportu). Zvlášť hlídej vstupy business case: chybí-li benefit, VŽDY musí být otázky na přínos a investici — právě ony odblokují verdikt.
- Formuluj **lidsky a připravené ke zkopírování** zadavateli — ptáš se člověka, ne vyplňuješ formulář.
- Otázky na čísla formuluj tak, aby odpověď šla **rovnou dosadit do kalkulačky** (např. „Kolikrát týdně něco dohledáváte a kolik minut jedno hledání zabere?" → vstupy `--odhad-hodin`), a v závorce uveď, k čemu odpověď poslouží.

### Krok 7 — Analýza podílníků (podmíněně)
**Povinná**, když je poptávka projekt (pracnost > ~10 h) NEBO jde standardní dráhou. U aktivit na rychlé dráze ji jen nabídni. Předvyplň z podkladů, co jde, zbytek nech prázdné s otazníkem — nevymýšlej očekávání za lidi. Formát **odrážky, nikdy tabulka** (Freelo markdown tabulky nevykresluje a rozpadnou se do nečitelné kaše):

```
• **Jméno** (oddělení) — role: používá / akceptuje / spolupracuje / realizuje · očekávání: …
```

Role vždy zahrnují minimálně: kdo to bude používat, kdo akceptuje výsledek, kdo spolupracuje na realizaci. Nezapomeň na compliance (citlivá data → Svatošová) a IT (integrace).

**Obecné pravidlo formátu pro Freelo: žádné markdown tabulky nikde ve výstupu** — vše, co by byla tabulka (checklist, podílníci), piš jako odrážky. Tabulky používej jen v konverzačním náhledu (souhrnná prioritizační tabulka dávky), do Freela se nezapisují.

## Šablona triage reportu

Pořadí je záměrně obrácené: **nahoře akce a verdikt (5 vteřin čtení), dole důkazní detail** (pro toho, kdo chce ověřit). Nikdy nepohřbívej otázky zadavateli na konec.

```
🟢/🟡/🔴 [VERDIKT VELKÝM] — [název poptávky]
[Verdikt jednou lidskou větou: co s tím a proč.]

❗ ZBÝVÁ VYJASNIT — otázky pro [zadavatel] (připravené k odeslání):
1. [lidsky formulovaná otázka] (→ k čemu odpověď poslouží)
2. …
[u 🟢 reportu: „Nic — podklady jsou kompletní."]

**Verdikt (návrh — rozhoduje člověk):**
dráha … [(předběžně) u 🟡] · aktivita/projekt (pracnost ~X h) · skóre … · návratnost …
· compliance: [příznaky / bez příznaků]

**Podílníci:**
• **Jméno** (oddělení) — role · očekávání
[nebo „nabídnuto — u aktivity volitelná"]

--- detail (důkazy) ---

**Identifikace:** zadavatel · oddělení · kanál · datum · odkaz na úkol

**Patří to nám? (checklist):**
• [položka] — ANO/NE/NEVÍME — [důkaz]
• Duplicita — NE / ANO — překryv s […]

**Devět otázek:**
• [otázka] — [odpověď + zdroj] / CHYBÍ (→ otázka č. X výše)

**Compliance:** úroveň rizika … · příznaky … · eskalace …

**Business case:** výstup business_case.py (text) + označení odhadů a jejich vstupů

**K propsání:** [co z triage patří do masterů / backlogu]

Pravidla dle: Operační model, Souhrnný dokument v2, Klasifikace rizik,
kalkulačka business case — načteno [datum] z docs/ tohoto repa;
výpočet: scripts/business_case.py.
```

## Náhled → schválení → zápis

1. **Ukaž uživateli vše v konverzaci**: u dávky nejdřív souhrnnou prioritizační tabulku, pak jednotlivé reporty. Zvlášť vypíchni: verdikty, chybějící informace a compliance příznaky. Počkej na schválení — uživatel může schválit všechny poptávky, jen některé („zapiš 1 a 3"), nebo si vyžádat úpravy.
2. Po schválení přes Freelo skript **u každé schválené poptávky**:
   - **založ v úkolu podúkol „Kvalifikace požadavku"** a vlož do něj celý triage report (poptávky mají jinak jen název a popis — podúkol vzniká právě tímto skillem, nikde jinde),
   - sekci „❗ ZBÝVÁ VYJASNIT" navíc vlož jako **komentář k úkolu**, aby zadavatel otázky viděl bez rozklikávání podúkolu.
   - **Stavy úkolů neměníš ani nenavrhuješ.**
3. Co uživatel v náhledu změní, změň i v zapisované verzi — zapisuje se schválená podoba, ne tvůj původní návrh.

## Rychlý kontrolní seznam před odevzdáním

- Načetl jsem KAŽDÝ úkol včetně komentářů a příloh, ne jen popis?
- Četl jsem pravidla z masterů v docs/ (jednou na začátku běhu), ne z paměti?
- Prošla každá poptávka všemi kroky nezávisle (žádná nepřeskočila bránu)?
- Je každé ANO/NE v checklistu podložené důkazem z podkladů?
- Spočítal jsem business case výhradně skriptem `business_case.py` (žádná replika, žádný ruční výpočet)?
- **Párování:** má každé CHYBÍ/NEVÍME/ČÁSTEČNĚ svou otázku v „Zbývá vyjasnit" — a u chybějícího benefitu otázky na přínos i investici?
- Začíná report semaforem a jednou lidskou větou; je u 🟡 dráha označena „(předběžně)"?
- Jsou podílníci i checklist jako odrážky (žádné tabulky ve výstupu pro Freelo)?
- Prošla citlivá data compliance branou a propsala se do dráhy?
- Je u dávky souhrnná tabulka (jen v náhledu) seřazená podle skóre a verdikty označené jako návrh?
- U projektu/standardní dráhy: je tam analýza podílníků?
- Čekám na schválení před jakýmkoli zápisem do Freela — a zapisuji jen schválené poptávky (podúkol „Kvalifikace požadavku" + komentář se „Zbývá vyjasnit", žádné změny stavů)?
