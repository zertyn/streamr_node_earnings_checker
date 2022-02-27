# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import requests as rq
from datetime import datetime

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

# EDIT HERE variable addresses -> enter your public node addresses here
addresses = ["","","","",""];
# EDIT HERE variable datetime -> mining start date (year, month, day, hour, minute). Check first mining reward code in https://streamr-dashboard.vercel.app/node
mining_start_datetime = datetime(2022, 2, 23, 0, 0)

personalnodes_url = "https://streamr-dashboard.vercel.app/node?address="
pricevalue_url = "https://coinmarketcap.com/currencies/streamr/"
accumulateddata = 0;
mining_time = datetime.now() - mining_start_datetime
mining_time_formatted = strfdelta(mining_time, "{days} days {hours} hours {minutes} minutes")
mining_days = mining_time.days
mining_hours, remainder = divmod(mining_time.seconds, 3600)

# loops through addresses and fetches total DATA acquired per node
for address in addresses:
    0 == 0;
    response = rq.get(personalnodes_url + address)
    soup = bs(response.content, 'html.parser')
    data_div = str(soup.find("div",attrs={"class","value svelte-f8rxn4"}))
    accumulateddata += float(data_div[(data_div.index('">') + 2):(data_div.index('</') - 5)])

# calculate revenue using Coinmarketcap current DATA worth
response = rq.get(pricevalue_url)
soup = bs(response.content, 'html.parser')
coinvalue_div = str(soup.find("div",attrs={"class","priceValue"}))
coin_value = float(coinvalue_div[(coinvalue_div.index('<span>') + 7):(coinvalue_div.index('</span>') - 1)])
rev_total = round(coin_value * accumulateddata, 2)
rev_day = round(rev_total / mining_days, 2)
rev_hour = round(rev_total / (mining_days * 24 + mining_hours), 2)

# prints all variables into a nice overview
print('\n############## STREAMR NODE EARNINGS ##############')
print(f'\n   Total time mined: {mining_time_formatted}')
print(f'\n          Accumulated coins: {round(accumulateddata, 2)} DATA')
print(f'               Total revenue: ${rev_total}')
print(f'          Average revenue per day: ${rev_day}')
print(f'          Average revenue per hour: ${rev_hour}')
print(f'\n##############  DATA VALUE: ${coin_value}  ##############')

input("Press Enter to continue...")

