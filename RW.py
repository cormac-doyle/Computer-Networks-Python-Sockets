stock = "[('Item ID,Item,Quantity',), ('1,eggs (dozen),15',), ('2,toilet roll (9 pack),3',), ('3,flour,11',)]"



print(stock[stock.find("('")+1 : stock.find("',)")])


