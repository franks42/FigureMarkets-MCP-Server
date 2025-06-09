**Always use the analysis tool for any calculations when numbers are involved.**
**Always convert date-time values to UTC before any comparison or duration calculations**
**Always use the local time zone for displaying and presenting date-time values.**
**Always convert all tokens to their smallest denom units, like nhash, neth, and uusd, and keep them in memory like that**
**All token calculations must be done after their amounts are converted to smallest denum units, like nhash, nbtc, uylds, uusdc**
**Always display and present the amount of any token in the standard token denom, like HASH, ETH, BTC, YLDS or USDC.**

A wallet contains a `wallet_total_amount` of HASH.

In general, HASH in a wallet can be traded on an exchange for other assets (e.g. sell/buy HASH for/with USD), transferred to or from other wallets (send or receive), or delegated to and undelegated from validators. 

New HASH is added to a wallet through buying HASH on an exchange (e.g. USD=>HASH), receiving HASH from an other wallet, or by earning delegation rewards from the delegation/staking with a validator. HASH is removed from a wallet by selling HASH on an exchange (e.g. HASH=>USD), by sending HASH to another wallet, or by the slashing of HASH by the blockchain governance policy enforcement (e.g. because a validator misbehaved).

We distinguish different buckets of HASH in the wallet where each bucket has its own policy that restrict the possible operations on that HASH.

The wallet's HASH can be delegated to or staked with Validators. Delegated HASH is subject to the associated delegation policy. This delegation policy does not allow the delegated hash to be traded or transferred. However, delegated hash can be undelegated or unbonded, after an unbonding period of 21 days.

The delegated_total_amount is the sum of the delegated_staked_amount, the delegated_rewards_amount, and the delegated_unbonding_amount:

```delegated_total_amount = delegated_staked_amount + delegated_rewards_amount + delegated_unbonding_amount```

 All the HASH of this `delegated_total_amount` is subject to the delegation policy.

The `available_total_amount` is all the HASH in the wallet that is not associated with delegation and is not subject to the delegation policy:

```available_total_amount = wallet_total_amount - delegated_total_amount```

We further divide this `available_total_amount` of HASH in buckets of `available_spendable_amount`, `available_committed_amount`, and `available_unvested_amount`, and rewrite the equation to show that `available_spendable_amount` is a dependent variable and calculated from the three other amounts:

```available_spendable_amount = available_total_amount - available_committed_amount - available_unvested_amount```

The policy pertaining to `available_committed_amount` is that only those HASH tokens can be traded on the exchange, cannot be transferred or delegated, but can be uncommitted to the `available_spendable_amount` bucket.

The HASH tokens in the `available_spendable_amount` can be committed to the exchange, can be transferred to other wallets, and can be delegated.

Lastly we have a subset of wallets that are subject to vesting schedules, and an associated policy pertaining to an `available_unvested_amount`. HASH tokens in this bucket cannot be committed to an exchange, cannot be transferred to other wallets, but can be delegated to validators. 

A HASH vesting schedule defines a `vesting_initial_amount`, a `vesting_start_date`, an `vesting_end-date`, and a schedule of vesting events. The `vesting_unvested_amount` equals the `vesting_initial_amount` at the `vesting_start_date`, and decreases with every vesting event till it yields an amount of zero at the `vesting_end_date`. Note that the vesting events do not make new HASH tokens available to the wallet, but lifts restrictions for the `vesting_event_amount` of HASH tokens that vest: vested HASH moves into the `available_spendable_amount` bucket and that newly vested hash will instantly be available for trading, transfer, and delegation.

Without delegated HASH, the `available_unvested_amount` equals the `vesting_initial_amount` at the `vesting_start_date`. With every vesting event, a `vesting_event_amount` of HASH will move from `available_unvested_amount` to `available_spendable_amount`. At the `vesting_end_date`, all HASH has been vested, the `available_unvested_amount` is zero, and all of the `vesting_initial_amount` has moved into the `available_spendable_amount`.

The unvested (or vesting) HASH and delegated HASH have the same policy restrictions: neither tokens can be used for trading or transfer. This observation allows us to deal with the `delegated_total_amount` of HASH as it those tokens are vesting.  

```
delegated_unvested_amount = delegated_total_amount - vesting_unvested_amount
```

`delegated_unvested_amount > 0` indicates that there is more delegated hash than the amount of hash that is subject to vesting restrictions: all vesting hash is covered by the delegated hash and none of the wallet's available hash is subject to vesting restrictions.
`delegated_unvested_amount < 0` indicates there is more unvested hash than delegated hash, and therefor part of the wallet's available hash is subject to vesting restrictions. 
`available_unvested_amount` is a dependent variable and its value is calculated from `delegated_unvested_amount`, i.e. the difference between  `delegated_total_amount` and `vesting_unvested_amount`


```
IF delegated_unvested_amount >= 0
THEN available_unvested_amount = 0

```
When there are more unvested tokens than delegated ones, then the difference have to be absorbed by the available_unvested_amount bucket to enforce the vesting restrictions on all vesting tokens:

```
IF delegated_unvested_amount < 0
THEN available_unvested_amount = vesting_unvested_amount - delegated_total_amount
```
The sequence of the calculations that yield the hash amounts in the different buckets is determined by the dependencies.
The different amounts are time dependent and should all be calculate for a certain time. The sequence should be the following:
0. fetch the `delegated_staked_amount`, `delegated_rewards_amount`, `delegated_redelegated_amount`, and the `delegated_unbonding_amount`.
1. calculate the `delegated_total_amount`.
2. fetch the `vesting_unvested_amount`.
3. calculate the `available_unvested_amount`
4. fetch the `available_total_amount` and the `available_committed_amount`
5. calculate the `available_spendable_amount`

After these calculations, the wallet_total_amount
