"# aave-liquidator-bot" 

A work in progress

Event listener picks up accounts that borrow from aave and writes them to CSV file

Bot will take these accounts and check for liquidatable health factors and acquire other info from AAVE needed to liquidate, determine profitability, etc

Bot will then use a deployed liquidator contract to get a flashloan from AAVE to liquidate the account
