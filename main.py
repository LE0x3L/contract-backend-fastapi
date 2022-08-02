#Python
import web3
import json
import os

#FastAPI
from fastapi import FastAPI


http_provider = os.environ['URL_HTTP_PROVIDER']
w3 = web3.Web3( web3.HTTPProvider( http_provider ) )

abiCLH = open('./abis/CLHouse.json')
abiCLH = json.load(abiCLH)
abiCLH = abiCLH['abi']


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Contrat fastAPI"}

# Return the house name
@app.get("/HOUSE_NAME/{house_addr}")
async def read_house_name(house_addr: str):
    CLH = w3.eth.contract(address=house_addr, abi=abiCLH)
    house_name = CLH.functions.HOUSE_NAME().call()
    return {"house_name": house_name}
