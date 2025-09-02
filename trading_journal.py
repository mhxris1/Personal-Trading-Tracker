def get_stored_shares(line):
     y=(line.split(",")[0]).strip()
     z=(y.split(":")[2]).strip()
     return int(z)

def get_investement(line):
       y=(line.split(",")[1]).strip()
       z=(y.split("$")[1]).strip()
       return float(z)





journal_running = True
portfolio={}
trade_history=[]
with open("Trading Portfolio", "r") as trading_portfolio:
    trade_data = trading_portfolio.readlines()
print(trade_data)

for x in trade_data:
    x=x.strip()
    stock_sticker=(x.split(":")[0]).strip()
    stored_shares=get_stored_shares(x)
    initial_investement=get_investement(x)
    average_price=initial_investement/stored_shares
    portfolio[stock_sticker]={
        "Total Shares":stored_shares,
        "Total Investement":initial_investement,
        "Average Price":average_price

    }







print("\nWelcome to My Trading Journal")
print("-----------------------------")
print("1. Add a Trade\n2.Sell Stock\n3.View Portfolio\n4.View Trade History\n5.Exit\n")

while journal_running==True:
    choose_option = int(input("Choose an option e.g (1,2,3 ,4 or 5): "))
    if choose_option==1:
        stock_sticker=input("Enter Stock Sticker: ")
        number_of_shares= int(input("Enter number of Shares you want to buy: "))
        buy_price_per_share=int(input("Enter buy price per share: "))
        price_of_trade= buy_price_per_share*number_of_shares
        new_trade={
                "Type":"Buy",
                "Stock":stock_sticker,
                "Shares":number_of_shares,
                "Price":price_of_trade
            }
        trade_history.append(new_trade)

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
        stock_sticker=input("Enter Stock Sticker: ")
        number_of_shares=int(input("Enter number of Shares you want to sell: "))
        sell_price_per_share=int(input("Enter sell price per share: "))
        price_of_trade=sell_price_per_share*number_of_shares

        if stock_sticker in portfolio and portfolio[stock_sticker]["Total Shares"] >= number_of_shares:

                average_price = portfolio[stock_sticker]["Average Price"]
                total_shares=portfolio[stock_sticker]["Total Shares"] - number_of_shares
                total_investement=portfolio[stock_sticker]["Total Investement"] - number_of_shares*average_price
                
                if total_shares > 0:
                     portfolio[stock_sticker]["Total Shares"] = total_shares
                     portfolio[stock_sticker]["Total Investement"] = total_investement
                     portfolio[stock_sticker]["Average Price"] = total_investement / total_shares
                else:
                    
                    del portfolio[stock_sticker]
                new_trade = {
                    "Type":"Sell",
                    "Stock": stock_sticker,
                    "Shares": number_of_shares,
                    "Price": price_of_trade
                }
                trade_history.append(new_trade)

        else:
            print("You dont own any shares of this stock.\n")
        
            
    elif choose_option==3:
        print ("📊 Portfolio Summary")
        print("---------------------")
        
        for stock_sticker, value  in portfolio.items():
            print(f"{stock_sticker}:Total Shares:{value['Total Shares']}, Total Investement: ${value['Total Investement']:.2f}, Average Price: ${value['Average Price']:.2f}\n")
           
        
        
    
    elif choose_option==4:
        print("📝 Trade History")
        print("-----------------")
        for x in trade_history:
            if x["Type"]=="Buy":
                 print(f"🟢You bought {x['Shares']} of {x['Stock']} for ${x['Price']:.2f}" )
            else:
                 print(f"🔴 Sold {x['Shares']} of {x['Stock']} for ${x['Price']:.2f}")


    elif choose_option==5:
        print("👋 Exiting Trading Journal. Goodbye!")
        journal_running=False

    else:
        print("Incorrect Input. Please enter the Number corresponding to your needs.")
    

trading_portfolio=open("Trading Portfolio","w")
for stock_sticker, value  in portfolio.items():
    trading_portfolio.write(f"{stock_sticker}:Total Shares:{value['Total Shares']}, Total Investement: ${value['Total Investement']:.2f}, Average Price: ${value['Average Price']:.2f}\n")
    
trading_portfolio.close()








