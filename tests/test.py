import sqlite3


def init_db():
    con = sqlite3.connect('../db.sqlite3')
    cur = con.cursor()
    cur.execute("""create table font_dict(
                site_name varchar(255) not null,
                font_name varchar(255) not null,
                unicode varchar(10) not null,
                ture_string varchar(10)
                )""")
    con.commit()
    cur.close()


init_db()
