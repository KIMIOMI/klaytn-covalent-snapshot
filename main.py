import time
from pymongo import MongoClient
import numpy
import pandas as pd
import requests
import json
import datetime

class covalant:
    with open('./data.json') as f:
      data = json.load(f)

    API_KEY = data["API_KEY"]
    base_url = data["base_url"]
    chain_id = data["chain_id"]
    address = data["address"]
    opensea_pklay = data["to_opensea_pklay"] # 0xd82dab73fc27c4207f2d87924506a1aca24dc7fc
    opensea_klay = data["to_opensea_klay"] # 0x41cff281b578f4cf45515d6e4efd535e47e76efd
    cluster = MongoClient(data["mongo"])

    db = cluster["zen-bot"]
    snapshot = db["snapshot2"]
    holder = db["holder2"]

    def get_wallet_balance(self, address):
        endpoint = f'/{self.chain_id}/address/{address}/balances_v2/?nft=true&no-nft-fetch=true&key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except requests.RequestException as e:
                print(e)
                print('Try again...')
                time.sleep(2)
        data = result["data"]
        items = data["items"]

        for item in items:
            if item["contract_address"] == self.address:
                balance = item["balance"]
                return balance
        return False

    def get_token_holders(self):
        endpoint = f'/{self.chain_id}/tokens/{self.address}/token_holders/?page-size=2018&key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except requests.RequestException as e:
                print(e)
                print('Try again...')
                time.sleep(2)
        data = result["data"]
        items = data["items"]
        with open('./holders.txt', 'w') as f:
            f.write("address, balance\n")
            for item in items:
                address = item["address"]
                balance = item["balance"]
                f.write(f'{address},{balance}\n')
        return pd.read_csv('./holders.txt')

    def is_original_owner(self, chain_id, address, token_id):
        endpoint =f'/{chain_id}/tokens/{address}/nft_metadata/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except requests.RequestException as e:
                print(e)
                print('Try again...')
                time.sleep(2)

        data = result["data"]
        items = data["items"]
        nft_data = items[0]["nft_data"]
        original_owner = nft_data[0]["original_owner"]
        owner = nft_data[0]["owner"]

        if owner == original_owner:
            is_original = True
        else:
            is_original = False

        output = (is_original, token_id, owner)

        print(output)
        return output

    def get_owner(self, token_id):
        endpoint =f'/{self.chain_id}/tokens/{self.address}/nft_metadata/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except requests.RequestException as e:
                print(e)
                print('Try again...')
                time.sleep(2)
        data = result["data"]
        items = data["items"]
        nft_data = items[0]["nft_data"]
        original_owner = nft_data[0]["original_owner"]
        owner = nft_data[0]["owner"]

        return original_owner, owner

    def transaction_check(self, chain_id, address, token_id):
        endpoint = f'/{chain_id}/tokens/{address}/nft_transactions/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except Exception as e:
                print(e)
                print('Try again...')
                time.sleep(2)

        data = result["data"]
        items = data["items"]
        nft_transactions = items[0]["nft_transactions"]
        total_transactions = len(nft_transactions)
        num = 0
        for transaction in nft_transactions:
            block_signed_at = transaction["block_signed_at"]
            to_address = transaction["to_address"]
            log_events_length = len(transaction["log_events"])
            num += 1
            if block_signed_at > "2022-03-22" and log_events_length > 2 and (to_address == self.opensea_klay or to_address == self.opensea_pklay):
                return "excluded", token_id, block_signed_at, to_address, log_events_length, total_transactions, num
            elif block_signed_at <= "2022-03-22" and log_events_length > 2 and (to_address == self.opensea_klay or to_address == self.opensea_pklay):
                return "condition B", token_id, block_signed_at, to_address, log_events_length, total_transactions, num
            else:
                pass

        return "condition A", token_id, block_signed_at, to_address, log_events_length, total_transactions, num

    def take_snapshot(self, token_id):
        endpoint = f'/{self.chain_id}/tokens/{self.address}/nft_transactions/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                if result != None:
                    break
            except Exception as e:
                print(e)
                print('Try again...')
                time.sleep(2)

        self.snapshot.insert_one(result)

    def take_holder(self):
        endpoint = f'/{self.chain_id}/tokens/{self.address}/token_holders/?page-size=2018&key={self.API_KEY}'
        url = self.base_url + endpoint
        while True:
            try:
                result = requests.get(url).json()
                break
            except requests.RequestException as e:
                print(e)
                print('Try again...')
                time.sleep(2)
        data = result["data"]
        self.holder.insert_one(result)

def transaction_check(reset : bool = False):
    with open('./data.json') as f:
        data = json.load(f)
    API_KEY = data["API_KEY"]
    base_url = data["base_url"]
    chain_id = data["chain_id"]
    address = data["address"]
    opensea_pklay = data["to_opensea_pklay"]  # 0xd82dab73fc27c4207f2d87924506a1aca24dc7fc
    opensea_klay = data["to_opensea_klay"]  # 0x41cff281b578f4cf45515d6e4efd535e47e76efd
    cluster = MongoClient(data["mongo"])
    db = cluster["zen-bot"]
    snapshot = db["snapshot2"]
    holder = db["holder2"]
    results = snapshot.find()
    token_id = -1

    if reset == True:
        with open('./notListed log.csv', 'w') as f:
            f.write('condition, token id, block signed at, to address, numbers of log events, total transaction, issued transaction')
        with open('./notListed tokenID.txt', 'w') as f:
            f.write('condition, token id, original owner, owner')

    for result in results:
        token_id += 1
        data = result["data"]
        items = data["items"]
        nft_transactions = items[0]["nft_transactions"]
        total_transactions = len(nft_transactions)
        num = 0
        for transaction in nft_transactions:
            block_signed_at = transaction["block_signed_at"]
            to_address = transaction["to_address"]
            log_events_length = len(transaction["log_events"])
            num += 1
            if block_signed_at > "2022-03-22" and log_events_length > 2 and (
                    to_address == opensea_klay or to_address == opensea_pklay):
                condition = "excluded"
                with open('./notListed log.csv', 'a') as f:
                    f.write(f'{condition},{token_id},{block_signed_at},{to_address},{log_events_length},{total_transactions},{num}\n')

            elif block_signed_at <= "2022-03-22" and log_events_length > 2 and (
                    to_address == opensea_klay or to_address == opensea_pklay):
                condition = "condition B"

            else:
                condition = "condition A"



def notlisted_token_find(start_token_id, end_token_id, reset = False):
    started_time = datetime.datetime.now()
    print('started at : ', started_time)

    if reset == True:
        with open('./notListed log.csv', 'w') as f:
            f.write('condition, token id, block signed at, to address, numbers of log events, total transaction, issued transaction')
        with open('./notListed tokenID.txt', 'w') as f:
            f.write('condition, token id, original owner, owner')

    api = covalant()

    for i in range(start_token_id, end_token_id):
        print("searching token number ", i)
        if i == 390:
            continue
        _notListed, token_id, block_signed_at, to_address, log_events_length, total_transaction, num = api.transaction_check(api.chain_id, api.address, i)
        with open('./notListed log.csv', 'a') as f:
            f.write(f'{_notListed},{token_id},{block_signed_at},{to_address},{log_events_length},{total_transaction},{num}\n')
        if _notListed == "condition A" or _notListed == "condition B":
            original_owner, owner = api.get_owner(token_id)
            with open('./notListed tokenID.txt', 'a') as f:
                f.write(f'{_notListed},{token_id},{original_owner},{owner}\n')
        print(i, " done")

    ended_time = datetime.datetime.now()
    cost_time = ended_time - started_time
    print('ended at : ', ended_time)
    print('cost_time : ', cost_time)
    return cost_time

def tier_calculate():
    column_name = ['condition', 'token id', 'original owner', 'owner']
    data = pd.read_csv('./notListed tokenID - test2.txt').apply(lambda x: x.str.strip(), axis = 1)
    dataframe = data.values.tolist()
    new_dataframe = pd.DataFrame(dataframe, columns=column_name)
    indexNames = new_dataframe[new_dataframe['condition'] == 'condition B'].index

    groups = new_dataframe.groupby('owner')
    new_group = pd.DataFrame(groups.size()).reset_index()
    new_group.columns = ['address', 'sum_balance']
    new_group = new_group.set_index('address')
    new_group["status"] = '만족'
    new_group.to_csv('test.txt')
    new_group = new_group.applymap(str)
    api = covalant()
    holder = api.get_token_holders().set_index('address')
    # new_balance = pd.merge(holder, new_group, how='outer', on='address')
    new_balance = holder.join(new_group)

    new_dataframe.drop(indexNames, inplace=True)
    groupA = new_dataframe.groupby('owner')
    new_group = pd.DataFrame(groupA.size()).reset_index()
    new_group.columns = ['address', 'A_balance']
    new_group = new_group.set_index('address')
    new_group["A condition"] = 'A 만족'
    new_group = new_group.applymap(str)
    new_balance = new_balance.join(new_group)
    new_balance.to_csv('final_balance.csv')

# tier_calculate()

# api = covalant()
# for i in range(0, 7778):
#     if i == 390:
#         continue
#     api.take_snapshot(i)
#     print(f'{i}는 끝')

# api.take_holder()

snapshot = Snapshot()
snapshot.transaction_check()
# notlisted_token_find(1207, 1208)
