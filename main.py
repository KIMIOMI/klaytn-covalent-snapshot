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

    def get_wallet_balance(self, chain_id, address):
        endpoint = f'/{chain_id}/address/{address}/balances_v2/?key={self.API_KEY}'
        url = self.base_url + endpoint
        result = requests.get(url).json()
        data = result["data"]
        print(data)
        return(data)

    def is_original_owner(self, chain_id, address, token_id):
        endpoint =f'/{chain_id}/tokens/{address}/nft_metadata/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        result = requests.get(url).json()
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
        result = requests.get(url).json()
        data = result["data"]
        items = data["items"]
        nft_data = items[0]["nft_data"]
        original_owner = nft_data[0]["original_owner"]
        owner = nft_data[0]["owner"]

        return original_owner, owner

    def transaction_check(self, chain_id, address, token_id):
        endpoint = f'/{chain_id}/tokens/{address}/nft_transactions/{token_id}/?key={self.API_KEY}'
        url = self.base_url + endpoint
        result = requests.get(url).json()
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

# Example address request
# get_wallet_balance(klatyn_chain_id, demo_address)
# A_condition = []
#

def notlisted_token_find(start_token_id, end_token_id, reset = False):
    started_time = datetime.datetime.now()
    print('started at : ', started_time)

    if reset == True:
        with open('./notListed log.csv', 'w') as f:
            pass
        with open('./notListed tokenID.txt', 'w') as f:
            pass

    api = covalant()

    for i in range(start_token_id, end_token_id):
        try:
            print("searching token number ", i)
            if i == 390:
                continue
            _notListed, token_id, block_signed_at, to_address, log_events_length, total_transaction, num = api.transaction_check(api.chain_id, api.address, i)
            with open('./notListed log.csv', 'a') as f:
                f.write(f'{_notListed}, {token_id}, {block_signed_at}, {to_address}, {log_events_length}, {total_transaction}, {num}\n')
            if  _notListed == "condition A" or _notListed == "condition B":
                original_owner, owner = api.get_owner(token_id)
                with open('./notListed tokenID.txt', 'a') as f:
                    f.write(f'{_notListed}, {token_id}, {original_owner}, {owner}\n')
            print(i, " done")
        except Exception as e:
            print(e)

    ended_time = datetime.datetime.now()
    cost_time = ended_time - started_time
    print('ended at : ', ended_time)
    print('cost_time : ', cost_time)
    return cost_time

def tier_calculate():
    with open('./notListed tokenID.txt', 'r') as f:
        tokenId = f.readline()
        api = covalant()

notlisted_token_find(424, 7778)