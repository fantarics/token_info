from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Union
from token_info import PolygonTokenInfo
from ankr.types import Blockchain

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/docs",
)
app.state.polygon_token_info = PolygonTokenInfo()


class AddressRequest(BaseModel):
    address: str


class BalanceResponse(BaseModel):
    balance: int


class ErrorResponse(BaseModel):
    error: str
    message: str


# Endpoint to get balance for a single address
@app.get("/get_balance")
async def get_balance(request: Request, request_body: AddressRequest):
    polygon_token_info: PolygonTokenInfo = request.app.state.polygon_token_info
    balance = await polygon_token_info.get_address_token_balance(
        request_body.address
    )
    return BalanceResponse(
        balance=balance
    )


# Model for batch balance request
class AddressBatchRequest(BaseModel):
    addresses: List[str]
    token_contract: str | None = None


class BalanceBatchResponse(BaseModel):
    addresses: List[List[Union[str, int]]]


# Endpoint to get balances for a batch of addresses
@app.get("/get_balance_batch")
async def get_balance_batch(request: Request, request_body: AddressBatchRequest):
    polygon_token_info: PolygonTokenInfo = request.app.state.polygon_token_info
    result = await polygon_token_info.get_addresses_token_balances(
        request_body.addresses,
        request_body.token_contract
    )
    return BalanceBatchResponse(
        addresses=result
    )


class TopHoldersRequest(BaseModel):
    token_address: str | None = None
    limit: int = 10
    blockchain: str | None = Blockchain.Polygon


class TopHoldersResponse(BaseModel):
    addresses: List[List[Union[str, int]]]


@app.get("/get_token_top_holders")
async def get_token_top_holders(request: Request, request_json: TopHoldersRequest):
    if 1 > request_json.limit > 10:
        return dict(status="Error", message="Limit out of range 1-10")
    polygon_token_info: PolygonTokenInfo = request.app.state.polygon_token_info
    result = await polygon_token_info.get_top_token_holders_with_balance(
        token_address=request_json.token_address,
        blockchain=request_json.blockchain
    )
    return TopHoldersResponse(
        addresses=result
    )


@app.get("/get_token_top_holders_and_ts")
async def get_token_top_holders(request: Request, request_json: TopHoldersRequest):
    if 1 > request_json.limit > 10:
        return dict(status="Error", message="Limit out of range 1-10")
    try:
        polygon_token_info: PolygonTokenInfo = request.app.state.polygon_token_info
        result = await polygon_token_info.get_top_token_holders_with_balance_and_ts(
            token_address=request_json.token_address,
            blockchain=request_json.blockchain,
            limit=request_json.limit
        )
    except Exception as e:
        print(e)
        return dict(status="Error", message="Please try again")
    return TopHoldersResponse(
        addresses=result
    )


@app.get("/ping")
async def ping_pong(request: Request):
    return "pong"



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
