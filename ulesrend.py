try:
    from pulp import *
    import pandas as pd
    import json
except ImportError as e:
    print("Error -> ", e)
    print("One of the packages or neccesery subpackages not installed: pulp, pandas, json")




#Set up room
file_name= os.path.join(os.path.dirname(os.path.abspath(__file__)), "room.txt")
with open(file_name) as roomFile:
    room = [line.split() for line in roomFile]
len_x=len(room)
len_y=len(room[0])
places=[]
for x in range(len_x): 
    for y in range(len_y):
        if room[x][y]!="0" and room[x][y]!=0:
            places.append((x,y))

# Import setups
file_name= os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup.json")
with open(file_name, encoding='utf-8') as import_file:
  setup = json.load(import_file)

cost_cat_row = setup['same_cat_row']
cost_cat_col = setup["same_cat_col"]
cost_sch_row = setup["same_sch_row"]
cost_sch_col = setup["same_sch_col"]
cost_sch_diag = setup["same_sch_diag"]
max_run_time = setup["max_run_time"]

# Import teams
file_name= os.path.join(os.path.dirname(os.path.abspath(__file__)), "csapatok.xlsx")
excel_data = pd.read_excel(file_name)
data = pd.DataFrame(excel_data, columns=['ID', 'Csapatnév', 'Kategória', '1. tag iskolája', '2. tag iskolája', '3. tag iskolája', 'Beosztani']) 
csapatok = data[data['Beosztani'] == 1]



# school dic
sch_dic={}
for (x,y) in places:
    for id1 in csapatok['ID']:
                sch1=set([csapatok[csapatok['ID']==id1]['1. tag iskolája'].values[0],csapatok[csapatok['ID']==id1]['2. tag iskolája'].values[0],csapatok[csapatok['ID']==id1]['3. tag iskolája'].values[0]])
                sch_dic[id1] = sch1


# Decide modell type: IS CATEGORY PLACES GIVEN
cat_place_given = False

room_set=set()
for e1 in room:
     for e2 in e1:
          room_set.add(e2)
if len(room_set) - 1 == len(csapatok['Kategória'].unique()):
    var = input("Choose option: Is the category place pre selected and translation is given in setup.json? (y/n):")
if var.strip() == 'y' or var.strip() == 'Y' or var.strip() == 'yes' or var.strip() == 'Yes':
    cat_place_given=True



#Model
model =LpProblem("Ülésrend",LpMinimize)


var_name_hely_indicator=[]
if cat_place_given == True:
    for id in csapatok['ID']:
        for (x,y) in places:
            if setup[str(csapatok[csapatok['ID']==id]['Kategória'].values[0])] == int(room[x][y]):
             var_name_hely_indicator.append((x,y,id))
else:
    for id in csapatok['ID']:
        for (x,y) in places:
            var_name_hely_indicator.append((x,y,id))
var_hely_indicator=LpVariable.dicts("hely", var_name_hely_indicator, cat="Binary", lowBound=0, upBound=1)


if cat_place_given == False:
    var_name_penalty_cat_row=[(x,y,id1,x-1,y,id2) for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']]
    var_penalty_cat_row = LpVariable.dicts("cat_pen_row", var_name_penalty_cat_row, cat="Binary", lowBound=0, upBound=1)
    var_name_penalty_cat_col=[(x,y,id1,x,y-1,id2) for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']]
    var_penalty_cat_col = LpVariable.dicts("cat_pen_col", var_name_penalty_cat_col, cat="Binary", lowBound=0, upBound=1)

var_name_penalty_sch_row=[(x,y,id1,x-1,y,id2) for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']]
var_penalty_sch_row = LpVariable.dicts("sch_pen_row", var_name_penalty_sch_row, cat="Binary", lowBound=0, upBound=1)
var_name_penalty_sch_col=[(x,y,id1,x,y-1,id2) for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']]
var_penalty_sch_col = LpVariable.dicts("sch_pen_col", var_name_penalty_sch_col, cat="Binary", lowBound=0, upBound=1)

var_name_penalty_sch_diag=[(x,y,id1,x+dx,y+dy,id2) for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID'] for (dx,dy) in [(-1,-1), (-1,1)]]
var_penalty_sch_diag = LpVariable.dicts("sch_pen_diag", var_name_penalty_sch_diag, cat="Binary", lowBound=0, upBound=1)

# extra cost, Objective function
s=time()
#obj
if cat_place_given == True:
    model += cost_sch_row * lpSum([var_penalty_sch_row[(x,y,id1,x-1,y,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
        cost_sch_col * lpSum([var_penalty_sch_col[(x,y,id1,x,y-1,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
        cost_sch_diag * lpSum([var_penalty_sch_diag[(x,y,id1,x+dx,y+dy,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID'] for (dx,dy) in [(-1,-1), (-1,1)]])
else:
    model += cost_cat_row * lpSum([var_penalty_cat_row[(x,y,id1,x-1,y,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
    cost_cat_col * lpSum([var_penalty_cat_col[(x,y,id1,x,y-1,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
    cost_sch_row * lpSum([var_penalty_sch_row[(x,y,id1,x-1,y,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
    cost_sch_col * lpSum([var_penalty_sch_col[(x,y,id1,x,y-1,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID']])+\
    cost_sch_diag * lpSum([var_penalty_sch_diag[(x,y,id1,x+dx,y+dy,id2)] for (x,y) in places for id1 in csapatok['ID'] for id2 in csapatok['ID'] for (dx,dy) in [(-1,-1), (-1,1)]])
    

# Conditions
for (x,y) in places:
    #row / x
    if x-1 > 0:
        for id1 in csapatok['ID']:
            for id2 in csapatok['ID']:       
                # cost of school per row
                if (x,y,id1) in var_name_hely_indicator and (x-1,y,id2) in var_name_hely_indicator and sch_dic[id1] & sch_dic[id2]:
                    model += var_penalty_sch_row[(x,y,id1,x-1,y,id2)] + 1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x-1, y, id2)]

                if cat_place_given == False:
                    # cost of category per row
                    cat1 = csapatok[csapatok['ID']==id1]['Kategória'].values[0]
                    cat2 = csapatok[csapatok['ID']==id2]['Kategória'].values[0]
                    if cat1 == cat2:
                        model += var_penalty_cat_row[(x,y,id1,x-1,y,id2)] + 1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x-1, y, id2)]

    #col / x
    if y-1 > 0:
        for id1 in csapatok['ID']:
            for id2 in csapatok['ID']:
                # cost of school per col
                if (x,y,id1) in var_name_hely_indicator and (x,y-1,id2) in var_name_hely_indicator and sch_dic[id1] & sch_dic[id2]:
                    model += var_penalty_sch_col[(x,y,id1,x,y-1,id2)] + 1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x, y-1, id2)]

                if cat_place_given == False:
                    # cost of category per col
                    if csapatok[csapatok['ID']==id1]['Kategória'].values[0] == csapatok[csapatok['ID']==id2]['Kategória'].values[0]:
                        model += var_penalty_cat_col[(x,y,id1,x,y-1,id2)] +1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x, y-1, id2)]

                
    # cost of school per diag 1
    if x-1 > 0 and y-1 >0: 
        if (x,y,id1) in var_name_hely_indicator and (x-1,y-1,id2) in var_name_hely_indicator and sch_dic[id1] & sch_dic[id2]:
            model += var_penalty_sch_diag[(x,y,id1,x-1,y-1,id2)] +1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x-1, y-1, id2)]
            
    # cost of school per diag 2
    if x-1 > 0 and y+1 < len_y: 
        if (x,y,id1) in var_name_hely_indicator and (x-1,y+1,id2) in var_name_hely_indicator and sch_dic[id1] & sch_dic[id2]:
            model += var_penalty_sch_diag[(x,y,id1,x-1,y+1,id2)] + 1 >= var_hely_indicator[(x, y, id1)] + var_hely_indicator[(x-1, y+1, id2)]
        

# Exactly at one place
for id in csapatok['ID']:
    model+= lpSum([var_hely_indicator[(x,y,id1)] for (x,y,id1) in var_name_hely_indicator if id==id1]) == 1

# Max one at each place
for (x,y) in places:
    model += 1 >= lpSum([var_hely_indicator[(x1,y1,id)] for (x1,y1,id) in var_name_hely_indicator if x==x1 and y==y1])

print(time()-s)
model.writeMPS(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.mps"))

time_limit_in_seconds = 60*max_run_time
model.solve(PULP_CBC_CMD(msg=1, maxSeconds=time_limit_in_seconds))


res_cat=[[""]*len_y for _ in range(len_x)]
res_name=[[""]*len_y for _ in range(len_x)]
print(f"csapat id: x,y")
for (x,y,id) in var_name_hely_indicator:
    if var_hely_indicator[(x,y,id)].value()==1:
        print(f"{id}: {x,y}")
        res_cat[x][y]=csapatok[csapatok['ID']==id]['Kategória'].values[0]
        res_name[x][y]=csapatok[csapatok['ID']==id]['Csapatnév'].values[0]


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ulesrend_kategoriak.txt'), 'w', encoding='utf-8') as f:
    for y in range(len_y):
        for x in range(len_x):
            f.write(f"{res_cat[x][y]} \t")
        f.write("\n")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'ulesrend.txt'), 'w', encoding='utf-8') as f:
    for y in range(len_y):
        for x in range(len_x):
            f.write(f"{res_name[x][y]} \t")
        f.write("\n")