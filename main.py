import string
import random

import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
import pandas as pd


def data_read(filename: string):
    df = pd.read_csv(filename, parse_dates=["Data"])
    return df["Data"], df["Zamkniecie"]

def ema(x: [], n: int) -> []:
    if len(x) < n:
        return [0.0] * len(x)

    alpha = 2 / (n + 1)
    ema_values = [sum(x[:n]) / n]

    for i in range(n, len(x)):
        ema_values.append(alpha * x[i] + (1 - alpha) * ema_values[-1])

    return ema_values

def macd(ema26: [], ema12: []) -> []:
    return [ema12[i] - ema26[i] for i in range(len(ema12))]

def generate_trade_signals(dates: list, macd: list, signal: list) -> dict:
    trade_signals = {}

    for i in range(1, len(macd)):
        if macd[i - 1] < signal[i - 1] and macd[i] > signal[i]:
            trade_signals[dates[i]] = "buy"

        elif macd[i - 1] > signal[i - 1] and macd[i] < signal[i]:
            trade_signals[dates[i]] = "sell"

    return trade_signals

def plot_data(dates: [], prices: [], name: string) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, label=name, color='b', linewidth=0.8)

    plt.title(name)
    plt.xlabel('Data')
    plt.ylabel('Wartość')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=30)
    plt.show()
    pass

def plot_macd_with_signals(macd: [], signal: [], dates: [], trade_signals: dict) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(dates, macd, label="MACD", color='r', linewidth=0.8)
    plt.plot(dates, signal, label="SIGNAL", color='b', linewidth=0.8)

    buy_dates = [date for date, action in trade_signals.items() if action == "buy"]
    sell_dates = [date for date, action in trade_signals.items() if action == "sell"]

    dates_list = list(dates)

    buy_values = [macd[dates_list.index(date)] for date in buy_dates]
    sell_values = [macd[dates_list.index(date)] for date in sell_dates]

    plt.scatter(buy_dates, buy_values, color='g', marker='^', label='Kupno')
    plt.scatter(sell_dates, sell_values, color='r', marker='v', label='Sprzedaż')

    plt.legend()
    plt.title("MACD, Signal & Transakcje")
    plt.xlabel("Okres")
    plt.ylabel("Wartość")
    plt.grid(True)
    plt.xticks(rotation=30)
    plt.show()

def plot_single_transaction_with_many_crossings(dates: [], macd: [], signal: [], trade_index, trade_signals: dict) -> None:
    trade_dates = list(trade_signals.keys())
    trade_pos = trade_dates.index(trade_index)

    start_index = max(0, trade_pos - 3)
    end_index = min(len(trade_dates) - 1, trade_pos + 4)

    selected_trade_dates = trade_dates[start_index:end_index + 1]

    selected_dates = [date for date in dates if date in selected_trade_dates]
    selected_macd = [macd[dates.index(date)] for date in selected_dates]
    selected_signal = [signal[dates.index(date)] for date in selected_dates]

    crossing_values = [macd[dates.index(date)] for date in selected_trade_dates if date != trade_index]
    selected_trade_dates.remove(trade_index)

    plt.figure(figsize=(10, 5))
    plt.plot(selected_dates, selected_macd, label="MACD", color='r')
    plt.plot(selected_dates, selected_signal, label="Signal", color='b')

    if trade_index in trade_signals:
        trade_date = dates.index(trade_index)
        trade_value = macd[trade_date]
        plt.scatter(trade_index, trade_value, color='g', s=100, marker='o', label='Punkt kupna-sprzedaży')

    plt.scatter(selected_trade_dates, crossing_values, color='black', s=75, marker='x', label='Punkty przecięć')

    plt.xlabel("Okres")
    plt.ylabel("Wartość")
    plt.title("MACD, Signal i punkt kupna-sprzedaży")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=30)

    plt.show()

def trading_simulation(dates: [], prices: [], signals: dict, initial_capital: float):
    capital = initial_capital * prices[0]
    shares = 0

    daily_shares = []
    daily_cash = []

    for date in dates:
        action = ""
        if date in signals.keys():
            action = signals[date]

        index = dates.index(date)
        price = prices[index]

        if action == "buy":
            if capital > 0:
                shares_to_buy = capital / price
                capital = 0
                shares += shares_to_buy
        elif action == "sell":
            if shares > 0:
                capital += shares * price
                shares = 0

        daily_shares.append(shares * price)
        daily_cash.append(capital)

    return daily_shares, daily_cash

def plot_simulation_results(dates, shares, cash) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(dates, cash, label='Gotówka', color='b', linewidth=0.75)
    plt.plot(dates, shares, label='Wartość akcji', color='r', linewidth=0.75)

    total = [cash[i] + shares[i] for i in range(len(cash))]
    plt.fill_between(dates, 0, cash, color='b', alpha=0.5)
    plt.fill_between(dates, cash, total, color='r', alpha=0.5)

    plt.title('Wartość portfela w czasie')
    plt.xlabel('Data')
    plt.ylabel('Wartość (PLN)')
    plt.grid(True)
    plt.legend(loc='best')

    formatter = mticker.StrMethodFormatter('{x:,.0f}')
    plt.gca().yaxis.set_major_formatter(formatter)
    max_value = max(max(shares), max(cash))
    plt.ylim(0, min(max_value * 1.1, 3000000))
    plt.xticks(rotation=30)

    plt.show()

def plot_prices_with_trading_points(dates: [], prices: [], signals: dict):
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, label="Wartość", color='b', linewidth=0.8)

    buy_dates = [date for date, action in signals.items() if action == "buy"]
    sell_dates = [date for date, action in signals.items() if action == "sell"]

    dates_list = list(dates)

    buy_values = [prices[dates_list.index(date)] for date in buy_dates]
    sell_values = [prices[dates_list.index(date)] for date in sell_dates]

    plt.scatter(buy_dates, buy_values, color='g', marker='^', label='Kupno')
    plt.scatter(sell_dates, sell_values, color='r', marker='v', label='Sprzedaż')

    plt.legend()
    plt.title("WIG 20 z transakcjami")
    plt.xlabel("Okres")
    plt.ylabel("Wartość")
    plt.grid(True)
    plt.xticks(rotation=30)
    plt.show()

def plot_trade_profits(cash: []):
    profits = []
    prev_cash = cash[0]
    next_profit = True

    for i in range(len(cash)):
        if cash[i] == prev_cash or cash[i] == 0:
            continue

        if next_profit:
            profits.append(cash[i] - prev_cash)
            next_profit = False
        else:
            prev_cash = cash[i]
            next_profit = True

    plt.figure(figsize=(10, 5))
    plt.bar(range(len(profits)), profits, color='blue')

    plt.xlabel("Numer transakcji")
    plt.ylabel("Wartość")
    plt.title("Zyski i straty z transakcji")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.2f}"))
    plt.show()

if __name__ == '__main__':
    dates, closing_prices = data_read('wig20.csv')
    ema12 = ema(closing_prices, 12)
    ema26 = ema(closing_prices, 26)
    macd = macd(ema12, ema26)
    signal = ema(macd, 9)
    macd = macd[8:]
    plot_data(dates, closing_prices, 'WIG20')

    dates = dates[33:].reset_index(drop=True).tolist()
    closing_prices = closing_prices[33:].reset_index(drop=True).tolist()

    trade_signals = generate_trade_signals(dates, macd, signal)
    plot_macd_with_signals(macd, signal, dates, trade_signals)
    plot_prices_with_trading_points(dates, closing_prices, trade_signals)

    shares_value, cash = trading_simulation(dates, closing_prices, trade_signals, 1000.0)
    plot_simulation_results(dates, shares_value, cash)
    index = list(trade_signals.keys())[26]
    plot_single_transaction_with_many_crossings(dates, macd, signal, index, trade_signals)

    index = list(trade_signals.keys())[44]
    plot_single_transaction_with_many_crossings(dates, macd, signal, index, trade_signals)

    plot_trade_profits(cash)