import pymysql
connection = pymysql.connect(host='ancssc-db.mysql.database.azure.com',
                             user='ancssc@ancssc-db',
                             password='819UiC@Uj&$Z^GY',
                             db='team_36_db_do_not_touch',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)