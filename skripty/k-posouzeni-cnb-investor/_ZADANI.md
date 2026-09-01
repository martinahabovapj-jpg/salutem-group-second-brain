# Zadání pro posouzení investorské strany ze seznamu ČNB

V `kandidati.md` jsou **skupiny nemovitostních fondů**, které ČNB vede ve své
měsíční statistice a které v naší databázi nejsou.

> **Proč po skupinách a ne po fondech.** WOOD & Company má sedm nemovitostních
> fondů, RSJ dvanáct ve třech větvích. Oslovuje se správce skupiny, ne každý
> podfond zvlášť. Kdyby se do fronty sypal každý fond, měla by sedm řádků pro
> tutéž firmu — a schvalovatel by se ji naučil přeskakovat.

> **Tohle je investorská strana, ne financování.** Nemovitostní fond nepůjčuje,
> ale alokuje kapitál do nemovitostí. Patří do listu 6, ne do listu 3.

## Co u každé skupiny zjistit

1. **Kdo je protistrana k oslovení.** Sloupec „Reprezentativní fond" je jen
   vodítko — u podfondů je skutečnou protistranou **obhospodařovatel nebo
   správce**, kterého v seznamu ČNB není. Ten se dohledá z webu fondu nebo
   z obchodního rejstříku.
2. **Do čeho konkrétně investuje** — rezidence, logistika, kanceláře, retail,
   půda, hotely. To rozhoduje, jestli je pro naše projekty relevantní.
3. **Objem** (NAV nebo AUM), pokud je zveřejněný.

## Rozhodnutí

| Verdikt | Kdy |
|---|---|
| `zaradit` | alokuje kapitál do nemovitostí a dá se doložit, do čeho |
| `zamitnout` | kaptivní fond jedné skupiny bez zájmu o cizí projekty · fond v likvidaci |
| `nevim` | fond existuje, ale nic dalšího se nedá doložit |

**Kategorie od ČNB nestačí k zařazení**, stačí ale k tomu, aby se skupina
neztratila. Když se nedá nic doložit, dej `nevim` — ne `zamitnout`.

## Pravidlo, které se neporušuje

Ke každému verdiktu `zaradit` i `zamitnout` musíš dodat **doslovnou citaci**
a **URL**.

## Výstup

Dávku zapiš do JSON ve tvaru pro `financovani-zapis-investoru.py` — tedy
s poli `ico`, `nazev`, `web`, `typ`, `verdikt`, `segment`, `aum`,
`gatekeeper`, `duvod`, `citace`, `zdroj`. U skupiny použij IČO té entity,
kterou jsi vyhodnotil jako protistranu.

```
python financovani-zapis-investoru.py davka.json --zapis
```
