import mysql.connector
from datetime import datetime

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='qg03cos1',
    database='data'
)

myCursor = db.cursor()

# myCursor.execute(
#     '''
#     CREATE TABLE Person (
#     name VARCHAR(50),
#     age smallint UNSIGNED,
#     personID int PRIMARY KEY AUTO_INCREMENT)
#     '''
# )

# myCursor.execute(
# "INSERT INTO Person (name, age) VALUES (%s,%s)", ('Manos', 23))
# db.commit()

# myCursor.execute("INSERT INTO Person (name, age) VALUES (%s,%s)", ('Elia', 26))
# db.commit()

#myCursor.execute("SELECT * FROM Person")
# for x in myCursor: ##myCursor is now an iterable object!
#   print(x)

# myCursor.execute(
#     '''
#     CREATE TABLE Random (
#     name VARCHAR(50) NOT NULL,
#     created datetime, # Python datetime object
#     gender ENUM('M', 'F'),
#     id int PRIMARY KEY AUTO_INCREMENT
#     )
#     ''')

# myCursor.execute("INSERT INTO Random (name, created, gender) VALUES (%s, %s, %s)",
#                  ("Nikos", datetime.now(), "M"))
# myCursor.execute("INSERT INTO Random (name, created, gender) VALUES (%s, %s, %s)",
#                  ("Lena", datetime.now(), "F"))
# myCursor.execute("INSERT INTO Random (name, created, gender) VALUES (%s, %s, %s)",
#                  ("Yvet", datetime.now(), "F"))
# db.commit()

# myCursor.execute("ALTER TABLE Random ADD COLUMN food VARCHAR(50)")

# myCursor.execute("DESCRIBE Random")

# for x in myCursor:
#     print(x)

users = [('Manos', 'manos1997'),
         ('Stella', 'stella2000'),
         ('Tasvak', 'tasvak2000')]

scores = [(55, 22),
          (27, 38),
          (32, 47)]

Q1 = "CREATE TABLE Users (id int PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50), passwd VARCHAR(50))"
Q2 = "CREATE TABLE Scores (userID int PRIMARY KEY, FOREIGN KEY(userID) REFERENCES Users(id), game1 int DEFAULT 0, game2 int DEFAULT 0)"

myCursor.execute(Q1)
myCursor.execute(Q2)

myCursor.executemany("INSERT INTO Users (name, passwd) VALUES (%s, %s)", users)
db.commit()

myCursor.execute("SELECT * FROM Users")

for x in myCursor:
    print(x)
