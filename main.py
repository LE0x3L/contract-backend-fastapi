#Python
import web3
import json
import os

#FastAPI
from fastapi import FastAPI
from fastapi import Query, Path

http_provider = os.environ['URL_HTTP_PROVIDER']
w3 = web3.Web3( web3.HTTPProvider( http_provider ) )

# Load CLHouse ABI
abiCLH = open('./abis/CLHouse.json')
abiCLH = json.load(abiCLH)
abiCLH = abiCLH['abi']

# Instance CLApi
adrCLA = '0x7D42c58A8a9dE412Fc70fDA4688C493fa01ef60a'
abiCLA = open('./abis/ApiCLHouse.json')
abiCLA = json.load(abiCLA)
abiCLA = abiCLA["abi"]
CLA = w3.eth.contract(address=adrCLA, abi=abiCLA)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Contrat fastAPI"}

# Return the house name
@app.get("/{house_addr}/HOUSE_NAME")
async def read_house_name(
    house_addr: str = Path(
        ...,
        min_length=42,
        max_length=42,
        title="CLHouse Address",
        description="CLHouse to get the name",
        example="0x7D42c58A8a9dE412Fc70fDA4688C493fa01ef60a"
    )
):
    CLH = w3.eth.contract(address=house_addr, abi=abiCLH)
    house_name = CLH.functions.HOUSE_NAME().call()
    return {"house_name": house_name}


# Validate offchain vote
@app.get("/api/ValidateSingOffChainVote")
async def VotePropOffChain(
    _house_addr: str = Query(
        ...,
        min_length=42,
        max_length=42,
        title="CLHouse Address",
        description="CLHouse to send the Vote",
        example="0x7D42c58A8a9dE412Fc70fDA4688C493fa01ef60a"
    ),
    _voter: str = Query(
        ...,
        min_length=42,
        max_length=42,
        title="Voter Address",
        description="Address Vote",
        example="0xc27480520a875bca3874df1f533523e9ffdb1af9"
        ),
    _propId: int = Query(
        ...,
        title="proposal ID",
        description="ID of proposal to vote",
        gt=0,
        example=1
        ),
    _support: bool = Query(
        ...,
        title="Vote",
        description="True or False Vote",
        example=True
        ),
    _justification: str = Query(
        ...,
        min_length=0,
        max_length=140,
        title="Voter justification",
        example="Acepto"
        ),
    _signature: str = Query(
        ...,
        min_length=132,
        max_length=132,
        title="Vote signature",
        example="0xd9f89d03055d160f71ccccfc6d25951b28d16cecfaf6982496ba48a61edffcd55d78a3bbbdde92113637fc6b906959f7ead1d202f82f9dfdcea40d5930fdd1451c"
        )
):
    result = CLA.functions.ValidateSingOffChainVote(
        w3.toChecksumAddress( _house_addr ),
        w3.toChecksumAddress( _voter ),
        _propId,
        _support,
        _justification,
        _signature
    ).call()
    return {"result": result}
