Strategies table should make the initial cost basis per trade

ROI needs to be calculated on a per trade basis
e.g. I can't have a cost basis of 75.00 

I need a premium per contract per share

To get the current_cost_basis
what is cost basis? The amount of money invested or at risk
Current cost basis is the cost basis where I have subtracted all the gains.
The purpose of this is to provide me with a metric on where I am okay with taking assignment on that strategy.
Should I do that on the trade level or should I do it on the strategy level?



Current cost_basis will be

for a put:
    sum the all strikes prices for open puts and divided by the number of contracts

for calls:
    Done: Need a way to capture purchase value
    Need to persist when rolling

# total_premium_received is the total, not per contract
# For puts get the strike and average them by adding the strikes and dividing by number of contracts for the new cost_basis
# Divid total_premium by num_contracts
# 

# Going to roll trade 16
# when done trade 16 should be closed
# trade 17 should be opened
# Because of my earlier mistake the average_cost_basis for OKE should go up (68.75)
# Adjusted cost_basis should change (add .05, subtract .50) (old one closes at .05, new one will be openening at .50)
# 61.98 should go down

# only roll 1 of the 2 contracts
# Trade 22 will be closed (num_contracts updated to 1)
# Trade 23 will be same data as trade 22, but open and only 1 contract
# Trade 24 will be opened with new trade data