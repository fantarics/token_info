import asyncio
import logging

from web3 import AsyncWeb3
from eth_account.signers.local import LocalAccount
from eth_account.messages import encode_defunct


def num_to_hex_filled(number: int):
    return str(hex(int(number)))[2:].zfill(64)


def address_to_hex_filled(address: str, fill: int = 64):
    return address.lower()[2:].zfill(64)


async def construct_transaction(
        account: LocalAccount,
        w3: AsyncWeb3,
        from_address: str,
        to_address: str,
        value: int,
        data: str,
        custom_gas: int = 0,
        wait: bool = True,
        custom_nonce=None
):
    if custom_nonce:
        nonce = custom_nonce
    else:
        nonce = await w3.eth.get_transaction_count(account.address)
    chain_id = await w3.eth.chain_id
    transaction_body = {
        "from": account.address,
        "to": w3.to_checksum_address(to_address),
        "chainId": chain_id,
        "value": value,
        "gasPrice": await w3.eth.gas_price,
        "gas": 1,
        "nonce": nonce,
        "data": data
    }
    try:
        transaction = await estimate_gas_limit(transaction_body, w3)
        signed_transaction = account.sign_transaction(transaction_dict=transaction)
        result = await w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        )
    except Exception as e:
        if f'nonce too low: next nonce {nonce+1}, tx nonce {nonce}' in str(e):
            return await construct_transaction(
                account,
                w3,
                from_address,
                to_address,
                value,
                data,
                custom_gas,
                wait,
                custom_nonce=nonce+1
            )
        if f"max fee per gas less than block base fee" in str(e):
            return await construct_transaction(
                account,
                w3,
                from_address,
                to_address,
                value,
                data,
                custom_gas,
                wait
            )
        print(e)
        return False

    tx_hex = result.hex()
    if wait:
        finalized = await wait_transaction_final(tx_hex, w3, from_address)
        return tx_hex if finalized else False
    else:
        return tx_hex


async def wait_transaction_final(tx_hex, w3: AsyncWeb3, from_address):
    tx_uploaded = False
    retries = 0
    while not tx_uploaded and retries < 15:
        await asyncio.sleep(2)
        try:
            await w3.eth.get_transaction_receipt(
                tx_hex
            )
            tx_uploaded = True
        except Exception as e:
            retries += 1
            tx_uploaded = False
    await asyncio.sleep(5)
    if tx_uploaded:
        return True
    else:
        logging.warning(
            "Transaction could not be uploaded for address {}".format(from_address)
        )
        return False


async def get_token_balance(w3: AsyncWeb3, address, token_contract):
    token_contract = w3.eth.contract(address=w3.to_checksum_address(token_contract), abi=token_abi)
    token_balance = await token_contract.functions.balanceOf(address).call()
    return token_balance


async def estimate_gas_limit(transaction, w3: AsyncWeb3):
    estimate_gas = await w3.eth.estimate_gas(
        transaction=transaction
    )
    transaction["gas"] = int(estimate_gas * 1.1)
    return transaction


def sign_message(account, msg):
    encoded_msg = encode_defunct(
        text=msg
    )
    signed_msg = account.sign_message(encoded_msg)
    return signed_msg.signature.hex()


token_abi = """[
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": true,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]"""


def sign_message(account, msg):
    encoded_msg = encode_defunct(
        text=msg
    )
    signed_msg = account.sign_message(encoded_msg)
    return signed_msg.signature.hex()
