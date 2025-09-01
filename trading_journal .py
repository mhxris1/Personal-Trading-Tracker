
journal_running = True
portfolio={}

print("\nWelcome to My Trading Journal")
print("-----------------------------")
print("1. Add a Trade\n2. View Portfolio\n3.View Trade History\n4.Exit\n")

while journal_running==True:
    choose_option = int(input("Choose an option e.g (1,2,3 or 4): "))
    if choose_option==1:
        stock_sticker=input("Enter Stock Sticker: ")
        number_of_shares= int(input("Enter number of Shares you want to buy: "))
        buy_price_per_share=int(input("Enter buy price per share: "))
        if stock_sticker in portfolio:
            total_shares=portfolio[stock_sticker]["Total Shares"] + number_of_shares
            total_investement=portfolio[stock_sticker]["Total Investement"] + number_of_shares*buy_price_per_share
            portfolio[stock_sticker]["Total Shares"]=total_shares
            portfolio[stock_sticker]["Total Investement"]=total_investement
            portfolio[stock_sticker]["Average Price"]=total_investement/total_shares
       
        
        else:
            portfolio[stock_sticker] = {
                "Total Shares":number_of_shares,
                "Total Investement":number_of_shares*buy_price_per_share,
                "Average Price":buy_price_per_share
             }
            
    elif choose_option==2:
        print ("📊 Portfolio Summary")
        print("---------------------")
        for stock_sticker, value  in portfolio.items():
            print(f"{stock_sticker}:Total Shares:{value['Total Shares']}, Total Investement: ${value['Total Investement']:.2f}, Average Price: ${value['Average Price']:.2f}")
            print("\n")









