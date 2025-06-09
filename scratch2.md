# HASH Token Wallet Management Specification

## Technical Requirements

**Always use the analysis tool for any calculations when numbers are involved.**
**Always convert date-time values to UTC before any comparison or duration calculations.**
**Always use the local time zone for displaying and presenting date-time values.**
**Always convert all tokens to their smallest denom units, like nhash, neth, and uusd, and keep them in memory like that.**
**All token calculations must be done after their amounts are converted to smallest denom units, like nhash, nbtc, uylds, uusdc.**
**Always display and present the amount of any token in the standard token denom, like HASH, ETH, BTC, YLDS or USDC.**

## Overview

A wallet contains a `wallet_total_amount` of HASH tokens organized into policy-based buckets that determine allowable operations. HASH can be traded on exchanges, transferred between wallets, or delegated to validators for staking rewards.

## Core Operations

### Adding HASH to Wallet
- Buying HASH on an exchange (USD ⇒ HASH)
- Receiving HASH from another wallet
- Earning delegation rewards from validator staking

### Removing HASH from Wallet
- Selling HASH on an exchange (HASH ⇒ USD)
- Sending HASH to another wallet
- Slashing by blockchain governance (validator misbehavior)

## Token Bucket Structure

### Primary Categories

#### 1. Delegated HASH (`delegated_total_amount`)
HASH delegated to validators for staking, subject to delegation policy restrictions:

- **`delegated_staked_amount`** - Currently staked with validators
- **`delegated_rewards_amount`** - Earned staking rewards
- **`delegated_unbonding_amount`** - HASH in 21-day unbonding period

**Policy Restrictions:**
- Cannot be traded or transferred
- Can be undelegated (with 21-day unbonding period)
- Rewards can be claimed to available buckets

#### 2. Available HASH (`available_total_amount`)
HASH not subject to delegation policies, further subdivided by usage restrictions:

- **`available_spendable_amount`** - Fully liquid HASH
- **`available_committed_amount`** - Committed to exchange trading
- **`available_unvested_amount`** - Subject to vesting schedule restrictions

## Bucket Calculations

### Core Relationships

```
delegated_total_amount = delegated_staked_amount + delegated_rewards_amount + delegated_unbonding_amount

available_total_amount = wallet_total_amount - delegated_total_amount

available_spendable_amount = available_total_amount - available_committed_amount - available_unvested_amount
```

### Vesting Integration Logic

For wallets subject to vesting schedules, we calculate the **vesting coverage deficit** to determine policy application:

```
vesting_coverage_deficit = vesting_unvested_amount - delegated_total_amount
```

This determines how vesting restrictions apply to available HASH:

```
IF vesting_coverage_deficit <= 0
THEN available_unvested_amount = 0
ELSE available_unvested_amount = vesting_coverage_deficit
```

**Rationale:** Delegated and unvested HASH have identical policy restrictions (no trading/transfers). When delegation covers all unvested amounts, no additional restrictions apply to available HASH.

## Policy Matrix

| Bucket | Trade | Transfer | Delegate | Commit | Uncommit | Unbond |
|--------|-------|----------|----------|--------|----------|--------|
| `available_spendable_amount` | ✗ | ✓ | ✓ | ✓ | N/A | N/A |
| `available_committed_amount` | ✓ | ✗ | ✗ | ✗ | ✓ | N/A |
| `available_unvested_amount` | ✗ | ✗ | ✓ | ✗ | N/A | N/A |
| `delegated_staked_amount` | ✗ | ✗ | ✗ | N/A | N/A | ✓* |
| `delegated_rewards_amount` | ✗ | ✗ | ✗ | N/A | N/A | ✓* |
| `delegated_unbonding_amount` | ✗ | ✗ | ✗ | N/A | N/A | ✗ |

*Requires 21-day unbonding period

## Vesting Schedule Management

### Vesting Parameters
- **`vesting_initial_amount`** - Total HASH subject to vesting
- **`vesting_start_date`** - When vesting schedule begins
- **`vesting_end_date`** - When all HASH becomes fully vested
- **`vesting_events`** - List of scheduled vesting releases

### Vesting Event Processing
When a vesting event occurs:
1. `vesting_event_amount` moves from unvested to vested status
2. If `available_unvested_amount > 0`, reduce it by `vesting_event_amount`
3. Increase `available_spendable_amount` by the vested amount
4. Recalculate all dependent buckets

## Calculation Sequence

Due to dependencies between buckets, calculations must follow this precise order:

### Step 0: Fetch Delegation Data
```
delegated_staked_amount = fetch_delegated_staked_amount(wallet_address)
delegated_rewards_amount = fetch_delegated_rewards_amount(wallet_address)
delegated_unbonding_amount = fetch_delegated_unbonding_amount(wallet_address)
```

### Step 1: Calculate Delegated Total
```
delegated_total_amount = delegated_staked_amount + delegated_rewards_amount + delegated_unbonding_amount
```

### Step 2: Fetch Vesting Data
```
vesting_unvested_amount = fetch_current_vesting_unvested_amount(wallet_address)
```

### Step 3: Calculate Vesting Coverage
```
vesting_coverage_deficit = vesting_unvested_amount - delegated_total_amount

IF vesting_coverage_deficit <= 0
THEN available_unvested_amount = 0
ELSE available_unvested_amount = vesting_coverage_deficit
```

### Step 4: Fetch Available Data
```
available_total_amount = fetch_available_total_amount(wallet_address)
available_committed_amount = fetch_available_committed_amount(wallet_address)
```

### Step 5: Calculate Available Spendable
```
available_spendable_amount = available_total_amount - available_committed_amount - available_unvested_amount
```

### Step 6: Verify Wallet Total
```
calculated_wallet_total = available_total_amount + delegated_total_amount
```

## Validation Rules

### Invariants
All calculations must satisfy these invariants:

```
INVARIANT_1: wallet_total_amount >= 0
INVARIANT_2: available_total_amount + delegated_total_amount = wallet_total_amount
INVARIANT_3: available_spendable_amount >= 0
INVARIANT_4: available_committed_amount >= 0
INVARIANT_5: available_unvested_amount >= 0
INVARIANT_6: delegated_staked_amount >= 0
INVARIANT_7: delegated_rewards_amount >= 0
INVARIANT_8: delegated_unbonding_amount >= 0
INVARIANT_8: vesting_unvested_amount >= 0
```

### Data Consistency Checks
```
CHECK_1: available_spendable_amount + available_committed_amount + available_unvested_amount = available_total_amount
CHECK_2: IF wallet has vesting schedule THEN vesting_unvested_amount <= vesting_initial_amount
CHECK_3: calculated_wallet_total matches fetched wallet_total_amount (within dust tolerance)
```

## Error Handling

### API Failure Recovery
1. **Fetch Failures:** Retry with exponential backoff, maximum 3 attempts
2. **Partial Data:** If any fetch fails, abort calculation and return cached values
3. **Network Timeout:** Use cached values with staleness warning

### Calculation Errors
1. **Negative Amounts:** If any bucket calculates negative, throw validation error
2. **Precision Loss:** Round to nearest smallest denomination unit
3. **Invariant Violations:** Log error, return cached values, trigger reconciliation

### Reconciliation Process
When inconsistencies are detected:
1. Fetch fresh data from all sources
2. Recalculate from scratch
3. If inconsistencies persist, escalate to manual review
4. Update cached values only after successful validation

## Timing and Refresh Triggers

### Automatic Refresh
Recalculate bucket amounts when:
- New transaction detected
- Vesting event occurs (daily at UTC midnight on vesting dates)
- Delegation/undelegation operations
- Reward claiming
- Exchange operations (commit/uncommit)

### Periodic Reconciliation
- Full recalculation every 1 hour
- Deep validation against blockchain state every 24 hours
- Cached values expire after 5 minutes of staleness

## Edge Cases

### Dust Amounts
- Minimum transferable amount: 1000 nhash (0.001 HASH)
- Amounts below dust threshold remain in current bucket
- Dust consolidation during bucket transfers

### Concurrent Operations
- Use atomic operations for bucket updates
- Lock wallet state during multi-step calculations
- Queue conflicting operations

### Vesting Schedule Changes
- New schedules only apply to future allocations
- Existing unvested amounts maintain original schedule
- Schedule modifications require governance approval

## Implementation Notes

### Precision Handling
- All internal calculations in smallest denomination (nhash)
- Conversion factor: 1 HASH = 1,000,000,000 nhash
- Display rounding to 6 decimal places for user interfaces

### Date/Time Handling
- Store all timestamps in UTC
- Vesting events trigger at UTC midnight
- Display times in user's local timezone
- Account for leap seconds in duration calculations

### State Management
- Maintain calculation audit trail for debugging
- Cache intermediate results for performance
- Version state changes for rollback capability

## Security Considerations

### Access Control
- Read operations: No restrictions
- Bucket modifications: Require transaction authorization
- Vesting parameter changes: Require governance approval

### Validation
- Cryptographic verification of delegated amounts against blockchain
- Multi-source validation for critical calculations
- Rate limiting for calculation requests

### Audit Requirements
- Log all bucket state changes
- Track calculation performance metrics
- Alert on invariant violations
- Maintain 90-day calculation history