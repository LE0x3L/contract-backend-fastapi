# Python
import web3
import json
import os

# FastAPI
from fastapi import FastAPI
from fastapi import Query, Path
from fastapi.middleware.cors import CORSMiddleware


# Basic Configurations


http_provider = os.environ[ 'URL_HTTP_PROVIDER' ]
w3 = web3.Web3( web3.HTTPProvider( http_provider ) )
chainId = w3.eth.chain_id

acc_key = os.environ[ 'ACC_PRIVATE_KEY' ]
acc2paid = w3.eth.account.privateKeyToAccount( acc_key )

## Load CLHouse ABI
abiCLH = open( './abis/CLHouse.json' )
abiCLH = json.load( abiCLH )
abiCLH = abiCLH[ 'abi' ]

## Instance CLApi
adrCLA = '0x7D42c58A8a9dE412Fc70fDA4688C493fa01ef60a'
abiCLA = open( './abis/ApiCLHouse.json' )
abiCLA = json.load( abiCLA )
abiCLA = abiCLA[ "abi" ]
CLA = w3.eth.contract( address=adrCLA, abi=abiCLA )


# fastApi Config


app = FastAPI(
    title="CLBApi Test",
    description="Backend API test for CL contracts",
    version="1.0"
)

'''
"*" is for testing purposes only
For deployment, change it to the allowed website(s)
'''
origins = [
    "*"
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
)


# endpoint configurations


# Default call
@app.get("/")
async def root():
    return { "message": "Contract fastAPI" }


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
    CLH = w3.eth.contract( address=house_addr, abi=abiCLH )
    house_name = CLH.functions.HOUSE_NAME().call()
    return { "house_name" : house_name }


# Validate offchain vote
@app.get("/api/ValidateSingOffChainVote")
async def ValidateSingOffChainVote(
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
    return { "result" : result }

# Send offchain vote to CLH
@app.get("/{house_addr}/VotePropOffChain")
async def VotePropOffChain(
    house_addr: str = Path(
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
    _signR: str = Query(
        ...,
        title="sign R",
        min_length=66,
        max_length=66,
        description="r signature value",
        example="0xd2134ec8956ebca22d6b3af6e3e2e597526c1992f5593441e8c406bfbfb8e738"
        ),
    _signS: str = Query(
        ...,
        title="sign S",
        min_length=66,
        max_length=66,
        description="s signature value",
        example="0x058aa274bf9d822c831ae046e42b174e902891e64882245aa0bd322005472d7c"
        ),
    _signV: int = Query(
        ...,
        title="sign V",
        description="v signature value",
        ge=27,
        le=28,
        example=28
        )
):
    txCLH = CLH.functions.VotePropOffChain(
        w3.toChecksumAddress( _voter ),
        _propId,
        _support,
        _justification,
        _signR,
        _signS,
        _signV
    ).buildTransaction({
        'chainId': chainId,
        'gas': 20000000,
        'maxFeePerGas': w3.toWei( '4', 'gwei' ),
        'maxPriorityFeePerGas': w3.toWei( '2', 'gwei' ),
        'nonce': w3.eth.get_transaction_count( acc2paid.address ),
        'from': acc2paid.address,
    })

    signed_txn = w3.eth.account.sign_transaction( txCLH, acc2paid.privateKey )

    w3.eth.send_raw_transaction( signed_txn.rawTransaction )
    result = w3.eth.wait_for_transaction_receipt( signed_txn.hash )
    return { "result" : result }