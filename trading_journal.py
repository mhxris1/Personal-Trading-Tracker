import os

def get_stored_shares(line):
    y = (line.split(",")[0]).strip()
    z = (y.split(":")[2]).strip()
    return float(z)

def get_investment(line):
    y = (line.split(",")[1]).strip()
    z = (y.split("$")[1]).strip()
    return float(z)


journal_running = True
portfolio = {}
trade_history = []

if not os.path.exists("Trading Portfolio"):
    with open("Trading Portfolio", "w") as f:
        pass  

try:
    with open("Trading Portfolio", "r") as f:
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


print("\nWelcome to My Trading Journal")
print("-----------------------------")
print("1. Add a Trade\n2.Sell Stock\n3.View Portfolio\n4.View Trade History\n5.Exit\n")

while journal_running:

    # Get user choice
    while True:
        try:
            choose_option = int(input("Choose an option (1-5): "))
            if choose_option in range(1, 6):
                break
            else:
                print("Enter a number between 1 and 5")
        except ValueError:
            print("Invalid input. Enter a number.")

    # Option 1: Buy
    if choose_option == 1:

        while True:
            stock_sticker = input("Enter Stock Sticker: ").upper().strip()
            if stock_sticker.isalpha() and len(stock_sticker) > 0:
                break
            print("Invalid Stock Sticker. Please use only letters")

        while True:
            try:
                number_of_shares = float(input("Enter number of Shares: "))
                if number_of_shares <= 0:
                    raise ValueError("Number of shares must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        while True:
            try:
                buy_price_per_share = float(input("Enter buy price per share: "))
                if buy_price_per_share <= 0:
                    raise ValueError("Price must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        price_of_trade = round(buy_price_per_share * number_of_shares, 2)
        new_trade = {
            "Type": "Buy",
            "Stock": stock_sticker,
            "Shares": number_of_shares,
            "Price": price_of_trade
        }
        trade_history.append(new_trade)

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

    # Option 2: Sell
    elif choose_option == 2:

        while True:
            stock_sticker = input("Enter Stock Sticker: ").upper().strip()
            if stock_sticker.isalpha() and len(stock_sticker) > 0:
                break
            print("Invalid Stock Sticker. Please use only letters")

        while True:
            try:
                number_of_shares = float(input("Enter number of Shares: "))
                if number_of_shares <= 0:
                    raise ValueError("Number of shares must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        while True:
            try:
                sell_price_per_share = float(input("Enter sell price per share: "))
                if sell_price_per_share <= 0:
                    raise ValueError("Price must be positive.")
                break
            except ValueError as e:
                print(f"Invalid input: {e}")

        price_of_trade = round(sell_price_per_share * number_of_shares, 2)

        if stock_sticker not in portfolio:
            print("You don't own any shares of this stock.\n")
        elif number_of_shares > portfolio[stock_sticker]["Total Shares"]:
            print("Not enough shares to sell.")
        else:
            average_price = portfolio[stock_sticker]["Average Price"]
            total_shares = portfolio[stock_sticker]["Total Shares"] - number_of_shares
            total_investment = portfolio[stock_sticker]["Total investment"] - number_of_shares * average_price

            if total_shares > 0:
                portfolio[stock_sticker]["Total Shares"] = total_shares
                portfolio[stock_sticker]["Total investment"] = round(total_investment, 2)
                portfolio[stock_sticker]["Average Price"] = round(total_investment / total_shares, 2)
            else:
                del portfolio[stock_sticker]

            new_trade = {
                "Type": "Sell",
                "Stock": stock_sticker,
                "Shares": number_of_shares,
                "Price": price_of_trade
            }
            trade_history.append(new_trade)

    # Option 3: Portfolio Summary
    elif choose_option == 3:
        print("📊 Portfolio Summary")
        print("---------------------")

        for stock_sticker, value in portfolio.items():
            print(f"{stock_sticker}:Total Shares:{value['Total Shares']}, Total investment: ${value['Total investment']:.2f}, Average Price: ${value['Average Price']:.2f}\n")

    # Option 4: Trade History
    elif choose_option == 4:
        print("📝 Trade History")
        print("-----------------")
        for x in trade_history:
            if x["Type"] == "Buy":
                print(f"🟢You bought {x['Shares']} of {x['Stock']} for ${x['Price']:.2f}")
            else:
                print(f"🔴 Sold {x['Shares']} of {x['Stock']} for ${x['Price']:.2f}")

    # Option 5: Exit
    elif choose_option == 5:
        print("👋 Exiting Trading Journal. Goodbye!")
        journal_running = False

    else:
        print("Incorrect Input. Please enter the Number corresponding to your needs.")


# Save portfolio to file
try:
    with open("Trading Portfolio", "w") as f:
        for stock, val in portfolio.items():
            f.write(f"{stock}:Total Shares:{val['Total Shares']}, Total investment: ${val['Total investment']:.2f}, Average Price: ${val['Average Price']:.2f}\n")
except IOError as e:
    print(f"Error writing to file: {e}")
