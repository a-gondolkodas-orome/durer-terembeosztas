# durer-terembeosztas
python script based on IP model that scheduls a room for a competition day based on different parameters

## Projekt célja

**Ülésrend viszonylagosan gyors generálása a Dűrer versenyre egy IP modell segítségével.**

## Matematikai modell elemei:

- **büntető súlyok kategóriák alapján vízszintes és függőleges szomszédok számára.**
- **büntető súlyok legalább egy közös iskola esetén vízszintes és függőleges és átlós szomszédok számára.**
- **A kapott eredmény egy ültetést reprezentál - minden helyen may 1 csapat ül és minden csapat ül valahol**

***Extra funkció: Meg lehet adni a kategóriák elhelyezkedését a teremben.***

## Technikai adatok:

- **terem: Egy *room.txt nevű* file amiben egy n*k-s téglalapba írt értékek vannak elkódolva space és újsor elválasztásokkal. Ajánlott számokkal kitölteni. Speciálisan a 0 jelent olyan helyet, ahova nem ülhet csapat.**
- **Adatok: Egy *setup.json* nevű file, amiben szerepelnek a súlyok, és egy max futás idő. Plust az extra funkció használatához egy leképezés, hogy melyik szám, melyik katóriát jelöli a megadott room.txt fileban is van generálva, ami egy elterjett mpi modellforma.**
**A használandó kulcsokhoz itt a példa: *"same_cat_row": 20,"same_cat_col": 15,"same_sch_row": 2,"same_sch_col": 2,"same_sch_diag": 1,"A kategória": 2,"B kategória": 1,"C kategória": 3,"max_run_time": 5***
- **csapatadatok: Egy *csapatok.xlsx* nevű file, amiben szerepelnek a következő oszlopok pont ezen fejlecekkel: 'ID', 'Csapatnév', 'Kategória', '1. tag iskolája', '2. tag iskolája', '3. tag iskolája', 'Beosztani'
  Itt a 'Beosztani' oszlop egy indikátor oszlop, ahol 1 jelöli, hoyg mely csapatokat akarjuk az adott terembe beosztani. A többi oszlop értelemszerű adat a csapat adatbázisokból**

## Használat

**A mellékelten szolgáltatott *ulesrend.py* filet és a technikai adatok közt ismertetett fileokat helyezd egy mappába, majd tetszőleges helyről futtasd az *ulesrend.py* scriptet. A használt solver a CBC_CMD MIP solver.**

**Ha kategóriákat nem akarsz megadni fix helyen a teremben, akkor egyszerűen lefut a program, generálva egy *ulesrend.txt -* t a csapatnevekkel egy terembeosztás formájában, tab és sortörés van elválasztónak használva. Illetve ha valakit a keletkezett kategória elhelyezkedés érdekli, az is hasonló formában megtalálható az *ulesrend_kategoriak.txt* fileban.
Amennyiben módosítanád a modellt, vagy más megoldót használnál, akkor egy *test.mps* file is. **

**Ha pythonnal és ugyan így PuLP-vel akarsz más megoldót használni, akkor importoktól eltekintve elég a következő script:**

```
import pulp as pl
var, model = pl.LpProblem.fromMPS(r'test.mps')
result = model.solve(pl.GUOROBI()))
```

**Ha kategóriát is megadsz,** akkor előfeltétel, hogy ugyanannyi külöböző kategória legyen a megadott csapatok között, mint amennyi különböző nem 0 jelölő van a room.txt fileban. Ez esetben kapsz egy kérdést a programtól, hogy ezen adatok fel legyenek-e használva.

## Példa
Az itt feltöltött példa input fileokkal lehet tesztelni a program futását, illetve azokat lehet alapul venni, ha új input fileokat szeretnél készíteni.
