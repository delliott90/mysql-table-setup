import mysql.connector
from mysql.connector import errorcode
import json
import random
import secrets


VARCHAR = "varchar(100)"
INT = "int"
DOUBLE = "double"

DATA_TYPES = {
    "system_name": VARCHAR,
    "source_ipaddr": VARCHAR,
    "dest_ipaddr": VARCHAR,
    "url": VARCHAR,
    "entry_time": DOUBLE,
    "source_port": INT,
    "dest_port": INT,
    "username": VARCHAR,
    "filename": VARCHAR,
    "protocol": VARCHAR,
    "sha256hash": VARCHAR,
    "md5hash": VARCHAR,
    "file_path": VARCHAR,
    "severity": INT
}

URL_SEGMENT = ["puppy", "cat", "dog", "express", "company", "canada", "usa", "two", "four"] 
URL_END = ["ca", "com", "biz", "net", "org"]
FILE_SEGMENT = ["photos", "appointment", "config", "spreadsheet", "WoW_installer", "calendar"]
FILE_END = ["exe", "ini", "dmg", "xml", "doc"]
EMAIL_END = ["gmail.com", "gmail.ca", "msn.com", "hotmail.com", "icloud.com", "sympatico.ca", "aol.com", "mac.com", "iwork.com"]
DIRECTORIES = ["C:/PHOTOS", "usr/bin", "user/preferences/lib"]
PROTOCOLS = ["tcp", "udp"]

TO_FIVE = [0, 1, 2, 3, 4, 5]
TO_FOUR = [0, 1, 2, 3, 4]
TO_NINE = [1, 2, 3, 4, 5, 6, 7, 8, 9]
TO_ONE = [1]


class TableSetup():

    def __init__(self, connection_params, table):
        self.connection_params = json.loads(connection_params)
        self.table = table

        self.ip_segment_choices = ["25{}".format(random.choice(TO_FIVE)), "2{}{}".format(random.choice(TO_FOUR), random.choice(TO_NINE)), "{}{}{}".format(random.choice(TO_ONE), random.choice(TO_NINE), random.choice(TO_NINE))]

    def __get_db_connection(self):
        return mysql.connector.connect(user=self.connection_params["user"], password=self.connection_params["password"], host=self.connection_params["host"], database=self.connection_params["database"])
    
    def __generate_ip(self, ip_count=1):
        ip_list = []
        count = ip_count
        while count > 0:
            ip_list.append(str(random.choice(self.ip_segment_choices)) + "." + str(random.choice(self.ip_segment_choices)) + "." + str(random.choice(self.ip_segment_choices)) + "." + str(random.choice(TO_NINE)))
            count -= 1
        return ip_list

        # \b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b

    def __generate_email(self):
        return "{}@{}".format(secrets.token_hex(nbytes=4), random.choice(EMAIL_END))

    def __generate_url(self):
        return "www.{}-{}.{}".format(random.choice(URL_SEGMENT), random.choice(URL_SEGMENT), random.choice(URL_END))

    def __generate_file(self):
        return "{}.{}".format(random.choice(FILE_SEGMENT), random.choice(FILE_END))

    def __give_random_int(self):
        return str(int(random()*10))

    # 32 for SHA-256, 16 for MD5
    def __generate_hash(self, number=32):
        return secrets.token_hex(nbytes=number)

    def __generate_file_dict(self, file_list):
        file_dict = {}
        hash_type = [16, 32]
        for file in file_list:
            file_dict[file] = self.__generate_hash(random.choice(hash_type))
        return file_dict

    def __handle_error(self, err):
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

    def drop_table(self):
        try:
            cnx = self.__get_db_connection()
            cursor = cnx.cursor()
            sql = "DROP TABLE IF EXISTS {}".format(self.table)
            cursor.execute(sql)
        except mysql.connector.Error as err:
            self.__handle_error(err)
        else:
            cnx.close()

    def create_table(self):
        try:
            mapping_file = open("from_stix_map.json", "r")
            json_map = json.load(mapping_file)
            cnx = self.__get_db_connection()
            cursor = cnx.cursor()
            fields_list = []
            for stix_object, value in json_map.items():
                for stix_property, fields_array in value["fields"].items():
                    for field in fields_array:
                        if field not in fields_list:
                            fields_list.append(field)

            fields_and_type = "("
            for field in fields_list:
                fields_and_type += "{} {}, ".format(field, DATA_TYPES.get(field, VARCHAR))
            fields_and_type = fields_and_type[:-2]
            fields_and_type += ")"

            sql = "CREATE TABLE {} {};".format(self.table, fields_and_type)
            cursor.execute(sql)
        except mysql.connector.Error as err:
            self.__handle_error(err)
        else:
            cnx.close()

    def populate_table(self, rows):
        USERS = ["root", "admin", "user", self.__generate_email(), self.__generate_email(), self.__generate_email()]
        IP_LIST = self.__generate_ip(4)
        FILE_LIST = [self.__generate_file(), self.__generate_file(), self.__generate_file(), self.__generate_file(), self.__generate_file()]
        FILE_DICT = self.__generate_file_dict(FILE_LIST)

        try:
            cnx = self.__get_db_connection()
            row_count = rows
            cursor = cnx.cursor()
            while row_count > 0:
                sql = "INSERT INTO {} (system_name, source_ipaddr, dest_ipaddr, url, entry_time, source_port, dest_port, username, filename, protocol, sha256hash, md5hash, file_path, severity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(self.table)

                file_name = random.choice(FILE_LIST)
                file_hash = FILE_DICT[file_name]
                if len(file_hash) == 32:
                    sha256 = None
                    md5 = file_hash
                else:
                    sha256 = file_hash
                    md5 = None
                val = ('demo_system', random.choice(IP_LIST), random.choice(IP_LIST), self.__generate_url(), 1617123877, 143, 8080, random.choice(USERS), file_name, random.choice(PROTOCOLS), sha256, md5, random.choice(DIRECTORIES), random.choice(TO_NINE))
                cursor.execute(sql, val)
                row_count -= 1

                cnx.commit()
        except mysql.connector.Error as err:
            self.__handle_error(err)
        else:
            cnx.close()