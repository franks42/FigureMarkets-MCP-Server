# server.py
from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import json
from datetime import datetime, timezone
import webbrowser
from typing import Tuple, Any, Dict, List, Union

# Union type for mixed JSON values
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

# class MCPServer:
#     def __init__(self):
#         self.context_read = False
    
#     def get_system_context(self):
#         self.context_read = True
#         return system_context_data
    
#     def fetch_current_fm_data(self):
#         if not self.context_read:
#             return {
#                 "error": "Must call get_system_context() first",
#                 "required_action": "Call get_system_context() before using other functions"
#             }
#         return actual_data

# Create an MCP server
mcp = FastMCP("FigureMarkets")
mcp.mcp_context_read = False

denom_conversion = {
    #stable coins
    "uusd.trading": {"denom": "USD", "factor": 1000000},
    "uylds.fcc": {"denom": "YLDS", "factor": 1000000},
    "uusdc.figure.se": {"denom": "USDC", "factor": 1000000},
    "uusdt.figure.se": {"denom": "USDT", "factor": 1000000},
    # crypto-tokens
    "nhash": {"denom": "HASH", "factor": 1000000000},
    "neth.figure.se": {"denom": "ETH", "factor": 1000000000},
    "nsol.figure.se": {"denom": "SOL", "factor": 1000000000},
    "uxrp.figure.se": {"denom": "XRP", "factor": 1000000},
    "nbtc.figure.se": {"denom": "BTC", "factor": 1000000000},
    "nlink.figure.se": {"denom": "LINK", "factor": 1000000000},
    "nuni.figure.se": {"denom": "UNI", "factor": 1000000000},
    #
}

#########################################################################################
## helper functions
#########################################################################################

def datetime_to_ms(dt):
    """Convert datetime to milliseconds since epoch"""
    if dt.tzinfo is None:
        # Assume UTC if no timezone specified
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def ms_to_datetime(ms_timestamp, tz=timezone.utc):
    """Convert milliseconds since epoch to datetime"""
    return datetime.fromtimestamp(ms_timestamp / 1000, tz=tz)

def current_ms():
    """Get current time in milliseconds since epoch"""
    return int(datetime.now(timezone.utc).timestamp() * 1000)

###

async def async_http_get_json(
    url: str, 
    params: dict | None = None,
    timeout: float = 10.0,
    connect_timeout: float = 5.0
) -> JSONValue:
    """Make an async HTTP GET request and return JSON response.
    
    Args:
        url: The URL to send the GET request to
        params: Query parameters to include
        timeout: Total request timeout in seconds
        connect_timeout: Connection timeout in seconds
        
    Returns:
        JSON response data on success, or error dict with 'MCP-ERROR' key on failure
    """
    
    if mcp.mcp_context_read == False:
        mcp.mcp_context_read = True
        return {"MCP-ERROR": "Must review MCP server's context first! - Call get_system_context() before using this or other functions."}

    if params is None:
        params = {}
        
    timeout_config = httpx.Timeout(timeout, connect=connect_timeout)
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return {"MCP-ERROR": f"Expected JSON, got {content_type}"}
                
            return response.json()
            
        except httpx.TimeoutException:
            return {"MCP-ERROR": "Network Error: Request timed out"}
        except httpx.HTTPStatusError as e:
            return {"MCP-ERROR": f"HTTP error: {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"MCP-ERROR": f"Request error: {e}"}
        except ValueError as e:
            return {"MCP-ERROR": f"Invalid JSON response: {e}"}
        except Exception as e:
            return {"MCP-ERROR": f"Unknown exception raised: {e}"}


#########################################################################################
## resources
#########################################################################################

# @mcp.resource("system://context")
@mcp.tool()
async def get_system_context() -> str:
    """
    REQUIRED READING: Essential system context that MUST be read before using any tools.
    Contains critical usage guidelines, data handling protocols, and server capabilities.
    Returns:
        str: return is md formatted
    """
    url = "https://raw.githubusercontent.com/franks42/FigureMarkets-MCP-Server/refs/heads/main/FigureMarketsContext.md"
    
    timeout = httpx.Timeout(10.0, connect=5.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Raises exception for 4xx/5xx
            return response.text
        except httpx.TimeoutException:
            return "Network Error: Request timed out"
        except httpx.HTTPStatusError as e:
            return f"HTTP error: {e.response.status_code}"
        except httpx.RequestError as e:
            return f"Request error: {e}"

#########################################################################################
## tools
#########################################################################################

@mcp.tool()
async def fetch_last_crypto_token_price(token_pair : str="HASH-USD", last_number_of_trades : int=1) -> JSONValue:
    """For the crypto token_pair, e.g. HASH-USD, fetch the prices for the last_number_of_trades 
    from the Figure Markets exchange.
    Args:
        token_pair (str, optional): Two token/crypto symbols separated by '-', like BTC-USDC. Defaults to HASH-USD.
        last_number_of_trades (int, optional): Ask for specified number of trades to return. Defaults to 1.
    Returns:
        JSONValue: json dict where attribute 'matches' has a list of individual trade details
    """
    url = 'https://www.figuremarkets.com/service-hft-exchange/api/v1/trades/' + token_pair 
    params = {'size': last_number_of_trades}
    response = await async_http_get_json(url, params=params)
    if response.get("MCP-ERROR"): return response
    #massage json response data
    return response


@mcp.tool()
async def fetch_current_fm_data() -> JSONValue:
    """Fetch the current market data from the Figure Markets exchange.
    The data is a list of trading pair details.
    The 'id' attribute is the identifier for the trading pair.
    Each trading pair's 'denom' attribute is the token name and the 'quoteDenum' denotes the currency.
    Returns:
        JSONValue: json list of trading pair details
    """
    url = 'https://www.figuremarkets.com/service-hft-exchange/api/v1/markets' 
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    data = response['data']
    return data


@mcp.tool()
async def fetch_current_fm_account_balance_data(wallet_address: str) -> JSONValue:
    """Fetch the current account balance data from the Figure Markets exchange for the given wallet address' portfolio.
    The data is a list of dictionaries with balance details for all assets in the wallet.
    The relevant attributes are:
    'denom', which is the asset identifier. Note that 'neth.figure.se' denotes ETH, 'nhash' denotes nano-HASH, 'nsol.figure.se' denotes SOL, 
    'uusd.trading' denotes micro-USD, 'uusdc.figure.se' denotes USDC, 'uxrp.figure.se' denotes XRP, 'uylds.fcc' denotes YLDS, and ignore others.
    Note that the amount for denom 'nhash' represents only the AVAILABLE HASH in the wallet (non-delegated).
    To get total HASH holdings, you must also fetch delegation amounts separately.
    Args:
        wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json list of balance item details
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/balances"
    params = {"count": 20, "page": 1}
    response = await async_http_get_json(url, params=params)
    if response.get("MCP-ERROR"): return response
    balance_list = response['results']
    return balance_list


@mcp.tool()
async def fetch_available_total_amount(wallet_address: str) -> JSONValue:
    """Fetch the current available_total_amount of HASH in the wallet.
    
    available_total_amount = available_spendable_amount + available_committed_amount + available_unvested_amount
    
    The relevant attributes in the returned json dict are:
    'available_total_amount': amount in denom units
    'denom': the asset identifier and denom for the amount (nhash).
    Args:
        wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/balances"
    params = {"count": 20, "page": 1}
    response = await async_http_get_json(url, params=params)
    if response.get("MCP-ERROR"): return response
    balance_list = response['results']
    for e in balance_list:
        if e['denom'] == "nhash":
            return {'available_total_amount' : e['amount'],
                    'denom': e['denom']}
    return {"MCP ERROR" : "fetch_available_total_amount() - No 'nhash' in balance list"} 


@mcp.tool()
async def fetch_current_fm_account_info(wallet_address: str) -> JSONValue:
    """Fetch the current account/wallet info from the Figure Markets exchange for the given wallet address.
    Important attributes in the json response:
    'isVesting' : If True, then the account/wallet is subject to vesting restrictions. 
                  If False then the wallet has no applicable or active vesting schedule, no vesting hash amounts and therefore no vesting restrictions.
    Args:
        wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict of account details
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    return response


# @mcp.tool()
# async def fetch_current_hash_vesting_data(wallet_address: str) -> JSONValue:
#     """Fetch the current account HASH vesting data from the Figure Markets exchange for the given wallet address.
#     Note that the current vesting and vested amounts of hash should NOT be added to an account,
#     but should only apply to the amounts of hash in the account like delegated and available hash amounts.
#     Note that the locked-up Hash is subject to a vesting schedule where 1/48th of the original amount is vested monthly on the 22nd.
#     API returns amounts in nhash (1 HASH = 1,000,000,000 nhash). Convert to HASH for display purposes.
#     The returned dictionary has the following attributes:
#     'vesting_original_amount': the original number of nano-HASH that are subject to vesting schedule
#     'denom': token denomination
#     'vesting_total_vested_amount': amount of nhash that have vested as of today
#     'vesting_total_unvested_amount': amount of nhash that is still vesting and is unvested as of today
#     'vesting_events': list of dict with vesting_date, is-vested, amount and denom of upcoming vesting events
#     Args:
#         wallet_address (str): Wallet's Bech32 address.
#     Returns:
#         JSONValue: json dict of vesting schedule details
#     """
#     url = "https://service-explorer.provenance.io/api/v3/accounts/" + wallet_address + "/vesting"
#     response = await async_http_get_json(url)
#     if response.get("MCP-ERROR"): return response
#     vesting_data = {}
#     vesting_data['vesting_original_amount'] = int(response['originalVestingList'][0]['amount'])
#     vesting_data['denom'] = response['originalVestingList'][0]['denom']
#     list_of_vested_amounts = [int(e['coins'][0]['amount'])  for e in response['periodicVestingList'] if e['isVested']]
#     total_vested_amount = sum(list_of_vested_amounts)
#     vesting_data['vesting_total_vested_amount'] = total_vested_amount
#     vesting_data['vesting_total_unvested_amount'] = vesting_data['vesting_original_amount'] - vesting_data['vesting_total_vested_amount']
#     list_of_vesting_events = [{'amount': int(e['coins'][0]['amount']),
#                                'denom': e['coins'][0]['denom'],
#                                'vesting_date': e['vestingDate'],
#                                'is-vested' : e['isVested']}
#                             #   for e in response['periodicVestingList'] if not e['isVested']]
#                               for e in response['periodicVestingList']]
#     list_of_vesting_events.sort(key=lambda x: datetime.fromisoformat(x['vesting_date']))
#     vesting_data['vesting_events'] = list_of_vesting_events
#     return vesting_data

@mcp.tool()
async def fetch_vesting_total_unvested_amount(wallet_address: str, date_time: str|None=None) -> JSONValue:
    """Fetch the vesting_total_unvested_amount from the Figure Markets exchange for the given wallet address and the given `date_time`.
    `date_time` is current datetime.now() by default.
    The vesting schedule is estimated by a linear function for the unvested_amount that starts on start_time at vesting_original_amount, 
    and decreases linearly over time to zero at end_time.
    The returned dictionary has the following attributes:
    'date_time': the date-time for which the vesting info was requested
    'vesting_original_amount': the original number of nano-HASH that are subject to vesting schedule
    'denom': token denomination
    'vesting_total_vested_amount': amount of nhash that have vested as of `date_time`
    'vesting_total_unvested_amount': amount of nhash that is still vesting and is unvested as of `date_time`
    'start_time': date-time for when the vesting starts
    'end_time': date-time for when the vesting ends, and the unvested amount is zero and vested amount equals the vesting_original_amount
    Args:
        wallet_address (str): Wallet's Bech32 address.
        date_time (str): date_time in ISO 8601 format for which the vesting date is requested.
    Returns:
        JSONValue: json dict of vesting details
    """
    
    url = "https://service-explorer.provenance.io/api/v3/accounts/" + wallet_address + "/vesting"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    
    if date_time:
        dtms = datetime_to_ms(datetime.fromisoformat(date_time))
    else:
        dtms = current_ms()
    
    end_time_ms = datetime_to_ms(datetime.fromisoformat(response["endTime"]))
    start_time_ms = datetime_to_ms(datetime.fromisoformat(response["startTime"]))
    vesting_original_amount = int(response['originalVestingList'][0]['amount'])
    denom = response['originalVestingList'][0]['denom']
    if dtms < start_time_ms:
        total_vested_amount = 0
    elif dtms > end_time_ms:
        total_vested_amount = vesting_original_amount
    else:
        total_vested_amount = int(vesting_original_amount * (dtms - start_time_ms)/(end_time_ms - start_time_ms))
    total_unvested_amount = vesting_original_amount - total_vested_amount
    
    vesting_data = {'date_time' : ms_to_datetime(dtms).isoformat()}
    vesting_data['vesting_original_amount'] = vesting_original_amount
    vesting_data['denom'] = denom
    vesting_data['vesting_total_vested_amount'] = total_vested_amount
    vesting_data['vesting_total_unvested_amount'] = total_unvested_amount
    vesting_data['start_time'] = response["startTime"]
    vesting_data['end_time'] = response["endTime"]
    
    return vesting_data


@mcp.tool()
async def fetch_available_committed_amount(wallet_address: str) -> JSONValue:
    """Fetch the current committed HASH amount to the the Figure Markets exchange for the given wallet address.
    API returns amounts in nhash (1 HASH = 1,000,000,000 nhash). Convert to HASH for display purposes.
    The returned dictionary has the following attributes:
    'denom': token/HASH denomination
    'available_committed_amount': the number of 'denom' that are committed to the exchange
    Args:
        wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict of committed hash amount
    """
    url = "https://api.provenance.io/provenance/exchange/v1/commitments/account/" + wallet_address
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    market1_list = [x["amount"] for x in response["commitments"] if x["market_id"] == 1]
    hash_amount_dict_list = [x for x in (market1_list[0] if market1_list else []) if x["denom"] == "nhash"]
    hash_amount_dict = {"denom": "nhash"}
    hash_amount_dict["available_committed_amount"] = hash_amount_dict_list[0]["amount"] if hash_amount_dict_list else 0
    return hash_amount_dict


@mcp.tool()
async def fetch_figure_markets_assets_info() -> JSONValue:
    """Fetch the list of assets, like (crypto) tokens, stable coins, and funds,
    that are traded on the Figure Markets exchange.
    The returned list of dictionaries of asset's info has the following attributes:
    'asset_name' : identifier to use for asset
    'asset_description' : 
    'asset_display_name' : 
    'asset_type' : CRYPTO, STABLECOIN or FUND
    'asset_exponent' : 10 to the power asset_exponent multiplied by amount of asset_denom,
                        yields the asset amount
    'asset_denom' : asset denomination
    Args:
    Returns:
        JSONValue: json list of asset details
    """
    url = "https://figuremarkets.com/service-hft-exchange/api/v1/assets"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    asset_details_list = [{'asset_name' : details['name'],
                           'asset_description' : details['description'],
                           'asset_display_name' : details['displayName'],
                           'asset_type' : details['type'],
                           'asset_exponent' : details['exponent'],
                           'asset_denom' : details['provenanceMarkerName']}
                          for details in response['data']]
    return asset_details_list


@mcp.tool()
async def fetch_delegated_rewards_amount(wallet_address: str) -> JSONValue:
    """For the given wallet address, fetch the current, total amount of earned rewards
    from the staked/delegated hash with the validators.
    The returned dict has the following attributes:
    'delegated_rewards_amount' : total amount of rewarded hash
    'denom' : hash denomination
    Args: wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict with attrubutes 'delegated_rewards_amount' and 'denom'
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/rewards"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    if response['total']:
        return {'delegated_rewards_amount' : response['total'][0]['amount'],
                'denom' : response['total'][0]['denom']}
    else:
        return {'delegated_rewards_amount' : 0, 'denom' : 'nhash'}


@mcp.tool()
async def fetch_delegated_staked_amount(wallet_address: str) -> JSONValue:
    """For the given wallet address, fetch the current, total amount of staked hash
    with the validators.
    The returned dict has the following attributes:
    'staking_validators': number of validators used for staking
    'delegated_staked_amount' : total amount of staked hash
    'denom' : hash denomination
    Args: wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict with attributes 'staking_validators', 'delegated_staked_amount' and 'denom'
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/delegations"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    return {'staking_validators' : response['total'],
            'delegated_staked_amount' : response['rollupTotals']['bondedTotal']['amount'],
            'denom' : response['rollupTotals']['bondedTotal']['denom']}


@mcp.tool()
async def fetch_delegated_unbonding_amount(wallet_address: str) -> JSONValue:
    """For the given wallet address, fetch the current, total amount of hash
    that is unbonding with the validators.
    The returned dict has the following attributes:
    'delegated_unbonding_amount' : total amount of unbonding hash
    'denom' : hash denomination
    Args: wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict with attributes 'delegated_unbonding_amount' and 'denom'
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/unbonding"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    return {'delegated_unbonding_amount' : response['rollupTotals']['unbondingTotal']['amount'],
            'denom' : response['rollupTotals']['unbondingTotal']['denom']}


@mcp.tool()
async def fetch_delegated_redelegation_amount(wallet_address: str) -> JSONValue:
    """For the given wallet address, fetch the current, total amount of hash
    that is redelegated with the validators.
    The returned dict has the following attributes:
    'delegated_redelegated_amount' : total amount of redelegated hash
    'denom' : hash denomination
    Args: wallet_address (str): Wallet's Bech32 address.
    Returns:
        JSONValue: json dict with attributes 'delegated_redelegated_amount' and 'denom'
    """
    url = "https://service-explorer.provenance.io/api/v2/accounts/" + wallet_address + "/redelegations"
    response = await async_http_get_json(url)
    if response.get("MCP-ERROR"): return response
    return {'delegated_redelegated_amount' : response['rollupTotals']['redelegationTotal']['amount'],
            'denom' : response['rollupTotals']['redelegationTotal']['denom']}


# # # PB Pulse Trends table fetch
# # @mcp.tool()
# # def fetchPBPulseTrends() -> str:
# #     """Fetch a table from the Provenance Blockchain that shows the 24 hour, 1 week and 1 month trend for a couple of metrics.
# #     The metric trends are retrieved for:
# #     HASH price, volume
# #     .
# #     """
# #     client = httpx.Client()
# #     response = client.get("https://service-explorer.provenance.io/api/v2/accounts/" + wallet_adr)
# #     print(response.status_code)
# #     # data = response.text
# #     data = response.json()
# #     # print(data)
# #     return(json.dumps(data))

# # https://app.osmosis.zone/api/edge-trpc-assets/assets.getAssetHistoricalPrice?input={%22json%22:{%22coinMinimalDenom%22:%22ibc/CE5BFF1D9BADA03BB5CCA5F56939392A761B53A10FBD03B37506669C3218D3B2%22,%22timeFrame%22:{%22custom%22:{%22timeFrame%22:60,%22numRecentFrames%22:1}},%22realtime%22:true}}
# # Osmosis Hash Price
# # Symbol: HASH
# # IBC Denom: ibc/CE5BFF1D9BADA03BB5CCA5F56939392A761B53A10FBD03B37506669C3218D3B2
# #         Destination Chain: provenance Denom:nhash
# #         Destination Channel: channel-7
# #         Source Channel: channel-222
# #         Base Denom: nhash
# # {
# #   "result": {
# #     "data": {
# #       "json": [
# #         {
# #           "time": 1748390400,
# #           "high": 0.0205347756148018,
# #           "low": 0.02032216375124,
# #           "close": 0.0203711111611626,
# #           "open": 0.0205346536164336,
# #           "volume": 32.6893968585663
# #         }
# #       ]
# #     }
# #   }
# # }
# @mcp.tool()
# async def fetchCurrentHashPriceFromOsmosis() -> str:
#     """Fetch the current HASH price from the Osmosis exchange"""
#     timeout = httpx.Timeout(10.0, connect=5.0)
#     async with httpx.AsyncClient(timeout=timeout) as client:
#         try:
#             response = await client.get('https://app.osmosis.zone/api/edge-trpc-assets/assets.getAssetHistoricalPrice?input={%22json%22:{%22coinMinimalDenom%22:%22ibc/CE5BFF1D9BADA03BB5CCA5F56939392A761B53A10FBD03B37506669C3218D3B2%22,%22timeFrame%22:{%22custom%22:{%22timeFrame%22:60,%22numRecentFrames%22:1}},%22realtime%22:true}}')
#             response.raise_for_status()
#             print(response.status_code)
#             data = response.json()
#             data_dict = data["result"]["data"]["json"][0]
#             data_dict["market"] = "Osmosis"
#             data_dict["denom"] = "HASH"
#             data_dict["symbol"] = "HASH-USD"
#             data_dict["marketId"] = "HASH-USD"
#             data_dict["price"] = data_dict["close"]
#             data_dict["created"] = datetime.utcfromtimestamp(
#                 data_dict["time"]).strftime('%Y-%m-%d %H:%M:%S UTC')
#             return json.dumps(data_dict)
#         except httpx.TimeoutException:
#             return "Network Error: Request timed out"
#         except httpx.HTTPStatusError as e:
#             return f"HTTP error: {e.response.status_code}"
#         except httpx.RequestError as e:
#             return f"Request error: {e}"
#         except (KeyError, IndexError) as e:
#             return f"Data parsing error: {e}"

# # {
# #   "denom": "HASH",
# #   "symbol": "HASH-USD",
# #   "marketId": "HASH-USD",
# #   "matches": [
# #     {
# #       "id": "2YM4M5C041RV",
# #       "price": 0.025,
# #       "quantity": 4153.847,
# #       "created": "2025-05-28T00:14:34.051048235Z"
# #     }
# #   ]
# # }


# @mcp.tool()
# def openPBExplorerPage(page: str, wallet: str = "", browser: str = "") -> str:
#     """Open specific pages on the Provenance Blockchain Explorer website based on the 'page' argument value.
#     When page is 'pulse', open the Provenance Pulse web page.
#     When page is 'pulse assets', open the pulse assets list web page.
#     When page is 'explorer', open the provenance explorer web page.
#     When page is 'explorer wallet' then pass also the wallet address, and it will open the explorer page with the wallet details.
#     """
#     dispatch = {'pulse': "https://provenance.io/pulse",
#                 'pulse assets': "https://provenance.io/pulse/asset-list",
#                 'explorer': "https://explorer.provenance.io/",
#                 'explorer wallet': "https://explorer.provenance.io/accounts/" + wallet}
#     try:
#         url = dispatch[page]
#         webbrowser.get(browser if browser != "" else None).open(url)
#         return browser
#     except Exception as e:
#         return (f"Error opening webpage: {e}")

#     # "FigureMarkets": {
#     #   "command": "/opt/homebrew/bin/uv",
#     #   "args": [
#     #     "run",
#     #     "--with",
#     #     "mcp[cli]",
#     #     "mcp",
#     #     "run",
#     #     "/Users/franksiebenlist/Documents/GitHub/fm-mcp-server/server.py"
#     #   ],
#     #   "toolCallTimeoutMillis": 120000
#     # }