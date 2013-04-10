import Database

verbose = False

# ------------------------------------
#		SNOUT TESTS
# ------------------------------------
from Snout_DB import *
print("Testing snout")
s = Snout_DB(Database.FILE_TEST)
s.clear()
s.insert("Generic",'90-78',1,76.371,82.329,49.91)
s.insert("Generic",'90-78',2,76.371,75.171,49.91)
s.insert("Generic",'90-78',3,103.629,82.329,49.91)
s.insert("Generic2",'90-78',4,103.629,75.171,49.91)
s.update("Generic",'90-78',1,'theta',1)
s.csv_export('test/snouts.csv')
snout_test = True
snout_test = snout_test and (s.num_rows()==4)
if not snout_test:
	print("FAILED: num_rows")
snout_test = snout_test and (s.num_columns()==6)
if not snout_test:
	print("FAILED: num_columns")
snout_test = snout_test and (s.get_columns()==[[0, 'name', 'text', 0, None, 0], [1, 'DIM', 'text', 0, None, 0], [2, 'pos', 'int', 0, None, 0], [3, 'theta', 'real', 0, None, 0], [4, 'phi', 'real', 0, None, 0], [5, 'r', 'real', 0, None, 0]])
if not snout_test:
	print("FAILED: get_columns")
snout_test = snout_test and (s.get_column_names() == ['name','DIM','pos','theta','phi','r'])
if not snout_test:
	print("FAILED: get_column_names")
snout_test = snout_test and (s.get_names() == ['Generic','Generic2'])
if not snout_test:
	print("FAILED: get_names")
snout_test = snout_test and (s.get_pos("Generic","90-78") == [1,2,3])
if not snout_test:
	print("FAILED: get_pos")
snout_test = snout_test and (s.query("Generic","90-78",1) == [["Generic","90-78",1,1,82.329,49.91]])
if not snout_test:
	print("FAILED: query")

if verbose:
	print(s.num_rows())
	print(s.num_columns())
	print(s.get_columns())
	print(s.get_names())
	print(s.get_pos("Generic","90-78"))
	print(s.query("Generic","90-78",1))

if snout_test:
	print('PASSED')
else:
	print('FAILED')




# ------------------------------------
#		HOHLRAUM TESTS
# ------------------------------------
print('---------------')
print('Testing hohlraum')
from Hohlraum_DB import *
hohl_test = True
h = Hohlraum_DB(Database.FILE_TEST)
h.insert('AAA123',"Generic_Au_575",0,"Au",5,10)
h.insert('AAA123',"Generic_Au_575",0,"Au",5,11)
h.insert('AAA456',"Generic_U_575",0,"U",1,2)
h.csv_export('test/hohlraum.csv')

hohl_test = hohl_test and (h.get_names()==['Generic_Au_575','Generic_U_575'])
if not hohl_test:
	print("FAILED: get_names")
hohl_test = hohl_test and (h.get_drawings() == ['AAA123','AAA456'])
if not hohl_test:
	print("FAILED: get_drawings")
hohl_test = hohl_test and (h.get_drawing_name('AAA123') == ['Generic_Au_575'])
if not hohl_test:
	print("FAILED: get_drawing_name")
hohl_test = hohl_test and (h.get_name_drawing('Generic_U_575') == ['AAA456'])
if not hohl_test:
	print("FAILED: get_name_drawing")
hohl_test = hohl_test and (h.get_layers('Generic_U_575') == [0])
if not hohl_test:
	print("FAILED: get_layers")
hohl_test = hohl_test and (h.get_layers('Generic_U_575','AAA456') ==[0])
if not hohl_test:
	print("FAILED: get_layers")
hohl_test = hohl_test and (h.get_layers('asdf') == [])
if not hohl_test:
	print("FAILED: get_layers")
hohl_test = hohl_test and (h.query_drawing('AAA123',0) == [['AAA123',"Generic_Au_575",0,"Au",5,10],['AAA123',"Generic_Au_575",0,"Au",5,11]])
if not hohl_test:
	print("FAILED: query_drawing")
hohl_test = hohl_test and (h.query_name('Generic_Au_575',0) == [['AAA123',"Generic_Au_575",0,"Au",5,10],['AAA123',"Generic_Au_575",0,"Au",5,11]])
if not hohl_test:
	print("FAILED: query_name")
hohl_test = hohl_test and (h.query_name('Generic_Au_575',1) == [])
if not hohl_test:
	print("FAILED: query_name")

if verbose:
	print(h.get_names())
	print(h.get_drawings())
	print(h.get_drawing_name('AAA123'))
	print(h.get_name_drawing('Generic_U_575'))
	print(h.get_layers('Generic_U_575'))
	print(h.get_layers('Generic_U_575','AAA456'))
	print(h.get_layers('asdf'))
	print(h.query_drawing('AAA123',0))
	print(h.query_name('Generic_Au_575',0))
	print(h.query_name('Generic_Au_575',1))

if hohl_test:
	print('PASSED')
else:
	print('FAILED')


# ------------------------------------
#		SHOT TESTS
# ------------------------------------
print('---------------')
print('Testing shot')
from Shot_DB import *
shot_test = True
shot = Shot_DB(Database.FILE_TEST)
shot.clear()
shot.add_column('Yn','real')
shot.add_column("Yn Unc",'real')
shot.add_column('Ti','real')
shot.insert('N010203')
shot.update('N010203','Yn',5)
shot.update('N010203','Yn Unc',2)
shot.update('N010203','Ti',18)
shot.csv_export('test/shot.csv')

shot_test = shot_test and (shot.get_columns() == [[0, 'shot', 'text', 0, None, 0], [1, 'Yn', 'real', 0, None, 0], [2, 'Yn Unc', 'real', 0, None, 0], [3, 'Ti', 'real', 0, None, 0]])
if not shot_test:
	print("FAILED: get_columns")
shot_test = shot_test and (shot.get_column_names() == ['shot', 'Yn', 'Yn Unc', 'Ti'])
if not shot_test:
	print("FAILED: get_column_names")
shot_test = shot_test and (shot.query('N010203') == ['N010203', 5.0, 2.0, 18.0])
if not shot_test:
	print("FAILED: query")
shot_test = shot_test and (shot.query_col('N010203','Yn') == (5,2))
if not shot_test:
	print("FAILED: query_col")
shot_test = shot_test and (shot.query_col('N010203','Ti') == 18)
if not shot_test:
	print("FAILED: query_col 2")

if verbose:
	print(shot.get_columns())
	print(shot.get_column_names())
	print(shot.query('N010203'))
	print(shot.query_col('N010203','Yn'))
	print(shot.query_col('N010203','Ti'))

if shot_test:
	print('PASSED')
else:
	print('FAILED')

# ------------------------------------
#		WRF INVENTORY TESTS
# ------------------------------------
print('---------------')
print('Testing wrf inventory')
from WRF_Inventory_DB import *

wrf_inventory_test = WRF_Inventory_DB(Database.FILE_TEST)
wrf_inventory_test.clear()
wi_test = True
wrf_inventory_test.insert('1',3,'active')
wrf_inventory_test.insert('2',0,'active')
wrf_inventory_test.insert('3',-1,'retired')
if not wi_test:
	print("FAILED: insert")
wrf_inventory_test.update('3',5,'retired')
if not wi_test:
	print("FAILED: update")

wrf_inventory_test.csv_export('test/wrf_inventory.csv')

wi_test = wi_test and ( wrf_inventory_test.get_ids() == ['1','2','3'] )
if not wi_test:
	print("FAILED: get_ids")
wi_test = wi_test and ( wrf_inventory_test.get_shots('3') == 5 )
if not wi_test:
	print("FAILED: get_shots")
wi_test = wi_test and ( wrf_inventory_test.get_status('2') == 'active')
if not wi_test:
	print("FAILED: get_status")

if verbose:
	print(wrf_inventory_test.get_ids())
	print(wrf_inventory_test.get_shots('3'))
	print(wrf_inventory_test.get_status('2'))

if wi_test:
	print('PASSED')
else:
	print('FAILED')



# ------------------------------------
#		WRF SETUP TESTS
# ------------------------------------
print('---------------')
print('Testing wrf setup')
from WRF_Setup_DB import *

wrf_setup = WRF_Setup_DB(Database.FILE_TEST)
wrf_setup.clear()
wrf_setup.insert('N130227-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','90-78',50,'Generic',1,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
wrf_setup.insert('N130228-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','90-78',50,'Generic',2,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
wrf_setup.insert('N130229-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','90-78',50,'Generic',3,'13425857','13511730','13511716','',100,'','32:40:00','0:34:00')
wrf_setup.insert('N130229-001-999','AAA10-108020-10','I_Shap_2DConA_Lgth_S05','90-78',50,'Generic',3,'foo','13511730','13511716','',100,'','32:40:00','0:34:00')
wrf_setup.update('N130229-001-999','90-78','Generic',3,'wrf_id','12345')
wrf_setup.update('N130229-001-999','90-78','Generic',3,'cr39_1_id','12345')
wrf_setup.csv_export('test/wrf_setup.csv')

wrf_setup_test = True
wrf_setup_test = wrf_setup_test and ( wrf_setup.get_shots() == ['N130227-001-999', 'N130228-001-999', 'N130229-001-999'] )
if not wrf_setup_test:
	print("FAILED: get_shots")
wrf_setup_test = wrf_setup_test and ( wrf_setup.query('N130229-001-999') == [['N130229-001-999', 'AAA10-108020-10', 'I_Shap_2DConA_Lgth_S05', '90-78', 50.0, 'Generic', 3, '12345', '12345', '13511716', '', 100.0, '', '32:40:00', '0:34:00']] )
if not wrf_setup_test:
	print("FAILED: query")
wrf_setup_test = wrf_setup_test and ( wrf_setup.query_col('N130227-001-999',"wrf_id") == ['13425857'] )
if not wrf_setup_test:
	print("FAILED: query_col")
wrf_setup_test = wrf_setup_test and ( wrf_setup.find_wrf('13425857') == ['N130227-001-999','N130228-001-999'] )
if not wrf_setup_test:
	print("FAILED: find_wrf")
wrf_setup_test = wrf_setup_test and ( wrf_setup.find_cr39('13511730') == ['N130227-001-999','N130228-001-999'] )
if not wrf_setup_test:
	print("FAILED: find_cr39")

if verbose:
	print(wrf_setup.get_shots())
	print(wrf_setup.query('N130229-001-999'))
	print(wrf_setup.query_col('N130227-001-999',"wrf_id"))
	print(wrf_setup.find_wrf('13425857'))
	print(wrf_setup.find_cr39('13511730'))

if wrf_setup_test:
	print("PASSED")
else:
	print("FAILED")