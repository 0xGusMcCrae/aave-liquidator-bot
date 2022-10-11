from brownie import *
import time
import os
from dotenv import load_dotenv

load_dotenv()

#open terminal, import EventListener from eventListener, instantiate, run main()


class EventListener:
    def __init__(self):
        self.pool = Contract.from_explorer(os.getenv('AAVE_ARB_MAIN_POOL')) #switch this to a dontenv load
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
       

