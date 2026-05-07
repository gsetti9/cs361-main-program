"""
Stock Watchlist Tracker
CS361- Sprint 1 / Milestone #1
"""

import json
import os
import time
import yfinance as yf


WATCHLIST_FILE = "watchlist.json"


# Load and save watchlist 

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return []


def save_watchlist(watchlist):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f)


# Look up a stock price

def fetch_price(ticker):
    """
    Returns (name, price, change_pct) for a ticker symbol.
    Raises an error if the ticker is invalid.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    name = info.get("longName") or info.get("shortName")
    price = info.get("currentPrice") or info.get("regularMarketPrice")

    if not name or not price:
        raise ValueError(f"'{ticker}' was not found. Check the spelling and try again.")

    prev_close = info.get("previousClose") or price
    change_pct = ((price - prev_close) / prev_close) * 100

    return name, round(price, 2), round(change_pct, 2)


# Main menu

def main_menu():
    """
    IH#1 - Banner explains what the app does and why to use it.
    IH#2 - Footer tells users data is local, so no privacy cost.
    IH#4 - Numbered menu is a familiar CLI pattern.
    IH#6 - All four options shown upfront before user picks one.
    """
    print()
    print("=" * 50)
    print("  Stock Watchlist Tracker")
    print("  Track stocks. Save locally. Stay alert!")
    print("=" * 50)
    print()
    print("  What would you like to do?")
    print()
    print("  [1]  Add a stock to your watchlist")
    print("  [2]  View watchlist and live prices")
    print("  [3]  Remove a stock from your watchlist")
    print("  [4]  Exit")
    print()
    print("  Your data is saved to watchlist.json")
    print("  No account needed. Stays on your machine.")
    print()

    while True:
        choice = input("  Enter choice (1-4): ").strip()
        if choice in ("1", "2", "3", "4"):
            return choice
        print("  Invalid choice. Please enter 1, 2, 3, or 4.")


# Add stock view 

def view_add_stock():
    """
    User story: Add Stock to Watchlist
    As a user, I want to add a stock to my watchlist so that I can keep track of it.

    IH#5 - 'back' lets users cancel at any time.
    IH#6 - Step-by-step instructions shown before user types anything.
    IH#7 - Two ways to exit: finish the action OR type 'back'.
    IH#4 - Familiar ticker format with an example shown.
    IH#1 - Confirmation shows the stock name and price.
    """
    print()
    print("── Add a Stock ──────────────────────────────────")
    print()
    print("  Here is how it works:")
    print("    Step 1: Type a ticker symbol (e.g. TSLA)")
    print("    Step 2: We check if it exists using Yahoo Finance")
    print("    Step 3: If it's valid, it gets saved to your watchlist")
    print()
    print("  Type 'back' at any time to return to the main menu.")
    print()

    watchlist = load_watchlist()

    while True:
        ticker_input = input("  Enter ticker (e.g. AAPL) or 'back': ").strip().upper()

        if ticker_input == "BACK":
            return

        if ticker_input == "":
            print("  Please enter a ticker symbol.")
            continue

        if ticker_input in watchlist:
            print(f"  {ticker_input} is already on your watchlist.")
            answer = input("  Try a different one? (y/n): ").strip().lower()
            if answer != "y":
                return
            continue

        print(f"  Looking up {ticker_input}...")

        # Responsiveness NFR: track how long the fetch takes
        start_time = time.time()

        try:
            name, price, change_pct = fetch_price(ticker_input)
            elapsed = time.time() - start_time
        except Exception as e:
            print(f"  Error: {e}")
            answer = input("  Try again? (y/n): ").strip().lower()
            if answer != "y":
                return
            continue

        print(f"  Found: {name} ({ticker_input}) - ${price}")
        print(f"  Price fetched in {round(elapsed, 1)} seconds")
        print()

        watchlist.append(ticker_input)
        save_watchlist(watchlist)

        print(f"  {ticker_input} has been added to your watchlist and saved.")
        print()

        answer = input("  Add another stock? (y/n): ").strip().lower()
        if answer != "y":
            return


# View watchlist

def view_watchlist():
    """
    User story: View Current Stock Price
    As a user, I want to see the current price of stocks on my watchlist
    so that I know how they are doing.

    IH#2 - Tells user fetch may take a few seconds (time cost).
    IH#3 - Summary shown by default; press [d] for more detail if wanted.
    IH#4 - Green/red labels match familiar finance conventions.
    IH#7 - [d] and [b] give two different paths.
    Reliability NFR - API failure shows friendly message, app does not crash.
    Responsiveness NFR - prices fetched and shown within 5 seconds each.
    """
    print()
    print("── Your Watchlist ───────────────────────────────")
    print()

    watchlist = load_watchlist()

    if len(watchlist) == 0:
        print("  Your watchlist is empty.")
        print("  Go to option [1] to add some stocks first.")
        print()
        input("  Press Enter to return to the main menu...")
        return

    print("  Fetching live prices (this may take a few seconds)..")
    print()

    # Fetch prices for every ticker and store results in a list
    results = []
    for ticker in watchlist:
        try:
            name, price, change_pct = fetch_price(ticker)
            results.append({
                "ticker": ticker,
                "name": name,
                "price": price,
                "change_pct": change_pct,
                "error": None
            })
        except Exception as e:
            # Reliability NFR: keep going even if one ticker fails
            results.append({
                "ticker": ticker,
                "name": "Unknown",
                "price": None,
                "change_pct": None,
                "error": str(e)
            })

    # Print each result
    print(f"  {'Ticker':<8}  {'Price':>10}  {'Change':>8}  Name")
    print("  " + "-" * 46)

    for r in results:
        if r["error"]:
            print(f"  {r['ticker']:<8}  {'N/A':>10}  {'N/A':>8}  Could not load price")
        else:
            # Show + or - in front of the change percentage
            if r["change_pct"] >= 0:
                change_label = f"+{r['change_pct']}%"
            else:
                change_label = f"{r['change_pct']}%"

            print(f"  {r['ticker']:<8}  ${r['price']:>9}  {change_label:>8}  {r['name'][:25]}")

    print()
    print(f"  Last updated: {time.strftime('%I:%M %p')}  |  Source: Yahoo Finance")
    print()

    # IH#3- let user decide if they want more info or not
    print("  [d]  View details for a specific stock")
    print("  [b]  Back to main menu")
    print()

    while True:
        action = input("  Enter choice (d/b): ").strip().lower()

        if action == "b":
            return

        elif action == "d":
            ticker_input = input("  Enter ticker to view details: ").strip().upper()

            # Find that ticker in the results list
            found = None
            for r in results:
                if r["ticker"] == ticker_input:
                    found = r
                    break

            if found is None:
                print(f"  {ticker_input} is not in your current results.")
            elif found["error"]:
                print(f"  Could not load details for {ticker_input}: {found['error']}")
            else:
                print()
                print(f"  {found['name']} ({found['ticker']})")
                print(f"  Price:  ${found['price']}")
                if found["change_pct"] >= 0:
                    print(f"  Change: +{found['change_pct']}% from previous close")
                else:
                    print(f"  Change: {found['change_pct']}% from previous close")
                print()

        else:
            print("  Please enter 'd' or 'b'.")


# Remove stock view

def view_remove_stock():
    """
    User story: Remove Stock from Watchlist
    As a user, I want to remove a stock from my watchlist
    so that I only see the ones I still care about.

    IH#3 - Watchlist shown before prompt so user has all the context.
    IH#5 - [n] cancels immediately; 'back' always available.
    IH#6 - Prompt shows what to type and how to cancel before user acts.
    IH#7 - Two ways to cancel: type 'back' OR press [n] at confirmation.
    IH#8 - Warning + y/n confirmation before removing anything.
    Reliability NFR - updated list saved to file right away.
    Usability NFR - watchlist shown so user can check spelling before typing.
    """
    print()
    print("── Remove a Stock ───────────────────────────────")
    print()

    watchlist = load_watchlist()

    if len(watchlist) == 0:
        print("  Your watchlist is empty. Nothing to remove.")
        print()
        input("  Press Enter to return to the main menu...")
        return

    # IH#3 - show watchlist so user knows what's there
    print("  Your current watchlist:")
    print(f"    {', '.join(watchlist)}")
    print()
    print("  Type 'back' at any time to return to the main menu.")
    print()

    while True:
        ticker_input = input("  Enter ticker to remove (e.g. TSLA) or 'back': ").strip().upper()

        if ticker_input == "BACK":
            return

        if ticker_input == "":
            print("  Please enter a ticker symbol.")
            continue

        if ticker_input not in watchlist:
            print(f"  {ticker_input} is not on your watchlist.")
            print(f"  Currently tracking: {', '.join(watchlist)}")
            answer = input("  Try again? (y/n): ").strip().lower()
            if answer != "y":
                return
            continue

        # IH#8 - warning before doing anything permanent
        print()
        print(f"  Are you sure you want to remove {ticker_input}?")
        print("  You can undo this by re-adding it using option [1].")
        print()
        confirm = input("  Confirm? [y] Yes   [n] No, go back: ").strip().lower()

        if confirm == "y":
            watchlist.remove(ticker_input)
            save_watchlist(watchlist)  # Reliability NFR: save right away

            print()
            print(f"  {ticker_input} has been removed. Watchlist saved.")

            if len(watchlist) > 0:
                print(f"  Remaining: {', '.join(watchlist)}")
            else:
                print("  Your watchlist is now empty.")

            print()
            input("  Press Enter to return to the main menu...")
            return

        else:
            # IH#5 - explicit backtrack, nothing was changed
            print(f"  Cancelled. {ticker_input} was not removed.")
            answer = input("  Remove a different stock? (y/n): ").strip().lower()
            if answer != "y":
                return


# Main loop 

def main():
    while True:
        choice = main_menu()

        if choice == "1":
            view_add_stock()
        elif choice == "2":
            view_watchlist()
        elif choice == "3":
            view_remove_stock()
        elif choice == "4":
            print()
            print("  Goodbye! Your watchlist is saved to watchlist.json.")
            print()
            break


if __name__ == "__main__":
    main()