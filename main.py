import string

import numpy as np
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
        if macd[i - 1] < signal[i - 1] and (macd[i] > signal[i]):
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

def trading_simulation(dates: [], prices: [], signals: dict, initial_capital: float) -> float:
    capital = initial_capital
    shares = 0

    for date, action in signals.items():
        index = dates.index(date)
        price = prices[index]

        if action == "buy":
            if capital > 0:
                shares_to_buy = capital / price
                capital -= shares_to_buy * price
                shares += shares_to_buy
        elif action == "sell":
            if shares > 0:
                capital += shares * price
                shares = 0

    if shares > 0:
        capital += shares * prices[-1]

    return capital

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

    simulation_res = trading_simulation(dates, closing_prices, trade_signals, 1000.0)
    print(f"After simulation value: {simulation_res:.2f}")