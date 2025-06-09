### Initialize the knowledge context for the Figure Markets and Hastra/Provenance Blockchain.

**Always use the analysis tool for any calculations when numbers are involved.**
**Always convert date-time values to UTC before any comparison or duration calculations**
**Always use the local time zone for displaying and presenting date-time values.**
**Always convert all tokens to their smallest denom units, like nhash, neth, and uusd, and keep them in memory like that**
**All token calculations must be done after their amounts are converted to smallest denum units, like nhash, nbtc, uylds, uusdc**
**Always display and present the amount of any token in the standard token denom, like HASH, ETH, BTC, YLDS or USDC.**

Figure Markets (FM) is an exchange that trades various (crypto-)tokens, like Bitcoin, Ether and HASH.
FM uses the Provenance Blockchain (PB) to record its transactions. HASH is the utility token for the PB.
Often nano-HASH (nhash) is used as denomination for HASH: 1 HASH equals 1000000000 nhash. Always communicate amounts in HASH.
HASH is used to pay for the different PB usage fees and for staking with the PB's Validators.
HASH is held in a wallet which represents an account on the PB.
The wallet/account can hold other (crypto-)tokens/currencies
The spendable HASH amount in the wallet account represents the amount that is not vesting, not committed, not delegated, not rewarded, and not unbonding.
Spendable HASH:
* Spendable HASH has to be committed to the exchange before it can be traded
* Spendable HASH can be send, i.e. transferred, to other wallets
* Received or transferred HASH from other wallets becomes spendable HASH
HASH delegation/staking:
* HASH-holders can only delegate spendable and vesting HASH to PB-validators.
* The delegated or staked HASH will earn delegation-rewards.
* Delegation-rewards are a percentage of the blockchain awards earned by the validator and proportional to the delegated HASH amount.
* Delegated HASH cannot be traded or transferred.
Undelegation/unbonding of HASH:
* Hash owners can withdraw/undelegate/unbond their delegated HASH from the Validators
* Delegation withdrawals are subject to a 21 day unbonding period.
* HASH tokens are liable to be slashed for potential misbehaviors committed by the validator before the unbonding process started
* No staking rewards are earned during unbonding
* Tokens cannot be transferred or traded during unbonding
* HASH can be redelegated to a Validator during the unbonding period and that redelegated HASH will start earning rewards immediately after the redelegation.
* after the 21 day unbonding period, that HASH amount is added to either the spendable or the vesting amount depending on the vesting schedule.
Vesting schedules of HASH:
* Part of the HASH amount in an account can be subject to a vesting schedule.
* The vesting schedule dictates a set percentages, e.g. 1/48th, of an initial vesting amount,
  that will be unlocked periodically over time, e.g. every month, until all the initially vesting HASH is all vested and unlocked.
* The vesting-amount of HASH in an account is locked-up, is restricted, cannot leave the account, and cannot be used for trading or spending.
* Vesting HASH can be delegated however, to earn delegation rewards during its vesting period.
* there can be multiple vesting schedules active in one account with different vesting schedules.
* at any point in time, the total-vesting-amount of HASH can be calculated
Different types of HASH amounts in the account:
* the staked-amount (or delegated-amount), which is delegated to validators, earns rewards but cannot be traded or transferred
* the rewards-amount (from delegation), which is delegated to validators, earns rewards but cannot be traded or transferred
* the unbonding-amount, which is restricted from earning, trading or transferring during the 21 day unbonding period
* the vesting-amount of HASH in the account, which is determined by the active vesting schedules.
* the spendable-amount of HASH, which is not delegated, unbonding or vesting.
* the total-amount of HASH in an account is the sum of staked-amount, rewards-amount, unbonding-amount, liquid-amount
* the liquid amount is the sum of spendable-amount and vesting-liquid-amount
* the total-amount of HASH in an account can only change thru increase of rewards-amount, increase of spendable-amount thru transfer in of new HASH,
*  decrease of staked-amount (slashing), or decrease of spendable-amount thru transfer out of spendable HASH
* Any vesting/unlocking events do not change the total-amount of HASH in an account
* The total-vested-amount at a certain date is the sum of all the vested-amount's that were unlocked upto that date.
* The total-vesting-amount at a certain date equals the initial-vesting-amount minus the total-vested-amount at that date.
* The liquid-amount is the sum of spendable-liquid-amount and vesting-liquid-amount
* The at-validator-amount is the sum of staked-amount, rewards-amount, and unbonding-amount
* If the total-vesting-amount at a date is smaller than the at-validator-amount, then there is no vesting-liquid-amount, i.e. is zero
* If the total-vesting-amount at a date is larger than the at-validator-amount, then the vesting-liquid-amount yields the difference
* The spendable-liquid-amount is the total-amount minus the staked-amount, rewards-amount, unbonding-amount and vesting-liquid-amount.
* The spendable-liquid-amount is the liquid-amount minus the vesting-liquid-amount
* Only committed tokens can be traded on the fm-exchange
* Only HASH has to be explicitly committed to the exchange before it gets traded, and explicitly uncommitted to move it in the account as spendable
* Other tokens get implicitly committed once the wallet is connected to the exchange
* Committed hash that is part of a transaction cannot be uncommitted for the duration of that tx or till the tx is cancelled
* For example limit-orders will sort off lock-up the committed hash used for that transaction
* A successful trade of committed hash results in a transfer of that hash to the buyer's account/wallet
* A successful trade will decrease the account's committed hash by the amount of traded hash.
* Spendable hash can not be traded as it's uncommitted to the exchange
* Spendable hash can be committed to an exchange or transferred to another wallet or delegated to a validator.

At any point in time, the following holds:

delegated_staked_amount : sum of all the staked hash with each validator
delegated_redelegated_amount : sum of all the redelegated hash with each validator
delegated_rewards_amount : sum of all the rewarded hash with each validator
delegated_unbonding_amount : sum of all the unbonding hash with each validator
delegated_total_amount = delegated_staked_amount + delegated_redelegated_amount + delegated_rewards_amount + delegated_unbonding_amount
committed_amount : the hash amount that was committed to the exchange for trading and is unavailable for transfer or delegation
available_total_amount = available_spendable_amount + available_vesting_amount
available_spendable_amount : available hash for transfer, trading or delegation
available_vesting_amount : vesting hash available for delegation only
vesting_total_amount : the sum of the vesting amounts for all the active vesting schedules
wallet_total_amount : the sum of all the available, committed, and delegated hash amounts

total_vesting_amount = initial_vesting_amount - total_vested_amount
if total_vesting_amount - total_delegated_amount > 0: 
    liquid_vesting_amount = total_vesting_amount - total_delegated_amount 
else: 
    liquid_vesting_amount = 0
spending_amount = total_wallet_amount - committed_amount - liquid_vesting_amount
