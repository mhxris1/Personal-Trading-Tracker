import os
from tkinter.messagebox import NO
import yfinance as yf
from yahooquery import search
import threading
import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time


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

def get_menu_choice():
    while True:
        try:
            choice = int(input("Choose an option (1-6): "))
            if choice in range(1, 7):
                return choice
            else:
                print("Enter a number between 1 and 6")
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
    update_portfolio(portfolio, "Trading Portfolio")

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
    update_portfolio(portfolio, "Trading Portfolio")

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
        return float(data["Open"].iloc[-1])   
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
        return float(data["Close"].iloc[-1])  
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

def get_portfolio_value(portfolio):
        total_value = 0
        for ticker, details in portfolio.items():
            try:
                stock = yf.Ticker(ticker)
                data = stock.history(period="1d", interval="1m")
                if data.empty:
                    print(f"⚠ No price data for {ticker}. Skipping.")
                    continue
                latest_price = data["Close"].iloc[-1]
                details["Latest Price"] = round(latest_price, 2)
                details["Current Value"] = round(latest_price * details["Total Shares"], 2)

                total_value += details["Current Value"]
            except Exception as e:
                print(f"⚠ Error fetching data for {ticker}: {e}")
        return round(total_value, 2)

def save_portfolio(filename, portfolio):
    
    try:
        with open(filename, "w") as f:
            for stock, val in portfolio.items():
                f.write(
                    f"{stock}:Total Shares:{val['Total Shares']}, "
                    f"Total investment: ${val['Total investment']:.2f}, "
                    f"Average Price: ${val['Average Price']:.2f}, "
                    f"Latest Price: ${val.get('Latest Price', 0):.2f}, "
                    f"Current Value: ${val.get('Current Value', 0):.2f}\n"
                )
    except IOError as e:
        print(f"Error writing to file: {e}")

def update_portfolio(portfolio, filename="Trading Portfolio",interval=120):
    global stop_updates,update_thread
    if stop_updates:
        return
    total_value = get_portfolio_value(portfolio)
    timestamp = datetime.datetime.now()
    portfolio_history.append((timestamp, total_value))
    print(f"\n[{timestamp:%Y-%m-%d %H:%M:%S}] Total Portfolio Value: ${total_value}")
    save_portfolio(filename, portfolio)
    update_thread = threading.Timer(interval, update_portfolio, [portfolio, filename,interval])
    update_thread.start()

def plot_portfolio(portfolio_history):
    global ani, fig, ax  
    if not portfolio_history:
        print("No portfolio history to plot.")
        return
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))

    def update(frame):
        ax.clear()
        if portfolio_history:  # Re-check in case it grows
            timestamps, values = zip(*portfolio_history)
            ax.plot(timestamps, values, marker='x', linestyle='-', color='red')
            ax.set_title("Portfolio Value Over Time")
            ax.set_xlabel("Time")
            ax.set_ylabel("Total Portfolio Value ($)")
            plt.xticks(rotation=45)
            ax.grid(True)
            plt.tight_layout()
    ani = FuncAnimation(fig, update, interval=12000,cache_frame_data=False)
    plt.show(block=False)


stop_updates=False
update_thread=None
journal_running = True
ani=None
fig, ax=None, None
portfolio = load_portfolio("Trading Portfolio")
create_trade_log_file("Trade History")
portfolio_history = []
trade_history = []
update_portfolio(portfolio, "Trading Portfolio")
Api_Url=("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&")


print("\nWelcome to My Trading Journal")
print("-----------------------------")
print("1. Add a Trade\n2.Sell Stock\n3.View Portfolio\n4.View Trade History\n5.View Graph\n6.Exit\n")

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
    
    elif choose_option==5:
        plot_portfolio(portfolio_history)
        continue
    
    elif choose_option == 6:
        print("👋 Exiting Trading Journal. Goodbye!")
        journal_running = False
        stop_updates = True
        if update_thread is not None:
            update_thread.cancel()  
        break
        

    else:
        print("Incorrect Input. Please enter the Number corresponding to your needs.")



save_portfolio("Trading Portfolio", portfolio)
