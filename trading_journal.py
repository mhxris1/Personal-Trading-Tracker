import os
import yfinance as yf
import requests
from yahooquery import search

def get_stored_shares(line):
    y = (line.split(",")[0]).strip()
    z = (y.split(":")[2]).strip()
    return float(z)

def get_investment(line):
    y = (line.split(",")[1]).strip()
    z = (y.split("$")[1]).strip()
    return float(z)

def load_portfolio(filename):
    portfolio = {}
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass
    try:
        with open(filename, "r") as f:
            trade_data = f.readlines()
    except FileNotFoundError:
        trade_data = []

    for x in trade_data:
        x = x.strip()
        if not x:
            continue
        stock_sticker = (x.split(":")[0]).strip()
        try:
            stored_shares = get_stored_shares(x)
            initial_investment = get_investment(x)
        except (IndexError, ValueError):
            print(f"Skipping invalid line: {x}")
            continue
        if stored_shares == 0:
            print(f"Skipping line with zero shares: {x}")
            continue
        average_price = initial_investment / stored_shares
        portfolio[stock_sticker] = {
            "Total Shares": stored_shares,
            "Total investment": initial_investment,
            "Average Price": average_price
        }
    return portfolio

def save_portfolio(filename, portfolio):
    try:
        with open(filename, "w") as f:
            for stock, val in portfolio.items():
                f.write(f"{stock}:Total Shares:{val['Total Shares']}, Total investment: ${val['Total investment']:.2f}, Average Price: ${val['Average Price']:.2f}\n")
    except IOError as e:
        print(f"Error writing to file: {e}")

def get_menu_choice():
    while True:
        try:
            choice = int(input("Choose an option (1-5): "))
            if choice in range(1, 6):
                return choice
            else:
                print("Enter a number between 1 and 5")
        except ValueError:
            print("Invalid input. Enter a number.")

def get_stock_input(prompt):
    while True:
        company = input(prompt).strip()
        stock=get_stock_sticker(company)
        if stock is not None:
            return stock
        print("⚠ Could not find a valid ticker. Please try again.")
           

def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                raise ValueError("Value must be positive.")
            return value
        except ValueError as e:
            print(f"Invalid input: {e}")

def process_buy(portfolio, trade_history):
    stock_sticker = get_stock_input("Enter a Company Name: ")
    number_of_shares = get_positive_float("Enter number of Shares: ")
    buy_price_per_share = get_buy_price(stock_sticker)
    if buy_price_per_share is None:
        return
    
    price_of_trade = round(buy_price_per_share * number_of_shares, 2)
    new_trade = {"Type":"Buy","Stock":stock_sticker,"Shares":number_of_shares,"Price":price_of_trade}
    trade_history.append(new_trade)
    log_trade("Trade History",new_trade)

    if stock_sticker in portfolio:
        total_shares = portfolio[stock_sticker]["Total Shares"] + number_of_shares
        total_investment = portfolio[stock_sticker]["Total investment"] + number_of_shares * buy_price_per_share
        portfolio[stock_sticker]["Total Shares"] = total_shares
        portfolio[stock_sticker]["Total investment"] = round(total_investment, 2)
        portfolio[stock_sticker]["Average Price"] = round(total_investment / total_shares, 2)
    else:
        portfolio[stock_sticker] = {
            "Total Shares": number_of_shares,
            "Total investment": number_of_shares * buy_price_per_share,
            "Average Price": buy_price_per_share
        }

def process_sell(portfolio, trade_history):
    stock_sticker = get_stock_input("Enter a Company Name: ")
    number_of_shares = get_positive_float("Enter number of Shares: ")
    sell_price_per_share = get_sell_price(stock_sticker)
    if sell_price_per_share is None:
        return
    
    price_of_trade = round(sell_price_per_share * number_of_shares, 2)

    if stock_sticker not in portfolio:
        print("You don't own any shares of this stock.\n")
        return
    elif number_of_shares > portfolio[stock_sticker]["Total Shares"]:
        print("Not enough shares to sell.")
        return

    average_price = portfolio[stock_sticker]["Average Price"]
    total_shares = portfolio[stock_sticker]["Total Shares"] - number_of_shares
    total_investment = portfolio[stock_sticker]["Total investment"] - number_of_shares * average_price

    if total_shares > 0:
        portfolio[stock_sticker]["Total Shares"] = total_shares
        portfolio[stock_sticker]["Total investment"] = round(total_investment, 2)
        portfolio[stock_sticker]["Average Price"] = round(total_investment / total_shares, 2)
    else:
        del portfolio[stock_sticker]

    new_trade=({"Type":"Sell","Stock":stock_sticker,"Shares":number_of_shares,"Price":price_of_trade})
    trade_history.append(new_trade)
    log_trade("Trade History",new_trade)

def display_portfolio(portfolio):
    print("📊 Portfolio Summary")
    print("---------------------")
    for stock_sticker, value in portfolio.items():
        print(f"{stock_sticker}:Total Shares:{value['Total Shares']}, Total investment: ${value['Total investment']:.2f}, Average Price: ${value['Average Price']:.2f}\n")

def display_trade_history(trade_history):
    print("📝 Trade History")
    print("-----------------")
    for trade in trade_history:
        if trade["Type"] == "Buy":
            print(f"🟢You bought {trade['Shares']} of {trade['Stock']} for ${trade['Price']:.2f}")
        else:
            print(f"🔴 Sold {trade['Shares']} of {trade['Stock']} for ${trade['Price']:.2f}")

def create_trade_log_file(filename):

     if not os.path.exists(filename):
        with open(filename, "w") as f:
            pass

def log_trade(filename,trade):
    try:
        with open(filename, "a") as f:
            f.write(f"{trade['Type']},{trade['Stock']},{trade['Shares']},{trade['Price']:.2f}\n")
    except IOError as e:
        print(f"Error writing to trade log: {e}")

def get_buy_price(name):
    try:
        ticker = yf.Ticker(name)
        data = ticker.history(period="1d")
        if data.empty:
            print(f"⚠ No data found for {name}.")
            return None
        return float(data["Open"].iloc[-1])   # Buy at market open
    except Exception as e:
        print(f"⚠ Error fetching buy price for {name}: {e}")
        return None

def get_sell_price(name):
   try:
        ticker = yf.Ticker(name)
        data = ticker.history(period="1d")
        if data.empty:
            print(f"⚠ No data found for {name}.")
            return None
        return float(data["Close"].iloc[-1])  # Sell at market close
   except Exception as e:
        print(f"⚠ Error fetching sell price for {name}: {e}")
        return None

def get_stock_sticker(company_name):

    try:
        results = search(company_name)
        quotes = results.get("quotes", [])
        if not quotes:
            print(f"⚠ No ticker found for {company_name}.")
            return None

        
        ticker = quotes[0].get("symbol")
        if ticker:
            return ticker.upper()
        else:
            print(f"⚠ Could not extract ticker for {company_name}.")
            return None
    except Exception as e:
        print(f"⚠ Error searching for {company_name}: {e}")
        return None





journal_running = True
portfolio = load_portfolio("Trading Portfolio")
create_trade_log_file("Trade History")
trade_history = []
Api_Url=("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&")


print("\nWelcome to My Trading Journal")
print("-----------------------------")
print("1. Add a Trade\n2.Sell Stock\n3.View Portfolio\n4.View Trade History\n5.Exit\n")

while journal_running:
    choose_option=get_menu_choice()
  
    if choose_option == 1:
        process_buy(portfolio, trade_history)
        
   
    elif choose_option == 2:
        process_sell(portfolio,trade_history)

    elif choose_option == 3:
        display_portfolio(portfolio)
        
    elif choose_option == 4:
       display_trade_history(trade_history)
    
    elif choose_option == 5:
        print("👋 Exiting Trading Journal. Goodbye!")
        journal_running = False

    else:
        print("Incorrect Input. Please enter the Number corresponding to your needs.")



save_portfolio("Trading Portfolio", portfolio)
