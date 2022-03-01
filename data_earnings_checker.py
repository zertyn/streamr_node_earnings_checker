# -*- coding: utf-8 -*-

import requests as rq
from datetime import datetime
import json
from apscheduler.schedulers.blocking import BlockingScheduler

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

# EDIT HERE variable addresses -> enter your public node addresses here
addresses = ["node_address_x","node_address_y","node_address_z"]

# EDIT HERE variable datetime -> mining start date (year, month, day, hour, minute). Check first mining reward code in https://streamr-dashboard.vercel.app/node
mining_start_datetime = datetime(2022, 2, 23, 0, 0)

# optional: EDIT HERE variable script_frequency -> speed with which the script reruns (3600 -> script runs once per hour)
script_frequency = 3600

# initalization of basic variables
pricevalue_url = "https://min-api.cryptocompare.com/data/price?fsym=DATA&tsyms=USD"
rewardendpoint_url = "https://brubeck1.streamr.network:3013/datarewards/"
personalnodes_url = "https://brubeck1.streamr.network:3013/stats/"
mining_time = datetime.now() - mining_start_datetime
mining_time_formatted = strfdelta(mining_time, "{days} days {hours} hours {minutes} minutes")
mining_days = mining_time.days
mining_hours, remainder = divmod(mining_time.seconds, 3600)
scheduler = BlockingScheduler()

def obtain_info():
    accumulated_data = 0;
    data_per_node = [];
    online_per_node = [];
    last_reward_per_node = [];
    claimpc_per_node = [];
    
	# loops through addresses and fetches total DATA acquired per node
    for address in addresses:
        
        response = rq.get(rewardendpoint_url + address)
        json_data = json.loads(response.text)
        data_per_node.append(float(json_data["DATA"]))
        accumulated_data += float(json_data["DATA"])
        
        response = rq.get(personalnodes_url + address)
        json_data = json.loads(response.text)
        node_reward_datetime = datetime.strptime(json_data["claimedRewardCodes"][-1]["claimTime"][:-5].replace("T"," "), "%Y-%m-%d %H:%M:%S")
        claimpc_per_node_formatted = str(round(float(json_data["claimPercentage"]),5))
        claimpc_per_node.append(claimpc_per_node_formatted[2:4] + "." + claimpc_per_node_formatted[4:6] + "%")
        last_reward_per_node.append((datetime.utcnow() - node_reward_datetime).seconds)
        
        if ((datetime.utcnow() - node_reward_datetime).seconds < 4500):         
            online_per_node.append("Online")
        else: 
            online_per_node.append("Offline")
        
    # calculate revenue using Cryptocompare current DATA worth
    response = rq.get(pricevalue_url)
    json_data = json.loads(response.text)
    coin_value = float(json_data["USD"])

    rev_total = round(coin_value * accumulated_data, 2)
    rev_day = round(rev_total / mining_days, 2)
    rev_hour = round(rev_total / (mining_days * 24 + mining_hours), 2)
    est_rev_month = round(rev_total / (mining_days * 24 + mining_hours) * 720, 2)
    est_rev_year = round(rev_total / (mining_days * 24 + mining_hours) * 8760, 2)

# prints all variables into a nice overview
    print('\n################ STREAMR NODE EARNINGS ################')
    print(f'################# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} #################')
    print(f'\n     Total time mined: {mining_time_formatted}')
    print(f'                    Total nodes: {len(addresses)}')
    print('\n_____________________ REVENUE _________________________')
    print(f'\n            Accumulated coins: {round(accumulated_data, 2)} DATA')
    print(f'                 Total revenue: ${rev_total}')
    print(f'            Average revenue per day: ${rev_day}')
    print(f'            Average revenue per hour: ${rev_hour}')
    print('\n____________________ NODE STATS _______________________\n')

    for index, address in enumerate(addresses):
        print(f'        Node {index + 1} | Gathered:      {data_per_node[index]} DATA')
        print(f'               | Status:        {online_per_node[index]}')
        print(f'               | Last reward:   {int(last_reward_per_node[index] / 60)} minutes ago')
        print(f'               | Claims(%):     {claimpc_per_node[index]}\n')
        
    print('____________________ ESTIMATES ________________________\n')
    print(f'  Estimated monthly revenue: ${est_rev_month} or { round(est_rev_month / coin_value, 2)} DATA')
    print(f'  Estimated yearly revenue: ${est_rev_year} or { round(est_rev_year / coin_value ,2)} DATA')
    print(f'\n################ DATA VALUE: ${coin_value} #################')

obtain_info()
scheduler.add_job(obtain_info, 'interval', seconds = script_frequency)
scheduler.start()
