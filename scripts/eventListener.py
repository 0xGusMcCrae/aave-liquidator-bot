from brownie import *
import time
import os
from dotenv import load_dotenv

load_dotenv()

#open terminal, import EventListener from eventListener, instantiate, run main()
#must be run using a websocket rpc connection

class EventListener:
    def __init__(self):
        self.poolAddressProvider = Contract.from_explorer(os.getenv('AAVE_POOL_ADDRESSES_PROVIDER'))
        self.pool = Contract.from_explorer(self.poolAddressProvider.getPool()) #switch this to a dontenv load
        #create event listener for Borrow
        self.borrowFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Borrow.createFilter(fromBlock='latest')
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
            if len(self.usersFound) >= 10: #can make higher or lower but for now, autodump if 10 users found
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
        output = open('./data/users.csv','a')
        print('\nDumping users to CSV...')
        while len(self.usersFound) > 0:
            output.write('\n')
            output.write(self.usersFound.pop())
        output.close()
        print('Done.')

    def handleBadConnection(self):
        #need to re-instantiate filter if we get this error:
        #ValueError: {'code': -32000, 'message': 'filter not found'}
        self.borrowFilter = web3.eth.contract(address=self.pool.address,abi=self.pool.abi).events.Borrow.createFilter(fromBlock='latest')
        
