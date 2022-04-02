# -*- coding: utf-8 -*-

"""
Created on Mon Feb 28 11:39:52 2022
Last update on Mon Mar 7 16:12:15 2022

@author: Zertyn
Intellectual property of Zertyn
Donations are very welcome (DATA, MATIC, ETH): 0xfdE5EbC9A5E3B770359eF8e4155d08FB2fd3aB92 (Polygon and Etherium chain)
"""

import requests as rq
from datetime import datetime
import json
from apscheduler.schedulers.blocking import BlockingScheduler
from collections import defaultdict
import warnings
import pandas as pd
from tabulate import tabulate
import sys
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from currency_symbols import CurrencySymbols

warnings.simplefilter(action='ignore', category=FutureWarning)
    
# function to transform timedelta to propper formatting
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)

try:
    with open('config.json', 'r') as f:
        json_dict = json.load(f)
        addresses = json_dict['nodes']
        currency_type = str(json_dict['preferred_currency_type'])

        if(json_dict['repeat_script'] == True):
            script_interval = json_dict['script_interval']
        else:
            script_interval = 0
            
        if(json_dict['email_node_status_update'] == True):
            email_address = json_dict['email_address']
            email_password = json_dict['email_password']
            email_node_status_interval = json_dict['email_node_status_interval']   
        else:
            email_node_status_interval = 0
            
        if(json_dict['email_node_offline_update'] == True):
            email_address = json_dict['email_address']
            email_password = json_dict['email_password']
            email_node_offline_interval = json_dict['email_node_offline_interval']
        else:
           email_node_offline_interval = 0
    
except Exception as e: print(e)

# initalization of basic variables
pricevalue_url = "https://min-api.cryptocompare.com/data/price?fsym=DATA&tsyms=" + currency_type
rewards_url = "https://brubeck1.streamr.network:3013/datarewards/"
personalnodes_url = "https://brubeck1.streamr.network:3013/stats/"
networkstats_url = "https://brubeck1.streamr.network:3013/apy"
online_per_node = []

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
    accumulated_data = 0
    paid_data = 0
    staked_data = 0
    paid_per_node = defaultdict(int)
    staked_per_node = defaultdict(int)
    global online_per_node
    online_per_node = []
    accumulated_per_node = []
    last_reward_per_node = []
    claimpc_per_node = []
    
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
            accumulated_per_node.append(float(json_data["DATA"]))
        except:
            accumulated_per_node.append(float(1))
        try:
            accumulated_data += float(json_data["DATA"])
        except:
            accumulated_data += float(1)
            
        # get amount of paid data in total and per node
        try:
            json_data = {
                'query': '{\n  erc20Transfers(\n    where: {\n      from: "0x3979f7d6b5c5bfa4bcd441b4f35bfa0731ccfaef"\n      to: "' + value.lower() + '"\n      timestamp_gt: "1646065752"\n    }\n  ) {\n    timestamp\n    value\n  }\n}\n',
                }

            response = rq.post('https://api.thegraph.com/subgraphs/name/streamr-dev/data-on-polygon', json=json_data)
            json_data = json.loads(response.text)
            for index, data in enumerate(json_data["data"]["erc20Transfers"]):
                paid_data += round(float(json_data["data"]["erc20Transfers"][index]["value"]), 2)
                paid_per_node[key] += round(float(json_data["data"]["erc20Transfers"][index]["value"]), 2)
                
        except:           
            paid_data += 0
            paid_per_node[key] += 0

        # get amount of staked data per node (to do)       
        try:
            json_data = {
                'query': '{\n  erc20Balances(where: {account: "' + value.lower() + '", contract:"0x3a9a81d576d83ff21f26f325066054540720fc34"}) {\n    value \n  }\n}',
                }

            response = rq.post('https://api.thegraph.com/subgraphs/name/streamr-dev/data-on-polygon', json=json_data)
            json_data = json.loads(response.text)            
            for data in json_data["data"]:
                staked_data += round(float(json_data["data"]["erc20Balances"][0]["value"]), 2)
                staked_per_node[key] += round(float(json_data["data"]["erc20Balances"][0]["value"]), 2)
        
        except:
            staked_data += 0
            staked_per_node[key] += 0
        
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
            if(((json_data["claimPercentage"]), 5) == 1):
                claimpc_per_node.append(str("100.00%"))
            elif(((json_data["claimPercentage"]), 5) == 0):
                claimpc_per_node.append(str("00.00%"))
            else:
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
    try:
        response = rq.get(pricevalue_url)
        json_data = json.loads(response.text)
        coin_value = float(json_data[currency_type])
        currency_symbol = CurrencySymbols.get_symbol(currency_type)
        rev_total = round(coin_value * accumulated_data, 2)
        rev_received = round(coin_value * paid_data, 2)
        
    except:
        print("The currency type filled in the config file is invalid, using USD instead")
        response = rq.get("https://min-api.cryptocompare.com/data/price?fsym=DATA&tsyms=USD")    
        json_data = json.loads(response.text)
        coin_value = float(json_data["USD"])
        currency_symbol = CurrencySymbols.get_symbol("USD")
        rev_total = round(coin_value * accumulated_data, 2)
        rev_received = round(coin_value * paid_data, 2)
        
    # average revenue per dag and hour, calculated from total revenue up to current date
    rev_day = round(rev_total / mining_days, 2)
    rev_hour = round(rev_total / (mining_days * 24 + mining_hours), 2)

    # average revenue per dag and hour, calculated from total revenue up to current date
    node_rev_day = round(
        (((accumulated_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 24) * len(addresses.keys()), 2)
    node_rev_hour = round(
        (((accumulated_per_node[0] * coin_value) / (mining_days * 24 + mining_hours))) * len(addresses.keys()), 2)

    # old estimates of monthly and yearly revenue, calculated from total revenue up to current date
    est_rev_month = round(rev_total / (mining_days * 24 + mining_hours) * 732, 2)
    est_rev_year = round(rev_total / (mining_days * 24 + mining_hours) * 8772, 2)

    # new estimates which calculate profits based on the profitability of your first node (assumes every node has equal DATA amount staked)
    node_est_rev_month = round(
        (((accumulated_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 732) * len(addresses.keys()), 2)
    node_est_rev_year = round(
        (((accumulated_per_node[0] * coin_value) / (mining_days * 24 + mining_hours)) * 8772) * len(addresses.keys()), 2)

    df = pd.DataFrame()
    column_names = ["Name", "Gathered", "Paid", "Unpaid", "Staked", "Status", "Last reward", "Claims"]
    currency_symbol = CurrencySymbols.get_symbol(currency_type)
    
    for index, address in enumerate(addresses):
        d = {'Name': "Node "+ str(index + 1), 
             'Gathered': "DATA: "+ str(round(accumulated_per_node[index],2)) + "\n" + currency_type + currency_symbol + ": " + str(round(accumulated_per_node[index] * coin_value, 2)), 
             'Paid': "DATA: "+ str(round(paid_per_node[address],2))  + "\n" + currency_type + currency_symbol + ": " + str(round(paid_per_node[address] * coin_value, 2)), 
             'Unpaid': "DATA: "+ str(round((accumulated_per_node[index] - paid_per_node[address]),2))  + "\n" + currency_type + currency_symbol + ": " + str(round((accumulated_per_node[index] - paid_per_node[address]) * coin_value, 2)),
             'Staked': "DATA: "+ str(round(staked_per_node[address],2)) + "\n" + currency_type + currency_symbol + ": " + str(round(staked_per_node[address] * coin_value, 2)),  
             'Status': online_per_node[index],
             'Last reward': last_reward_per_node[index], 
             'Claims': claimpc_per_node[index]}
        
        df = df.append(d, ignore_index=True)
    df = df.reindex(columns = column_names)
    try:
        print('\n############################################ STREAMR NODE EARNINGS ###########################################')
        print(f'############################################# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ############################################')
        print(f'\n                                Total time mined: {mining_time_formatted}')
        print(f'                                                Total nodes: {len(addresses)}')        
        print('\n__________________________________________________ REVENUE ___________________________________________________')
        print(f'\n                                   Total revenue        {round(accumulated_data, 2)} DATA / {currency_symbol + str(rev_total)}')
        print(f'                                   Total staked         {round(staked_data, 2)} DATA / {currency_symbol + str(round(staked_data * coin_value, 2))}\n')   
        print(f'                                   Received revenue     {round(paid_data, 2)} DATA / {currency_symbol + str(rev_received)} ')
        print(f'                                   Revenue to receive   {round(accumulated_data - paid_data, 2)} DATA / {currency_symbol + str(round(rev_total - rev_received, 2))}\n')    
        print(f'                              Average  | revenue per hour: {round(rev_hour / coin_value, 2)} DATA / {currency_symbol + str(rev_hour)}')
        print(f'                               based   | revenue per day:  {round(rev_day / coin_value, 2)} DATA / {currency_symbol + str(rev_day)}\n')
        print(f'                               Node    | revenue per hour: {round(node_rev_hour / coin_value, 2)} DATA / {currency_symbol + str(node_rev_hour)}')
        print(f'                               based   | revenue per day:  {round(node_rev_day / coin_value, 2)} DATA / {currency_symbol + str(node_rev_day)}')
        print('\n_________________________________________________ NODE STATS _________________________________________________\n')
        print(tabulate(df, headers= column_names, tablefmt='fancy_grid', showindex=False))
        print('\n__________________________________________________ ESTIMATES _________________________________________________\n')
        print(f'                               Average  | monthly revenue: {round(est_rev_month / coin_value, 2)} DATA / {currency_symbol + str(est_rev_month)}')
        print(f'                                based   | yearly revenue:  {round(est_rev_year / coin_value, 2)} DATA / {currency_symbol + str(est_rev_year)}\n')
        print(f'                                Node    | monthly revenue: {round(node_est_rev_month / coin_value, 2)} DATA / {currency_symbol + str(node_est_rev_month)}')
        print(f'                                based   | yearly revenue:  {round(node_est_rev_year / coin_value, 2)} DATA / {currency_symbol + str(node_est_rev_year)}')
        print(f'\n############################ APR: {apr}% ######################### APY: {apy}% #############################')
        print(f'############################################ DATA VALUE: {currency_symbol + str(coin_value)} #############################################')
   
    except Exception as e: print(e)
    
    with open('log.txt', 'w', encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = f # Change the standard output to the file.
        print('\n############################################ STREAMR NODE EARNINGS ###########################################')
        print(f'############################################# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ############################################')
        print(f'\n                                Total time mined: {mining_time_formatted}')
        print(f'                                                Total nodes: {len(addresses)}')        
        print('\n__________________________________________________ REVENUE ___________________________________________________')
        print(f'\n                                   Total revenue        {round(accumulated_data, 2)} DATA / ${rev_total}')
        print(f'                                   Total staked         {round(staked_data, 2)} DATA / {currency_symbol + str(round(staked_data * coin_value, 2))}\n')   
        print(f'                                   Received revenue     {round(paid_data, 2)} DATA / {currency_symbol + str(rev_received)} ')
        print(f'                                   Revenue to receive   {round(accumulated_data - paid_data, 2)} DATA / {currency_symbol + str(round(rev_total - rev_received, 2))}\n')    
        print(f'                              Average  | revenue per hour: {round(rev_hour / coin_value, 2)} DATA / {currency_symbol + str(rev_hour)}')
        print(f'                               based   | revenue per day:  {round(rev_day / coin_value, 2)} DATA / {currency_symbol + str(rev_day)}\n')
        print(f'                               Node    | revenue per hour: {round(node_rev_hour / coin_value, 2)} DATA / {currency_symbol + str(node_rev_hour)}')
        print(f'                               based   | revenue per day:  {round(node_rev_day / coin_value, 2)} DATA / {currency_symbol + str(node_rev_day)}')
        print('\n_________________________________________________ NODE STATS _________________________________________________\n')
        print(tabulate(df, headers= column_names, tablefmt='fancy_grid', showindex=False))
        print('\n__________________________________________________ ESTIMATES _________________________________________________\n')
        print(f'                               Average  | monthly revenue: {round(est_rev_month / coin_value, 2)} DATA / {currency_symbol + str(est_rev_month)}')
        print(f'                                based   | yearly revenue:  {round(est_rev_year / coin_value, 2)} DATA / {currency_symbol + str(est_rev_year)}\n')
        print(f'                                Node    | monthly revenue: {round(node_est_rev_month / coin_value, 2)} DATA / {currency_symbol + str(node_est_rev_month)}')
        print(f'                                based   | yearly revenue:  {round(node_est_rev_year / coin_value, 2)} DATA / {currency_symbol + str(node_est_rev_year)}')
        print(f'\n############################ APR: {apr}% ######################### APY: {apy}% #############################')
        print(f'############################################ DATA VALUE: {currency_symbol + str(coin_value)} #############################################')
        sys.stdout = original_stdout
        
def scheduler():
    # loops through obtain_info function once per set interval in variable script_frequency
    scheduler = BlockingScheduler()
    obtain_info()
    try:
        # adds needed jobs to the scheduler (configured in the json file)
        if(script_interval) != 0: 
            scheduler.add_job(obtain_info, 'interval', seconds=script_interval)
        
        if(email_node_status_interval) != 0: 
            scheduler.add_job(status_update, 'interval', seconds=email_node_status_interval)
            status_update()
        
        if(email_node_offline_interval) != 0: 
            scheduler.add_job(offline_update, 'interval', seconds=email_node_offline_interval)
            offline_update()
        
    # starts scheduler if any intervals are toggled
        if(script_interval != 0 or email_node_status_interval != 0 or email_node_offline_interval != 0):
            scheduler.start()

    except Exception as e: print(e)
    
def status_update():
    try:
        # setup the MIME
        message = MIMEMultipart()
        message['From'] = email_address
        message['To'] = email_address

        with open('log.txt', "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename('log.txt')
                )
        # after the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename('log.txt')
            message.attach(part)
        
        # the subject 
        message['Subject'] = f'Node earnings overview - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'   
        # creates SMTP session for sending the mail
        # uses gmail with port
        session = smtplib.SMTP('smtp.gmail.com', 587) 
        # enables security
        session.starttls()         
        # logs in  with mail_id and password (use https://support.google.com/accounts/answer/185833?hl=en if password is incorrect)        
        session.login(email_address, email_password) 
        text = message.as_string()
        session.sendmail(email_address, email_address, text)
        session.quit()
        
    except Exception as e: print(e)

def offline_update():
    try:
        if ("Offline?" in online_per_node):
            message = MIMEMultipart()
            message['From'] = email_address
            message['To'] = email_address

            with open('log.txt', "rb") as file:
                part = MIMEApplication(
                    file.read(),
                    Name=basename('log.txt')
                    )
                # after the file is closed
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename('log.txt')
                message.attach(part)
        
            message['Subject'] = f'One or more nodes may be offline  - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'   #The subject line
            # creates SMTP session for sending the mail
            # uses gmail with port
            session = smtplib.SMTP('smtp.gmail.com', 587) 
            # enables security
            session.starttls()         
            # logs in  with mail_id and password (use https://support.google.com/accounts/answer/185833?hl=en if password is incorrect)        
            session.login(email_address, email_password) 
            text = message.as_string()
            session.sendmail(email_address, email_address, text)
            session.quit()
    
    except Exception as e: print(e)

# runs the obtain_info function once on startup, after which the scheduler takes over
scheduler()

