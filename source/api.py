import hashlib

from eth_account import Account
from web3 import Web3
from web3.types import EventData
from typing import Dict, Any
from source.config import GAS_PRICE, GAS_LIMIT, CHAINID, TOKEN_ADDRESS
from source.types import *
from PyQt6.QtCore import QThread, pyqtSignal

class API:
    _session_wallet: Wallet | None = None
    event_names = [
        'PolicyCreated', 'PolicySigned', 'PolicyDeposited',
        'PaymentRequest', 'TerminateRequest', 'ClaimApproved',
        'ClaimRejected', 'PolicyTerminated'
    ]

    def __init__(self, url, address_contract, abi_contract, token_abi):
        self.web3 = Web3(Web3.HTTPProvider(url))

        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(address_contract),
            abi=abi_contract
        )

        self.token = self.web3.eth.contract(
            address=self.web3.to_checksum_address(TOKEN_ADDRESS),
            abi=token_abi
        )

    def _call(self, func_name, args: list):
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        func = getattr(self.contract.functions, func_name)
        result = func(*args).call()
        return result

    def _transact(self, func_name, args: list, private_key):
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
    
    def _execute(self,
                 func_name: str,
                 args: list[int | str],
                 approve_amount: int | None = None
    ):
        if self._session_wallet is None:
            raise ConnectionError("Not authorized")

        private_key = self._session_wallet.private_key

        if approve_amount is not None and approve_amount > 0:
            self.approveToken(self.contract.address, approve_amount)

        return self._transact(func_name, args, private_key)

    def _get_events(
            self,
            event_name: str,
            from_block: int | None = 0,
            to_block: int | None = None,
            argument_filters: Dict[str, Any] | None = None
    ) -> list[EventData]:
        if not self.web3.is_connected():
            raise ConnectionError("Web3 not connected")

        event = getattr(self.contract.events, event_name)

        if to_block is None:
            to_block = self.web3.eth.block_number

        filter_params = {
            'fromBlock': from_block,
            'toBlock': to_block,
        }
        if argument_filters:
            filter_params['argument_filters'] = argument_filters

        try:
            events = event.get_logs(**filter_params)
            return events
        except Exception as e:
            print(f"Error getting events: {e}")
            return []

    def _parse_event_to_transaction(self, event: EventData) -> Transaction:
        args = event['args']
        event_name = event['event']


        if event_name == 'TerminateRequest':
            from_addr = args['policyholder']
            to_addr = args['insurer']
        elif event_name in ['PolicyCreated', 'PaymentRequest']:
            from_addr = args.get('insurer', args.get('policyholder'))
            to_addr = self.contract.address
        else:
            from_addr = args.get('insurer', args.get('policyholder', ''))
            to_addr = args.get('policyholder', args.get('insurer', ''))

        tx_data = {
            'tx_hash': event['transactionHash'].hex(),
            'block_number': event['blockNumber'],
            'timestamp': args.get('timestamp'),
            'event_type': event_name,
            'policy_id': args.get('policyId', 0),
            'from_address': from_addr,
            'to_address': to_addr,
            'amount': args.get('amount', 0),
            'data': {}
        }

        if event_name == 'PolicyCreated':
            tx_data['data'] = {
                'name': args['name'],
                'payoutAmount': args['payoutAmount'],
                'durationWork': args['durationWork']
            }
        elif event_name == 'PaymentRequest':
            tx_data['data'] = {'proofs': args['proofs']}
        elif event_name == 'ClaimRejected':
            tx_data['data'] = {'reason': args['reason']}

        return Transaction(**tx_data)

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

    def getUserInfo(self, address) -> User:
        checksum = self.convertAddress(address)

        raw_user = self._call("getUserInfo", [checksum])
        return User(
            role=IntToRole[raw_user[1]],
            policies=list(raw_user[2]),
            address = self._session_wallet.address,
        )

    def getPolicyData(self, id: int) -> PolicyData:
        raw_policy = self._call("getPolicyData", [id])
        return PolicyData(
            startDate= raw_policy[0],
            endDate= raw_policy[1],
            durationWork= raw_policy[2],
            countOfPayout= raw_policy[3],
            hasPendingClaim= raw_policy[4],

            insurer= raw_policy[5],
            policyholder= raw_policy[6],
            payoutAmount= raw_policy[7],
            sumDeposits= raw_policy[8],

            name= raw_policy[9],
            conditions= raw_policy[10],
            status= raw_policy[11],
        )

    def isRegistered(self, address):
        checksum = self.convertAddress(address)
        return self._call("isRegistered", [checksum])

    def getPolicyCount(self):
        return self._call("getPolicyCount", [])

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

            self._transact("login", [int(hash, 16)], self._session_wallet.private_key)
            user = self.getUserInfo(self._session_wallet.address)
            return user
        except Exception as e:
            self._session_wallet = None
            raise Exception(f"Login failed: {str(e)}")

    def logout(self):
        self._transact("logout", [], self._session_wallet.private_key)
        self._session_wallet = None

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

            if isinstance(role, int):
                self._transact("registration", [role, int(hash, 16)], self._session_wallet.private_key)
            else:
                raise Exception(f"Invalid role type")

            user = self.getUserInfo(self._session_wallet.address)
            return user

        except Exception as e:
            self._session_wallet = None
            raise Exception(f"Registration failed: {str(e)}")

    def createPolicy(self,
                     name: str,
                     conditions: str,
                     payoutAmount: int,
                     durationWork: int,
                     countOfPayout: int):
        if self._session_wallet != None:
            args = [name, conditions, payoutAmount, durationWork, countOfPayout]
            private_key = self._session_wallet.private_key
            return self._transact("createPolicy", args, private_key)
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
        return self._execute("concludePolicy", [policyId, premium], approve_amount=premium)

    def deposit(self, policyId: int, amount: int):
        return self._execute("deposit", [policyId, amount], approve_amount=amount)

    def fileClaim(self, policyId: int, proofs: str):
        return self._execute("fileClaim", [policyId, proofs])

    def terminateRequest(self, policyId: int):
        return self._execute("terminateRequest", [policyId])

    def approved(self, policyId: int):
        return self._execute("approved", [policyId])

    def rejected(self, policyId: int):
        return self._execute("rejected", [policyId])

    def terminatePolicy(self, policyId: int):
        return self._execute("terminatePolicy", [policyId])

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

    def get_policy_transactions(self, policy_id: int) -> list[Transaction]:
        all_events = []
        for event_name in self.event_names:
            events = self._get_events(
                event_name=event_name,
                argument_filters={"policyId": policy_id}
            )
            all_events.extend(events)
        all_events.sort(key=lambda x: x['blockNumber'])

        return [self._parse_event_to_transaction(e) for e in all_events]

    def get_user_transactions(
            self,
            role: str,
            from_block: Optional[int] = None,
            to_block: Optional[int] = None
    ) -> list[Transaction]:
        if self._session_wallet is None:
            raise ConnectionError("Not authorized")
        checksum = self.convertAddress(self._session_wallet.address)

        all_events = []
        for event_name in self.event_names:
            events = self._get_events(
                event_name=event_name,
                from_block=from_block,
                to_block=to_block,
                argument_filters={role: checksum}
            )
            all_events.extend(events)

        unique_events = {}
        for event in all_events:
            key = f"{event['transactionHash'].hex()}_{event['logIndex']}"
            unique_events[key] = event
        sorted_events = sorted(unique_events.values(), key=lambda x: x['blockNumber'])

        transactions = [self._parse_event_to_transaction(e) for e in sorted_events]

        return transactions

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