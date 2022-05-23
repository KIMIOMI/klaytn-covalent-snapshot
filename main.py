import requests
import json
import datetime

with open('./data.json') as f:
  data = json.load(f)

API_KEY = data["API_KEY"]
base_url = data["base_url"]
chain_id = data["chain_id"]
address = data["address"]
opensea_pklay = data["to_opensea_pklay"] # 0xd82dab73fc27c4207f2d87924506a1aca24dc7fc
opensea_klay = data["to_opensea_klay"] # 0x41cff281b578f4cf45515d6e4efd535e47e76efd

def get_wallet_balance(chain_id, address):
    endpoint = f'/{chain_id}/address/{address}/balances_v2/?key={API_KEY}'
    url = base_url + endpoint
    result = requests.get(url).json()
    data = result["data"]
    print(data)
    return(data)

def is_original_owner(chain_id, address, token_id):
    endpoint =f'/{chain_id}/tokens/{address}/nft_metadata/{token_id}/?key={API_KEY}'
    url = base_url + endpoint
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

def transaction_check(chain_id, address, token_id):
    endpoint = f'/{chain_id}/tokens/{address}/nft_transactions/{token_id}/?key={API_KEY}'
    url = base_url + endpoint
    result = requests.get(url).json()
    data = result["data"]
    items = data["items"]
    nft_transactions = items[0]["nft_transactions"]
    for transaction in nft_transactions:
        block_signed_at = transaction["block_signed_at"]
        to_address = transaction["to_address"]
        log_events_length = len(transaction["log_events"])

        if block_signed_at > "2022-03-22" and log_events_length > 2 and (to_address == opensea_klay or to_address == opensea_pklay):
            return "excluded", token_id, block_signed_at, to_address, log_events_length
        elif block_signed_at <= "2022-03-22" and log_events_length > 2 and (to_address == opensea_klay or to_address == opensea_pklay):
            return "condition B", token_id, block_signed_at, to_address, log_events_length
        else:
            return "condition A", token_id, block_signed_at, to_address, log_events_length

# Example address request
# get_wallet_balance(klatyn_chain_id, demo_address)
# A_condition = []
#

def notlisted_token_find(start_token_id, end_token_id):
    try:
        started_time = datetime.datetime.now()
        print('started at : ', started_time)

        with open('./notListed log.csv', 'w') as f:
            pass
        with open('./notListed tokenID.txt', 'w') as f:
            pass

        for i in range(start_token_id, end_token_id):
            if i == 390:
                continue
            _notListed, token_id, block_signed_at, to_address, log_events_length = transaction_check(chain_id, address, i)
            with open('./notListed log.csv', 'a') as f:
                f.write(f'{_notListed}, {token_id}, {block_signed_at}, {to_address}, {log_events_length}\n')
            if _notListed:
                with open('./notListed tokenID.txt', 'a') as f:
                    f.write(f'{token_id}\n')

        ended_time = datetime.datetime.now()
        cost_time = ended_time - started_time
        print('ended at : ', ended_time)
        print('cost_time : ', cost_time)
        return cost_time
    except Exception as e:
        print(e)

notlisted_token_find(4483, 7778)
#     if is_original == True:
#         A_condition.append(owner)

#     is_original, token_id, owner = is_original_owner(klatyn_chain_id, demo_address, i)



