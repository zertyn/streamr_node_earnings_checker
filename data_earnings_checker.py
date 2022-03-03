# -*- coding: utf-8 -*-
"""
Created on Mon Feb 28 11:39:52 2022

@author: Zertyn
Intellectual property of @author
Donations are very welcome (DATA, ETH): 0x720D3842198A21403482C919841B81958B5220e1 (Polygon and Etherium chain)
"""

import requests as rq
from datetime import datetime
import json
from apscheduler.schedulers.blocking import BlockingScheduler


# function to transform timedelta to propper formatting
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


with open('nodes.json', 'r') as f:
    addresses = json.load(f)

# optional: EDIT HERE variable script_frequency -> speed with which the script reruns (3600 -> script runs once per hour)
output_frequency = 3600

# initalization of basic variables
pricevalue_url = "https://min-api.cryptocompare.com/data/price?fsym=DATA&tsyms=USD"
rewards_url = "https://brubeck1.streamr.network:3013/datarewards/"
personalnodes_url = "https://brubeck1.streamr.network:3013/stats/"
networkstats_url = "https://brubeck1.streamr.network:3013/apy"
scheduler = BlockingScheduler()

# automatically fetches the first reward code datetime from the first node, to check how long you've been mining
response = rq.get(personalnodes_url + list(addresses.values())[0])
json_data = json.loads(response.text)
try:
    mining_start_datetime = datetime.strptime(json_data["claimedRewardCodes"][0]["claimTime"][:-5].replace("T", " "),
                                          "%Y-%m-%d %H:%M:%S")
except:
    print ('Make sure to enter your node addresses correctly in nodes.json!')
    exit()


def obtain_info():
    # (re)create empty variables and lists to store JSON data
    accumulated_data = 0;
    data_per_node = [];
    online_per_node = [];
    last_reward_per_node = [];
    claimpc_per_node = [];

    # calculates mining time in days and hours
    mining_time = datetime.now() - mining_start_datetime
    mining_time_formatted = strfdelta(mining_time, "{days} days {hours} hours {minutes} minutes")
    mining_days = mining_time.days
    mining_hours, remainder = divmod(mining_time.seconds, 3600)

    # loops through addresses and fetches total DATA acquired per node
    for key, value in addresses.items():

        # get accumulated data for all nodes using JSON
        response = rq.get(rewards_url + value)
        json_data = json.loads(response.text)

        try:
            data_per_node.append(float(json_data["DATA"]))
        except:
            data_per_node.append(float(0))
        try:
            accumulated_data += float(json_data["DATA"])
        except:
            accumulated_data += float(0)

        # get claimed rewards and reward datetime per node
        response = rq.get(personalnodes_url + value)
        json_data = json.loads(response.text)

        try:
            node_reward_datetime = datetime.strptime(
                json_data["claimedRewardCodes"][-1]["claimTime"][:-5].replace("T", " "), "%Y-%m-%d %H:%M:%S")
            last_reward_per_node.append(
                str(int((datetime.utcnow() - node_reward_datetime).seconds / 60)) + " minutes ago")

            # calculate simple estimate if node is still online
            if ((datetime.utcnow() - node_reward_datetime).seconds < 4500):
                online_per_node.append("Online")
            elif ((datetime.utcnow() - node_reward_datetime).seconds > 4500 and (
                    datetime.utcnow() - node_reward_datetime).seconds < 9000):
                online_per_node.append("Unknown")
            else:
                online_per_node.append("Offline?")

        except:
            last_reward_per_node.append("No rewards")
            online_per_node.append("Unknown - New to network")

        try:
            claimpc_per_node_formatted = str(round(float(json_data["claimPercentage"]), 5))
            claimpc_per_node.append(claimpc_per_node_formatted[2:4] + "." + claimpc_per_node_formatted[4:6] + "%")
        except:
            claimpc_per_node.append("00.00%")

    # calculate revenue using Cryptocompare current DATA worth
    response = rq.get(networkstats_url)
    json_data = json.loads(response.text)
    apy = round(float(json_data["24h-APY"]), 2)
    apr = round(float(json_data["24h-APR"]), 2)

    # get APR and APY
    response = rq.get(pricevalue_url)
    json_data = json.loads(response.text)
    coin_value = float(json_data["USD"])
    rev_total = round(coin_value * accumulated_data, 2)

    # average revenue per dag and hour, calculated from total revenue up to current date
    rev_day = round(rev_total / mining_days, 2)
    rev_hour = round(rev_total / (mining_days * 24 + mining_hours), 2)

    # average revenue per dag and hour, calculated from total revenue up to current date
    node_rev_day = round(
        (((data_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 24) * len(addresses.keys()), 2)
    node_rev_hour = round(
        (((data_per_node[0] * coin_value) / (mining_days * 24 + mining_hours))) * len(addresses.keys()), 2)

    # old estimates of monthly and yearly revenue, calculated from total revenue up to current date
    est_rev_month = round(rev_total / (mining_days * 24 + mining_hours) * 732, 2)
    est_rev_year = round(rev_total / (mining_days * 24 + mining_hours) * 8772, 2)

    # new estimates which calculate profits based on the profitability of your first node (assumes every node has equal DATA amount staked)
    node_est_rev_month = round(
        (((data_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 732) * len(addresses.keys()), 2)
    node_est_rev_year = round(
        (((data_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 8772) * len(addresses.keys()), 2)

    # prints all variables into a nice overview
    print('\n################# STREAMR NODE EARNINGS #################')
    print(f'################## {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ##################')
    print(f'\n      Total time mined: {mining_time_formatted}')
    print(f'                    Total nodes: {len(addresses)}')
    print('\n______________________ REVENUE __________________________')
    print(f'\n            Accumulated coins: {round(accumulated_data, 2)} DATA')
    print(f'                 Total revenue: ${rev_total}\n')

    print(f'  Average  | revenue per hour: {round(rev_hour / coin_value, 2)} DATA / ${rev_hour}')
    print(f'   based   | revenue per day:  {round(rev_day / coin_value, 2)} DATA / ${rev_day}\n')

    print(f'   Node    | revenue per hour: {round(node_rev_hour / coin_value, 2)} DATA / ${node_rev_hour}')
    print(f'   based   | revenue per day:  {round(node_rev_day / coin_value, 2)} DATA / ${node_rev_day}')

    print('\n_____________________ NODE STATS ________________________\n')

    for index, address in enumerate(addresses):
        print(
            f'    Node {index + 1} | Gathered:      {data_per_node[index]} DATA / ${round(data_per_node[index] * coin_value, 2)}')
        print(f'           | Status:        {online_per_node[index]}')
        print(f'           | Last reward:   {last_reward_per_node[index]}')
        print(f'           | Claims(%):     {claimpc_per_node[index]}\n')

    print('_____________________ ESTIMATES _________________________\n')

    print(f'  Average  | monthly revenue: {round(est_rev_month / coin_value, 2)} DATA / ${est_rev_month}')
    print(f'   based   | yearly revenue:  {round(est_rev_year / coin_value, 2)} DATA / ${est_rev_year}\n')

    print(f'   Node    | monthly revenue: {round(node_est_rev_month / coin_value, 2)} DATA / ${node_est_rev_month}')
    print(f'   based   | yearly revenue:  {round(node_est_rev_year / coin_value, 2)} DATA / ${node_est_rev_year}')

    print(f'\n############ APR: {apr}% ##### APY: {apy}% ############')
    print(f'################# DATA VALUE: ${coin_value} ##################')


# runs the function once on startup, after which the scheduler takes over
obtain_info()

# loops through obtain_info function once per set interval in variable script_frequency
scheduler.add_job(obtain_info, 'interval', seconds=output_frequency)
scheduler.start()
