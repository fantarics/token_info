from typing import List, Iterable
from web3 import AsyncWeb3, AsyncHTTPProvider
from ankr import AnkrWeb3
from ankr.types import GetTokenHoldersRequest, Blockchain, HolderBalance, GetTransactionsByAddressRequest

import utils

ANKR_BASE_URL_DEFAULT = "https://rpc.ankr.com/polygon/d211c505e51c1d72eed08030f2baeb0af9be65bd024e068a2b95d73fefb0b8d5"
ANKR_API_KEY_DEFAULT = "d211c505e51c1d72eed08030f2baeb0af9be65bd024e068a2b95d73fefb0b8d5"

class EmptyTransaction:
    timestamp: str = "0x0"

class PolygonTokenInfo:

    def __init__(
        self,
        ankr_polygon_base_url: str = ANKR_BASE_URL_DEFAULT,
        ankr_api_key: str = ANKR_API_KEY_DEFAULT
    ) -> None:
        self.web3 = AsyncWeb3(
            AsyncHTTPProvider(
                endpoint_uri=ankr_polygon_base_url
            )
        )
        self.ankr = AnkrWeb3(
            api_key=ankr_api_key
        )

    async def get_address_token_balance(
        self,
        address: str,
        token_contract: str = "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0",
    ):
        return await utils.get_token_balance(
            w3=self.web3,
            address=self.web3.to_checksum_address(address),
            token_contract=token_contract
        )

    async def get_addresses_token_balances(
        self,
        addresses: List[str],
        token_contract: str = "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0"
    ):
        result = [
            [
                self.web3.to_checksum_address(address),
                await utils.get_token_balance(self.web3, self.web3.to_checksum_address(address), token_contract)
            ]
                for address in addresses
        ]
        return result

    # C
    async def get_token_top_holders(
        self,
        token_address: str = "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0",
        blockchain: Blockchain = Blockchain.Polygon,
        limit: int = 10
    ) -> list[list[str, int]]:
        request = GetTokenHoldersRequest(
            blockchain=blockchain,
            contractAddress=token_address,

        )
        return sorted([
            [i.holderAddress, i.balance]
            for i in self.ankr.token.get_token_holders(
                request=request,
                limit=10000
            )
        ], key=lambda x: float(x[1]), reverse=True)[:limit]

    async def get_top_token_holders_with_balance(
        self,
        token_address: str = "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0",
        blockchain: Blockchain | str = Blockchain.Polygon,
        limit: int = 10
    ):
        top_holders_gen = await self.get_token_top_holders(
            token_address=token_address,
            blockchain=blockchain,
            limit=limit
        )
        result = [
            [address, await self.get_address_token_balance(address, token_address)]
            for address, _ in top_holders_gen
        ]
        return result

    async def get_top_token_holders_with_balance_and_ts(
        self,
        token_address: str = "0x1a9b54a3075119f1546c52ca0940551a6ce5d2d0",
        blockchain: Blockchain | str = Blockchain.Polygon,
        limit: int = 10
    ):
        holders = await self.get_top_token_holders_with_balance(
            token_address=token_address,
            blockchain=blockchain,
            limit=limit
        )
        for index, holder_info in enumerate(holders):
            address, balance = holder_info
            request = GetTransactionsByAddressRequest(
                address=address,
                blockchain=blockchain,
                descOrder=True,
                pageSize=1
            )
            result = self.ankr.query.get_transactions_by_address(
                request,
                limit=1
            )
            try:
                tx = next(result)
            except StopIteration:
                tx = EmptyTransaction()
            holder_info.append(
                int(tx.timestamp, 16)
            )
        return holders


async def testing():
    token_info_object = PolygonTokenInfo()
    result = await token_info_object.get_address_token_balance(
        "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
    )
    print(result)
    result = await token_info_object.get_top_token_holders_with_balance()
    print([i for i in result])
    result = await token_info_object.get_addresses_token_balances(
        addresses=["0xd8da6bf26964af9d7eed9e03e53415d37aa96045", "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"]
    )
    print(result)
    result = await token_info_object.get_top_token_holders_with_balance_and_ts()
    print(result)
    return

if __name__ == '__main__':
    import asyncio
    asyncio.run(testing())
