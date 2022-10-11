from brownie import *
import time

#open terminal, import EventListener from eventListener, instantiate, run main()

#then again, this is just the event listener, really all I want it to do is
#feed addresses to be monitored with the liquidator bot - so I don't really
#need to keep things separate.

#so the goal of this file is to have the event listener methods ready to
#be called by main to get the the logs to a file that can be processed in
#main - or I could create another class to process the files to get the 
#addresses ready. and then have the liquidator bot be a class also - so it
#will have the logic build out, but everything is actually run through main.py

#ok and so we can have the event listener find  this:
#[AttributeDict({'args': AttributeDict({'reserve': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1', 'onBehalfOf': '0x00899ADda769602c9526043158585099bEC8829A', 'referralCode': 0, 'user': '0x00899ADda769602c9526043158585099bEC8829A', 'amount': 78105573720542559333}), 'event': 'Supply', 'logIndex': 4, 'transactionIndex': 1, 'transactionHash': HexBytes('0x1291402b1d4f84b732b66545477596b08417201a75d94570fcb9f2965c818d02'), 'address': '0x794a61358D6845594F94dc1DB02A252b5b4814aD', 'blockHash': HexBytes('0xf173f6109f0dbe7c803243a1be3af65fca1764d2affa2467edad0942af0c741b'), 'blockNumber': 29613988})]
#we want to capture that and just get the 'user' 

#im gonna capture the next one in a variable and see what I can do to access that

#arbitrum aave pool address is '0x794a61358D6845594F94dc1DB02A252b5b4814aD'

class EventListener:
    def __init__(self, address):
        self.pool = Contract.from_explorer(address) #switch this to a dontenv load
        #create event listeners for Borrow, supply, repay, withdraw
        #might only need borrowFilter - the others don't have much bearing on who can get liqd
        #still could be useful but borrow is definitely the main one to check ( could do all tho, not really any harder )
        self.borrowFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Borrow.createFilter(fromBlock='latest')
        self.supplyFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Supply.createFilter(fromBlock='latest')
        self.repayFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Repay.createFilter(fromBlock='latest')
        self.withdrawFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Withdraw.createFilter(fromBlock='latest')
        #so i can loop through and grab logs from each filter (since the actual events arent important)
        self.filters = [self.borrowFilter,self.supplyFilter,self.repayFilter,self.withdrawFilter]
        self.usersFound = [] #an array of all users found since last file dump
    
    
    def main(self): #either keep this here or move it to main.py
        while(True):
            time.sleep(5)
            try: 
                result = self.borrowFilter.get_new_entries()
            except:
                self.handleBadConnection()
                result = self.borrowFilter.get_new_entries()
            if result != []:
                user = self.parseUser(result)
                print("\nFound users!\n")
                print(user)
                print(f'{len(self.usersFound)} users have been found since last dump.')
            if len(self.usersFound) > 10: #can make higher or lower but for now, autodump if 10 users found
                self.dumpUsersToFile()
            



    def parseUser(self,result): #pass in event filter result
        usersLocal = [] #just the users from this specific call, not the same as the state variable of all users found over time
        for item in range(0,len(result)):
            temp = dict(result[item])
            temp = dict(temp['args'])
            usersLocal.append(temp['user'])
            self.usersFound.append(temp['user'])
        return usersLocal
        
    def dumpUsersToFile(self):
        output = open('../data/users.csv','a')
        while len(self.usersFound) > 0:
            output.write('\n')
            output.write(self.usersFound.pop())
        output.close()

    def handleBadConnection(self):
        #basically need to re-instantiate all filters if we get this error:
        #ValueError: {'code': -32000, 'message': 'filter not found'}
        self.borrowFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Borrow.createFilter(fromBlock='latest')
        self.supplyFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Supply.createFilter(fromBlock='latest')
        self.repayFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Repay.createFilter(fromBlock='latest')
        self.withdrawFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Withdraw.createFilter(fromBlock='latest')
       

