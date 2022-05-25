# klaytn-covalent-snapshot
This is for snapshot process of AOZ BOOKMARK made using covalent api

-------------------------

## Usage

Install the required modules

```
pip install -r requirements.txt
```

Create a file `data.json` with these contents

```
{
    "API_KEY" : "your covalent api key",
    "base_url" : "https://api.covalenthq.com/v1",
    "chain_id" : "chain id", # klaytn cahin id = 8217
    "address" : "address you want to search"
    "to_opensea_pklay": "0xd82dab73fc27c4207f2d87924506a1aca24dc7fc", # to check sold on opensea(using pkaly)
    "to_opensea_klay" : "0x41cff281b578f4cf45515d6e4efd535e47e76efd"  # to check sold on opensea(using kaly) 
}
```

-------------------------

#### Setup

