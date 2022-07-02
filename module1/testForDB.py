import sqlite3


def test01():
    conn = sqlite3.connect('database.db')

    print("Opened database successfully")

    sql_seach = "SELECT * from corona_net;"
    cursor = conn.execute(sql_seach)
    id = 3
    for i in range(0, 16):
        for row in cursor:
            id = id + 1
            print("policy_id: {}".format(id))
            original_text = row[40]
            original_text = original_text.replace('\'', '\'\'')
            sql_insert = "INSERT INTO corona_net (policy_id, original_text) \
                      VALUES ({}, '{}');".format(id, original_text)

            try:
                conn.execute(sql_insert)
                conn.commit()
            except:
                print(original_text)
                conn.close()
                return


    print("Records created successfully")

    conn.close()


def test02():
    prolific_id= '6153cd6d2d8ea888dc6248a3'
    conn = sqlite3.connect('database.db')

    sql_insert = "INSERT INTO corona_net (prolific_id, original_text) \
                              VALUES ({}, '{}');".format(prolific_id, 'test')

    try:
        conn.execute(sql_insert)
        conn.commit()
    except Exception as e:
        print('Reason:', e)
        conn.close()
        return


    conn.close()


if __name__ == '__main__':
    test02()