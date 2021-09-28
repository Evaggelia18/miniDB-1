from database import Database
from btree import Btree

# create db with name "smdb"
db = Database('vsmdb', load=False)
# create a single table named "classroom"
db.create_table('classroom', ['building', 'room_number', 'capacity'], [str,str,int])
# insert 5 rows
db.insert('classroom', ['Packard', '101', '500'])
db.insert('classroom', ['Painter', '514', '10'])
db.insert('classroom', ['Taylor', '3128', '70'])
db.insert('classroom', ['Watson', '100', '30'])
db.insert('classroom', ['Watson', '120', '50'])

bt = Btree(3)
bt.insert(5, 0)
bt.insert(12, 1)
bt.insert(7, 2)
bt.insert(3, 3)
bt.insert(2, 4)
bt.insert(9, 5)
