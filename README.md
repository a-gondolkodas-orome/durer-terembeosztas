# durer-seating plan

Category and school based seating plan for Dürer competition with Integer Programming model.

## Mathematical model

- Penalty weights based on categories for horizontal and vertical neighbors.
- Penalty weights if at least one school is the same for horizontal, vertical, and diagonal neighbors.
- The result represents a seating arrangement - every seat has one team, and every team is seated somewhere.

***Extra feature: You can specify the location of categories in the room.***

## Input

### Config
Adatok: Egy *setup.json* nevű file, amiben szerepelnek a súlyok, és egy max futás idő. Plust az extra funkció használatához egy leképezés, hogy melyik szám, melyik katóriát jelöli a megadott room.txt fileban is van generálva, ami egy elterjett mpi modellforma.

### Room
terem: Egy *room.txt nevű* file amiben egy n*k-s téglalapba írt értékek vannak elkódolva space és újsor elválasztásokkal. '-' jelentése, hogy ott nem ül csapat. Space-ekkel vagy tabokkal lehet elválasztani az értékeket. A kódolást a `setup.json`-ben meg kell adni.
A használandó kulcsokhoz itt a példa: *"same_category_row": 20,"same_category_col": 15,"same_school_row": 2,"same_school_col": 2,"same_school_diag": 1,"A kategória": 2,"B kategória": 1,"C kategória": 3,"max_run_time": 5*

### Teamdatas
Egy *csapatok.tsv* nevű file, amiben szerepelnek a következő oszlopok pont ezen fejlecekkel: 'ID', 'Csapatnév', 'Kategória', '1. tag iskolája', '2. tag iskolája', '3. tag iskolája', 'Beosztani'
Itt a 'Beosztani' oszlop egy indikátor oszlop, ahol 1 jelöli, hoyg mely csapatokat akarjuk az adott terembe beosztani. A többi oszlop értelemszerű adat a csapat adatbázisokból

## Használat

A mellékelten szolgáltatott *ulesrend.py* filet és a technikai adatok közt ismertetett fileokat helyezd egy mappába, majd tetszőleges helyről futtasd az *ulesrend.py* scriptet. A használt solver a CBC_CMD MIP solver.

**Ha kategóriákat nem akarsz megadni** fix helyen a teremben, akkor egyszerűen lefut a program, generálva egy *ulesrend.txt -* t a csapatnevekkel egy terembeosztás formájában, tab és sortörés van elválasztónak használva. Illetve ha valakit a keletkezett kategória elhelyezkedés érdekli, az is hasonló formában megtalálható az *ulesrend_kategoriak.txt* fileban.
Amennyiben módosítanád a modellt, vagy más megoldót használnál, akkor egy *test.mps* file is. 

Ha pythonnal és ugyan így PuLP-vel akarsz más megoldót használni, akkor importoktól eltekintve elég a következő script:

```
import pulp as pl
var, model = pl.LpProblem.fromMPS(r'test.mps')
result = model.solve(pl.GUOROBI()))
```

**Ha kategóriát is megadsz,** akkor előfeltétel, hogy ugyanannyi külöböző kategória legyen a megadott csapatok között, mint amennyi különböző nem 0 jelölő van a room.txt fileban. Ez esetben kapsz egy kérdést a programtól, hogy ezen adatok fel legyenek-e használva.

## Példa
Az itt feltöltött példa input fileokkal lehet tesztelni a program futását, illetve azokat lehet alapul venni, ha új input fileokat szeretnél készíteni.
