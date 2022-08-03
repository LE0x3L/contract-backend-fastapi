# contract-backend-fastapi

FastAPI implementation to interact with solidity contracts in blockchain

## How to install

Once you have cloned the repo, run in the terminal:

```sh
python -m venv venv
source ./venv/bin/activate
pip install fastapi uvicorn web3
```

## How to run

To initiate the server run in the terminal:

```sh
source ./venv/bin/activate
export URL_HTTP_PROVIDER="put your url from alchemy, infura or any other provider that you use"
export ACC_PRIVATE_KEY=PrivateKeyOfTheWalletToPayTransacctions
uvicorn main:app --reload
```

This normally starts `uvicorn` running on `http://127.0.0.1:8000`