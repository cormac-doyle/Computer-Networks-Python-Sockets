import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="123password",
    database="stockdb"
)
mycursor = mydb.cursor()

sqlFormula = "INSERT INTO stock (CategoryName, Product_id,ProductName,UnitsInStock) VALUES (%s, %s, %s, %s)"
stock = [ ("Beverage",1,"TeaBags",15),
("Beverage",2,"ColdDrinks",19),
]

mycursor.executemany(sqlFormula, stock)

mydb.commit()
