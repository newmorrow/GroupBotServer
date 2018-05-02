import pymysql

db = pymysql.connect("localhost","root","","furrends" )

cursor = db.cursor()

def getURL(location, keyWord) :
    sql = "SELECT * from grouped WHERE Location = '"+ location +"' AND Keyword ='"+keyWord+"' LIMIT 5"
    print(sql)
    cursor.execute(sql)
    results = cursor.fetchall()
    out = []
    for row in results:
        out.append(row[2])
    return out

def isLocation(location):
    sql = "SELECT * from groups WHERE location = '"+ location+"'"
    cursor.execute(sql)
    data = cursor.fetchone()
    if data == None:
        return False
    else:
        return True