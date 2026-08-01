import hashlib

from eth_account import Account
from web3 import Web3
from source.config import GAS_PRICE, GAS_LIMIT, CHAINID, TOKEN_ADDRESS
from source.utils import *
from PyQt6.QtCore import QThread, pyqtSignal

class API:
    _session_wallet: Wallet
    def __init__(self, url, address_contract, abi_contract):
        self.web3 = Web3(Web3.HTTPProvider(url))

        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(address_contract),
            abi=abi_contract
        )

        token_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "success", "type": "bool"}],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"}
                ],
                "name": "balanceOf",
                "outputs": [
                    {"name": "balance", "type": "uint256"}
                ],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]

        self.token = self.web3.eth.contract(
            address=self.web3.to_checksum_address(TOKEN_ADDRESS),
            abi=token_abi
        )

        self._session_wallet = Wallet(
            address="0x00000000000000000000000000000",
            private_key=""
        )

    def call(self, func_name, args: list):
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        func = getattr(self.contract.functions, func_name)
        result = func(*args).call()
        return result

    def transact(self, func_name, args: list, private_key):
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        func = getattr(self.contract.functions, func_name)
        sender = Account.from_key(private_key).address

        transactionInfo = func(*args).build_transaction({
            'chainId': CHAINID,
            'gas': GAS_LIMIT,
            'gasPrice': GAS_PRICE,
            'nonce': self.web3.eth.get_transaction_count(sender)
        })

        signed = self.web3.eth.account.sign_transaction(transactionInfo, private_key)
        sendTrans = self.web3.eth.send_raw_transaction(signed.raw_transaction)
        answer = self.web3.eth.wait_for_transaction_receipt(sendTrans)

        if answer.status == 0:
            try:
                details = self.web3.eth.get_transaction(sendTrans)
                self.web3.eth.call({
                    'from': details['from'],
                    'to': details['to'],
                    'data': details['input']
                })
            except Exception as e:
                raise Exception(str(e))

        return answer

    def convertAddress(self, address):
        if isinstance(address, str):
            addrStr = address
        elif hasattr(address, 'hex'):
            addrStr = address.hex()
            if not addrStr.startswith("0x"):
                addrStr= "0x" + addrStr
        elif isinstance(address, (bytes, bytearray)):
            addrStr = "0x" + address.hex()
        else:
            addrStr = str(address)

        if not (addrStr.startswith("0x") and len(addrStr) == 42):
            raise ValueError(f"Invalid address format: {addrStr}")
        return Web3.to_checksum_address(addrStr)

    def registration(self, role, password: str, private_key) -> User:
        try:
            account = Account.from_key(private_key)
            address = account.address

            self._session_wallet = Wallet(
                address=self.web3.to_checksum_address(address),
                private_key=HexBytes(private_key)
            )
            password_bytes = password.encode('utf-8')
            hash = hashlib.sha256(password_bytes).hexdigest()

            #print(f"=== DEBUG REGISTRATION ===")
            #print(f"Address: {address}")
            #print(f"Password: {password}")
            #print(f"Hash (hex): {hash}")
            #print(f"Hash (int): {int(hash, 16)}")

            if type(role) == str:
                self.transact("registration", [RoleEnum[role], int(hash, 16)], self._session_wallet.private_key)
            elif type(role) == int:
                self.transact("registration", [role, int(hash, 16)], self._session_wallet.private_key)
            else:
                self._session_wallet = Wallet(
                    address="0x00000000000000000000000000000",
                    private_key=""
                )
                raise Exception("Incorrect role type")

            user = self.getUserInfo(self._session_wallet.address)
            return user

        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")

    def login(self, password: str, private_key) -> User:
        try:
            account = Account.from_key(private_key)
            address = account.address
            password_bytes = password.encode('utf-8')
            hash = hashlib.sha256(password_bytes).hexdigest()
            self._session_wallet = Wallet(
                address=self.web3.to_checksum_address(address),
                private_key=HexBytes(private_key)
            )

            #print(f"=== DEBUG LOGIN ===")
            #print(f"Address: {address}")
            #print(f"Password: {password}")
            #print(f"Hash (hex): {hash}")
            #print(f"Hash (int): {int(hash, 16)}")

            self.transact("login", [int(hash, 16)], self._session_wallet.private_key)
            user = self.getUserInfo(self._session_wallet.address)
            return user
        except Exception as e:
            self._session_wallet = None
            raise Exception(f"Login failed: {str(e)}")

    def logout(self):
        self.transact("logout", [], self._session_wallet.private_key)
        self._session_wallet = None

    def getUserInfo(self, address) -> User:

        checksum = self.convertAddress(address)

        raw_user = self.call("getUserInfo", [checksum])
        return User(
            role=IntToRole[raw_user[1]],
            policies=list(raw_user[2]),
            transactions=list(raw_user[3]),
            address = self._session_wallet.address,
        )

    def getTransInfo(self, id: int) -> Transaction:
        raw_trans = self.call("getTransInfo", [id])
        return Transaction(
            transactionType = TransactionType[raw_trans[0]],
            addressFrom = raw_trans[1],
            addressTo = raw_trans[2],
            policyId = raw_trans[3],
            amount = raw_trans[4],
            unixTime = raw_trans[5]
        )

    def getPolicyData(self, id: int) -> PolicyData:
        raw_policy = self.call("getPolicyData", [id])
        return PolicyData(
            id = raw_policy[0],
            name = raw_policy[1],
            conditions = raw_policy[2],
            payoutAmount = raw_policy[3],
            durationWork = raw_policy[4],
            startDate = raw_policy[5],
            endDate = raw_policy[6],
            status = PolicyStatus[raw_policy[7]],
            insurer = raw_policy[8],
            policyholder = raw_policy[9],
            sumDeposits = raw_policy[10],
            countOfPayout = raw_policy[11],
            proofs = raw_policy[12],
        )

    def isRegistered(self, address):
        checksum = self.convertAddress(address)
        return self.call("isRegistered", [checksum])

    def getPolicyCount(self):
        return self.call("getPolicyCount", [])

    def getTransactionCount(self):
        return self.call("getTransactionCount", [])

    def createPolicy(self,
                     name: str,
                     conditions: str,
                     payoutAmount: int,
                     durationWork: int,
                     countOfPayout: int):
        if self._session_wallet != None:
            args = [name, conditions, payoutAmount, durationWork, countOfPayout]
            private_key = self._session_wallet.private_key
            return self.transact("createPolicy", args, private_key)
        else:
            raise ConnectionError("Not authorized")

    def approved(self, policyId: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            return self.transact("approved", [policyId], private_key)
        else:
            raise ConnectionError("Not authorized")

    def rejected(self, policyId: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            return self.transact("rejected", [policyId], private_key)
        else:
            raise ConnectionError("Not authorized")

    def terminatePolicy(self, policyId: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            return self.transact("terminatePolicy", [policyId], private_key)
        else:
            raise ConnectionError("Not authorized")

    def approveToken(self, spender_address: str, amount: int):
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        if not self._session_wallet:
            raise ConnectionError("Not authorized")

        try:
            private_key = self._session_wallet.private_key

            transaction = self.token.functions.approve(
                self.web3.to_checksum_address(spender_address),
                amount
            ).build_transaction({
                'chainId': CHAINID,
                'gas': GAS_LIMIT,
                'gasPrice': GAS_PRICE,
                'nonce': self.web3.eth.get_transaction_count(
                    Account.from_key(private_key).address
                )
            })

            signed = self.web3.eth.account.sign_transaction(transaction, private_key)
            sendTrans = self.web3.eth.send_raw_transaction(signed.raw_transaction)
            answer = self.web3.eth.wait_for_transaction_receipt(sendTrans)

            return answer

        except Exception as e:
            raise Exception(f"Approve failed: {str(e)}")

    def get_user_balance(self) -> int:
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        if not self._session_wallet:
            raise ConnectionError("Not authorized")

        try:
            balance = self.token.functions.balanceOf(
                    self.web3.to_checksum_address(self._session_wallet.address)
            ).call()

            return balance

        except Exception as e:
            raise Exception(f"Failed to get balance: {str(e)}")

    def concludePolicy(self, policyId: int, premium: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            self.approveToken(self.contract.address, premium)
            return self.transact("concludePolicy", [policyId, premium], private_key)
        else:
            raise ConnectionError("Not authorized")

    def deposit(self, policyId: int, amount: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            e = self.approveToken(self.contract.address, amount)
            print(e)
            return self.transact("deposit", [policyId, amount], private_key)
        else:
            raise ConnectionError("Not authorized")

    def fileClaim(self, policyId: int, proofs: str):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            return self.transact("fileClaim", [policyId, proofs], private_key)
        else:
            raise ConnectionError("Not authorized")

    def terminateRequest(self, policyId: int):
        if self._session_wallet != None:
            private_key = self._session_wallet.private_key
            return self.transact("terminateRequest", [policyId], private_key)
        else:
            raise ConnectionError("Not authorized")

    # Тут только проверка на статус и обладателя
    def loadPolicies(self, filter: PolicyData):
        result = []
        count = self.getPolicyCount() + 1
        try:
            if filter.insurer == self._session_wallet.address or filter.policyholder == self._session_wallet.address:
                current_user = self.getUserInfo(self._session_wallet.address)
                for i in current_user.policies:
                    result.append(self.getPolicyData(i))
            else:
                for i in range(0, count):
                    temp = self.getPolicyData(i)
                    if filter.status == temp.status and temp.id != 0:
                        result.append(temp)
        except Exception as e:
            raise e

        return result

    def loadTransactions(self):
        result = []
        if self._session_wallet.address != "0x00000000000000000000000000000":
            try:
                current_user = self.getUserInfo(self._session_wallet.address)
                for i in current_user.transactions:
                    result.append(self.getTransInfo(i))
            except Exception as e:
                raise e
        return result

class Web3Worker(QThread):
    result_ready = pyqtSignal(object)
    error_occured = pyqtSignal(str)

    def __init__(self, api, func, args):
        super().__init__()
        self.api = api
        self.func = func
        self.args = args

    def run(self):
        try:
            result = self.func(*self.args)
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occured.emit(str(e))