from sqllex import *
from sqllex.debug import debug_mode
from sqllex.types import *
from os import remove
from time import sleep, time

DB_NAME = "temp_table.db"

DB_TEMPLATE: DBTemplateType = {
    "t1": {
        "text_t": TEXT,
        "num_t": NUMERIC,
        "int_t": INTEGER,
        "real_t": REAL,
        "none_t": NONE,
        "blob_t": BLOB,
    }
}

db = SQLite3x(path=DB_NAME)

debug_mode(True, log_file='sqllex-test.log')


def remove_db():
    print("Table removed")
    remove(f"{DB_NAME}")


def tables_test():
    db = SQLite3x(path=DB_NAME, template=DB_TEMPLATE)

    db.markup(
        {
            "groups": {
                "group_id": [PRIMARY_KEY, UNIQUE, INTEGER],
                "group_name": [TEXT, NOT_NULL, DEFAULT, "GroupName"],
            },

            "users": {
                "user_id": [INTEGER, PRIMARY_KEY, UNIQUE],
                "user_name": TEXT,
                "group_id": INTEGER,

                FOREIGN_KEY: {
                    "group_id": ["groups", "group_id"]
                },
            }
        }
    )

    db.create_table(
        "remove_me",
        {
            "xxx": [AUTOINCREMENT, INTEGER, PRIMARY_KEY],
            "yyy": [INTEGER],
        },
        IF_NOT_EXIST=True
    )

    for x in db.tables_names:
        if not (x in ['t1', 'groups', 'users', 'remove_me', 'sqlite_sequence']):
            print(db.tables_names)
            raise FileExistsError

    db.drop('remove_me')

    for x in db.tables_names:
        if not (x in ['t1', 'groups', 'users', 'sqlite_sequence']):
            print(db.tables_names)
            raise FileExistsError


def insert_test():
    # just arg values
    db.insert("t1", 'asdf', 10.0, 1, 3.14, None, 2)
    db["t1"].insert('asdf', 10.0, 1, 3.14, None, 2)

    # arg list
    db.insert("t1", ['asdf', 10.0, 1, 3.14, None, 2])
    db["t1"].insert(['asdf', 10.0, 1, 3.14, None, 2])

    # arg tuple
    db.insert("t1", ('asdf', 10.0, 1, 3.14, None, 2))
    db["t1"].insert(('asdf', 10.0, 1, 3.14, None, 2))

    # arg tuple
    db.insert("t1", {"text_t": 'asdf', "num_t": 10.0, "int_t": 1, "real_t": 3.14, "none_t": None, "blob_t": 2})
    db["t1"].insert({"text_t": 'asdf', "num_t": 10.0, "int_t": 1, "real_t": 3.14, "none_t": None, "blob_t": 2})

    # kwargs
    db.insert("t1", text_t='asdf', num_t=10.0, int_t=1, real_t=3.14, none_t=None, blob_t=2)
    db["t1"].insert(text_t='asdf', num_t=10.0, int_t=1, real_t=3.14, none_t=None, blob_t=2)

    if db.select_all('t1') == \
            db.select('t1') == \
            db.select('t1', ALL) == \
            db.select('t1', '*') == \
            db['t1'].select_all() == \
            db['t1'].select() == \
            db['t1'].select(ALL):
        sel_all = db.select_all('t1')
    else:
        raise FileExistsError

    if not sel_all == [['asdf', 10.0, 1, 3.14, None, 2]] * 10:
        print(sel_all)
        print([['asdf', 10.0, 1, 3.14, None, 2]] * 10)
        raise FileExistsError


def select_test():
    if not db.select('t1', 'text_t') == [['asdf']] * 10:
        print(db.select('t1', 'text_t'))
        raise FileExistsError

    if not db.select('t1', 'text_t', 'num_t') == [['asdf', 10.0]] * 10:
        print(db.select('t1', ['text_t', 'num_t']))
        raise FileExistsError

    db.insert('t1', ['qwerty1', 11.1, 2, 4.14, None, 5])
    db.insert('t1', ['qwerty2', 11.1, 2, 4.14, None, 6])

    # WHERE as dict
    if not db.select('t1', ['text_t', 'num_t'], WHERE={'num_t': 11.1}) == [['qwerty1', 11.1], ['qwerty2', 11.1]]:
        print(db.select('t1', ['text_t', 'num_t'], WHERE={'num_t': 11.1}))
        raise FileExistsError

    # WHERE as dict
    if not db.select('t1', 'text_t', 'num_t', WHERE={'num_t': ['=', 11.1], 'blob_t': ['<=', 5]}) == [['qwerty1', 11.1]]:
        print(db.select('t1', ['text_t', 'num_t'], WHERE={'num_t': 11.1, 'blob_t': 5}))
        raise FileExistsError

    # WHERE as kwarg
    if not db.select('t1', ['text_t', 'num_t'], num_t=11.1) == [['qwerty1', 11.1], ['qwerty2', 11.1]]:
        print(db.select('t1', ['text_t', 'num_t'], num_t=11.1))
        raise FileExistsError

    # WHERE as kwargs
    if not db.select('t1', 'text_t', 'num_t', num_t=11.1, blob_t=6) == [['qwerty2', 11.1]]:
        print(db.select('t1', 'text_t', 'num_t', num_t=11.1, blob_t=6))
        raise FileExistsError

    # LIMIT test
    if not db.select('t1', text_t='asdf', LIMIT=5) == [['asdf', 10.0, 1, 3.14, None, 2]] * 5:
        print(db.select('t1', text_t='asdf', LIMIT=5))
        raise FileExistsError

    # OFFSET
    if not db.select('t1', text_t='asdf', LIMIT=5, OFFSET=6) == [['asdf', 10.0, 1, 3.14, None, 2]] * 4:
        print(db.select('t1', text_t='asdf', LIMIT=5, OFFSET=6))
        raise FileExistsError

    db.create_table(
        "t2",
        {
            "id": [AUTOINCREMENT, INTEGER, PRIMARY_KEY],
            "value": [INTEGER, DEFAULT, 8],
        },
    )

    db.insertmany('t2', [[1], [2], [3], [4]])

    # ORDER_BY ASC
    if not db.select('t2', 'id', ORDER_BY='id ASC') == [[1], [2], [3], [4]]:
        print(db.select('t2', 'id', ORDER_BY='id ASC'))
        raise FileExistsError

    # ORDER_BY DESC
    if not db.select('t2', 'id', ORDER_BY='id DESC') == [[4], [3], [2], [1]]:
        print(db.select('t2', 'id', ORDER_BY='id DESC'))
        raise FileExistsError

    # WITH & WHERE
    if not db.select(
            'xxx',
            WITH={
                'xxx': db.select('t2', 'MAX(id)', execute=False)
            }
    ) == [[4]]:
        print(db.select(
            'xxx',
            WITH={
                'xxx': db.select('t2', 'MAX(id)', execute=False)
            }
        ))
        raise FileExistsError

    if not db.select(
            't2',
            WHERE={
                'id': ['<', 3]
            },
    ) == [[1, 8], [2, 8]]:
        print(db.select('t2', WHERE={'id': ['<', 3]}))
        raise FileExistsError

    # JOIN
    if not db.select(
            't2',
            'id',
            JOIN=[
                [CROSS_JOIN, 't1', AS, 't', ON, 't.num_t > t2.value']
            ]
    ) == [
               [1], [1], [1], [1], [1], [1], [1], [1], [1], [1], [1], [1],
               [2], [2], [2], [2], [2], [2], [2], [2], [2], [2], [2], [2],
               [3], [3], [3], [3], [3], [3], [3], [3], [3], [3], [3], [3],
               [4], [4], [4], [4], [4], [4], [4], [4], [4], [4], [4], [4]
           ]:
        print(db.select('t2', 'id', JOIN=[[CROSS_JOIN, 't1', AS, 't', ON, 't.num_t > t2.value']]))
        raise FileExistsError


def insertmany_test():
    db.create_table(
        't3',
        {
            'id': [INTEGER, NOT_NULL],
            'val': [TEXT, DEFAULT, 'NO']
        }
    )

    db.insertmany('t3', [[1, 'hi']] * 100)
    db.insertmany('t3', [[1]] * 100)
    db.insertmany('t3', ((1, 'hi'),) * 100)
    db.insertmany('t3', ((1,),) * 100)
    db.insertmany('t3', id=[2] * 10)
    db.insertmany('t3', id=(2,) * 10)


def update_test():
    db.create_table(
        't4',
        {
            'id': [INTEGER, NOT_NULL],
            'val': [TEXT, DEFAULT, 'NO']
        }
    )

    db.insertmany('t4', [[x, bin(x)] for x in range(100)])

    db.update(
        't4',
        {'val': 'NEW_VAL'},
        WHERE={
            'id': ['<', 50]
        }
    )

    if not db.select('t4', 'id', WHERE={"val": 'NEW_VAL'}) == [[x] for x in range(50)]:
        print(db.select('t4', 'id', WHERE={"val": 'NEW_VAL'}))
        raise FileExistsError


def delete_test():
    db.delete('t4', id=['<', 50])

    if not db.select('t4', 'id', WHERE={"val": 'NEW_VAL'}) == []:
        print(db.select_all('t4'))
        raise FileExistsError


def replace_test():
    db.create_table(
        't5',
        {
            'id': [INTEGER, UNIQUE, NOT_NULL],
            'val': [TEXT, DEFAULT, '_x_']
        }
    )

    db.insertmany('t5', [[x, ] for x in range(100)])

    db.replace('t5', [99, 'O_O'])

    if not db.select('t5', val='O_O') == [[99, 'O_O']]:
        print(db.select('t5', val='O_O'))
        raise FileExistsError


def get_tables_test():
    if "<generator object SQLite3x._get_tables_" not in str(db.tables):
        print(db.tables)
        raise FileExistsError

    for table in db.tables:
        if table.name not in ['t1', 'groups', 'users', 'sqlite_sequence', 't2', 't3', 't4', 't5']:
            print(table)
            raise FileExistsError

    for table in db.tables:
        if table.name not in ['t1', 'groups', 'users', 'sqlite_sequence', 't2', 't3', 't4', 't5']:
            print(table)
            raise FileExistsError

    for name in db.tables_names:
        if name not in ['t1', 'groups', 'users', 'sqlite_sequence', 't2', 't3', 't4', 't5']:
            print(name)
            raise FileExistsError


# Start time counting
t = time()

# Connection
db.connect()

# Testes
tables_test()
insert_test()
select_test()
insertmany_test()
update_test()
delete_test()
replace_test()
get_tables_test()

# Disconnect
db.disconnect()

# Time counting
t = time() - t

# Little sleep and printing
sleep(0.1)
print(t)

# Remove db
remove_db()
