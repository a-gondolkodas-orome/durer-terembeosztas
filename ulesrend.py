from pulp import LpProblem, LpVariable, lpSum, LpMinimize, PULP_CBC_CMD
import pandas as pd
import json
import os
from time import time
from itertools import permutations

# Import setups
file_name = "setup.json"
with open(file_name, encoding="utf-8") as import_file:
    setup = json.load(import_file)

cost_cat_row = setup["penalty_weights"]["same_category_row"]
cost_cat_col = setup["penalty_weights"]["same_category_col"]
cost_sch_row = setup["penalty_weights"]["same_school_row"]
cost_sch_col = setup["penalty_weights"]["same_school_col"]
cost_sch_diag = setup["penalty_weights"]["same_school_diag"]
max_run_time = setup["max_run_time"]

# Set up room
file_name = "room.txt"
with open(file_name) as roomFile:
    room = [line.strip().split(setup["splitting_char"]) for line in roomFile]
places = []
len_x = len(room)
len_y = len(room[0])
for x in range(len_x):
    if len(room[x]) != len_y:
        raise ValueError(f"Invalid room setup: {room[x]}, expected length: {len_y}")
    for y in range(len_y):
        if room[x][y] == "-":
            pass
        elif room[x][y] in setup["category_notation"].values():
            places.append((x, y))
        else:
            raise ValueError(f"Invalid room setup: {room[x][y]}. It should be '-' or a category notation.")

# Import teams
file_name = "csapatok.tsv"
csapatok = pd.read_csv(file_name, delimiter="\t")
csapatok = csapatok[csapatok["Beosztani"] == 1]
expected_columns = {
    "ID",
    "Csapatnév",
    "Kategória",
    "Beosztani",
    "1. tag iskolája",
    "2. tag iskolája",
    "3. tag iskolája",
}
if set(csapatok.columns) != expected_columns:
    raise ValueError(
        f"Wrong columns. Expected: {expected_columns}, got: {set(csapatok.columns)}"
    )

# school dic
sch_dic = {}
for x, y in places:
    for id1 in csapatok["ID"]:
        sch1 = set([
            csapatok[csapatok["ID"] == id1]["1. tag iskolája"].values[0],
            csapatok[csapatok["ID"] == id1]["2. tag iskolája"].values[0],
            csapatok[csapatok["ID"] == id1]["3. tag iskolája"].values[0],
        ])
        sch_dic[id1] = sch1


# Decide modell type: IS CATEGORY PLACES GIVEN
cat_place_given = setup["is_category_preset"]

# room_set = set()
# for e1 in room:
#     for e2 in e1:
#         room_set.add(e2)
# if len(room_set) - 1 == len(csapatok["Kategória"].unique()):
#     cat_place_given
#     var = input(
#         "Choose option: Is the category place pre selected and translation is given in setup.json? (y/n):"
#     )
# if (
#     var.strip() == "y"
#     or var.strip() == "Y"
#     or var.strip() == "yes"
#     or var.strip() == "Yes"
# )::
# cat_place_given = True


# Model
model = LpProblem("Ülésrend", LpMinimize)


var_name_hely_indicator = []
for id in csapatok["ID"]:
    category = csapatok[csapatok["ID"] == id]["Kategória"].values[0]
    category_short = setup["category_notation"][category]
    for x, y in places:
        if not cat_place_given or category_short == room[x][y]:
            var_name_hely_indicator.append((x, y, id))
var_hely_indicator = LpVariable.dicts(
    "hely", var_name_hely_indicator, cat="Binary", lowBound=0, upBound=1
)

if not cat_place_given:
    var_name_penalty_cat_row = [
        (x, y, id1, x - 1, y, id2)
        for (x, y) in places
        for id1 in csapatok["ID"]
        for id2 in csapatok["ID"]
    ]
    var_penalty_cat_row = LpVariable.dicts(
        "cat_pen_row", var_name_penalty_cat_row, cat="Binary", lowBound=0, upBound=1
    )
    var_name_penalty_cat_col = [
        (x, y, id1, x, y - 1, id2)
        for (x, y) in places
        for id1 in csapatok["ID"]
        for id2 in csapatok["ID"]
    ]
    var_penalty_cat_col = LpVariable.dicts(
        "cat_pen_col", var_name_penalty_cat_col, cat="Binary", lowBound=0, upBound=1
    )

var_name_penalty_sch_row = [
    (x, y, id1, x - 1, y, id2)
    for (x, y) in places
    for id1 in csapatok["ID"]
    for id2 in csapatok["ID"]
]
var_penalty_sch_row = LpVariable.dicts(
    "sch_pen_row", var_name_penalty_sch_row, cat="Binary", lowBound=0, upBound=1
)
var_name_penalty_sch_col = [
    (x, y, id1, x, y - 1, id2)
    for (x, y) in places
    for id1 in csapatok["ID"]
    for id2 in csapatok["ID"]
]
var_penalty_sch_col = LpVariable.dicts(
    "sch_pen_col", var_name_penalty_sch_col, cat="Binary", lowBound=0, upBound=1
)

var_name_penalty_sch_diag = [
    (x, y, id1, x + dx, y + dy, id2)
    for (x, y) in places
    for id1 in csapatok["ID"]
    for id2 in csapatok["ID"]
    for (dx, dy) in [(-1, -1), (-1, 1)]
]
var_penalty_sch_diag = LpVariable.dicts(
    "sch_pen_diag", var_name_penalty_sch_diag, cat="Binary", lowBound=0, upBound=1
)

# extra cost, Objective function
s = time()
# obj
if cat_place_given == True:
    model += (
        cost_sch_row
        * lpSum(
            [
                var_penalty_sch_row[(x, y, id1, x - 1, y, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_sch_col
        * lpSum(
            [
                var_penalty_sch_col[(x, y, id1, x, y - 1, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_sch_diag
        * lpSum(
            [
                var_penalty_sch_diag[(x, y, id1, x + dx, y + dy, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
                for (dx, dy) in [(-1, -1), (-1, 1)]
            ]
        )
    )
else:
    model += (
        cost_cat_row
        * lpSum(
            [
                var_penalty_cat_row[(x, y, id1, x - 1, y, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_cat_col
        * lpSum(
            [
                var_penalty_cat_col[(x, y, id1, x, y - 1, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_sch_row
        * lpSum(
            [
                var_penalty_sch_row[(x, y, id1, x - 1, y, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_sch_col
        * lpSum(
            [
                var_penalty_sch_col[(x, y, id1, x, y - 1, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
            ]
        )
        + cost_sch_diag
        * lpSum(
            [
                var_penalty_sch_diag[(x, y, id1, x + dx, y + dy, id2)]
                for (x, y) in places
                for id1 in csapatok["ID"]
                for id2 in csapatok["ID"]
                for (dx, dy) in [(-1, -1), (-1, 1)]
            ]
        )
    )


# Conditions
for x, y in places:
    # row / x
    for id1, id2 in permutations(csapatok["ID"], 2):
        if x > 0:
            # cost of school per row
            if (
                (x, y, id1) in var_name_hely_indicator
                and (x - 1, y, id2) in var_name_hely_indicator
                and len(sch_dic[id1] & sch_dic[id2]) > 0
            ):
                model += (
                    var_penalty_sch_row[(x, y, id1, x - 1, y, id2)] + 1
                    >= var_hely_indicator[(x, y, id1)]
                    + var_hely_indicator[(x - 1, y, id2)]
                )

            if cat_place_given == False:
                # cost of category per row
                cat1 = csapatok[csapatok["ID"] == id1]["Kategória"].values[0]
                cat2 = csapatok[csapatok["ID"] == id2]["Kategória"].values[0]
                if cat1 == cat2:
                    model += (
                        var_penalty_cat_row[(x, y, id1, x - 1, y, id2)] + 1
                        >= var_hely_indicator[(x, y, id1)]
                        + var_hely_indicator[(x - 1, y, id2)]
                    )

        if y > 0:
            # cost of school per col
            if (
                (x, y, id1) in var_name_hely_indicator
                and (x, y - 1, id2) in var_name_hely_indicator
                and len(sch_dic[id1] & sch_dic[id2]) > 0
            ):
                if id1==705 and id2==734:
                    print(x,y, id1, id2)
                model += (
                    var_penalty_sch_col[(x, y, id1, x, y - 1, id2)] + 1
                    >= var_hely_indicator[(x, y, id1)]
                    + var_hely_indicator[(x, y - 1, id2)]
                )

            if cat_place_given == False:
                # cost of category per col
                if (
                    csapatok[csapatok["ID"] == id1]["Kategória"].values[0]
                    == csapatok[csapatok["ID"] == id2]["Kategória"].values[0]
                ):
                    model += (
                        var_penalty_cat_col[(x, y, id1, x, y - 1, id2)] + 1
                        >= var_hely_indicator[(x, y, id1)]
                        + var_hely_indicator[(x, y - 1, id2)]
                    )
        if x > 0 and y > 0:
            # cost of school per diag 1
            if (
                (x, y, id1) in var_name_hely_indicator
                and (x - 1, y - 1, id2) in var_name_hely_indicator
                and len(sch_dic[id1] & sch_dic[id2]) > 0
            ):
                model += (
                    var_penalty_sch_diag[(x, y, id1, x - 1, y - 1, id2)] + 1
                    >= var_hely_indicator[(x, y, id1)]
                    + var_hely_indicator[(x - 1, y - 1, id2)]
                )
        if x > 0 and y + 1 < len_y:
            # cost of school per diag 2
            if (
                (x, y, id1) in var_name_hely_indicator
                and (x - 1, y + 1, id2) in var_name_hely_indicator
                and len(sch_dic[id1] & sch_dic[id2]) > 0
            ):
                model += (
                    var_penalty_sch_diag[(x, y, id1, x - 1, y + 1, id2)] + 1
                    >= var_hely_indicator[(x, y, id1)]
                    + var_hely_indicator[(x - 1, y + 1, id2)]
                )


# Exactly at one place
for id in csapatok["ID"]:
    model += (
        lpSum(
            [
                var_hely_indicator[(x, y, id1)]
                for (x, y, id1) in var_name_hely_indicator
                if id == id1
            ]
        )
        == 1
    )

# Max one at each place
for x, y in places:
    model += 1 >= lpSum(
        [
            var_hely_indicator[(x1, y1, id)]
            for (x1, y1, id) in var_name_hely_indicator
            if x == x1 and y == y1
        ]
    )

print(time() - s)
model.writeMPS(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.mps"))

time_limit_in_seconds = 60 * max_run_time
model.solve(PULP_CBC_CMD(msg=1, timeLimit=time_limit_in_seconds))


res_cat = [[""] * len_y for _ in range(len_x)]
res_name = [[""] * len_y for _ in range(len_x)]
res_school1 = [[""] * len_y for _ in range(len_x)]
print(f"csapat id: x,y")
for x, y, id in var_name_hely_indicator:
    if var_hely_indicator[(x, y, id)].value() == 1:
        print(f"{id}: {x,y}")
        res_cat[x][y] = csapatok[csapatok["ID"] == id]["Kategória"].values[0]
        res_name[x][y] = csapatok[csapatok["ID"] == id]["Csapatnév"].values[0]
        res_school1[x][y] = csapatok[csapatok["ID"] == id]["1. tag iskolája"].values[0]


with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ulesrend_kategoriak.txt"),
    "w",
    encoding="utf-8",
) as f:
    for y in range(len_y):
        for x in range(len_x):
            f.write(f"{res_cat[x][y]} \t")
        f.write("\n")

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ulesrend.txt"),
    "w",
    encoding="utf-8",
) as f:
    for y in range(len_y):
        for x in range(len_x):
            f.write(f"{res_name[x][y]} \t")
        f.write("\n")

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ulesrend_iskolak.txt"),
    "w",
    encoding="utf-8",
) as f:
    for y in range(len_y):
        for x in range(len_x):
            f.write(f"{res_school1[x][y]} \t")
        f.write("\n")
