import sys
from table_setup import TableSetup


# USER = 'demo_system_dba'
# PASSWORD = 'alpine'
# HOST = '127.0.0.1'
# DATABASE = 'security_system'
# TABLE = 'demo_siem'


def main():
    # connection = {host, database, user, password}
    # host, database, user, password, table, rows
    connection = sys.argv[1]
    table = sys.argv[2]
    rows = int(sys.argv[3])

    table_setup = TableSetup(connection, table)
    table_setup.drop_table()
    table_setup.create_table()
    table_setup.populate_table(rows)


if __name__ == "__main__":
    main()