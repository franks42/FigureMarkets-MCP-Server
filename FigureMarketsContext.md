# Information about Trading, Transferring, Staking, and Vesting of HASH Utility Tokens on Figure Markets and the Provenance Blockchain
## System Documentation for MCP Server Integration

**Platform:** Figure Markets Exchange on Provenance Blockchain  
**Purpose:** Reference documentation for Claude MCP server wallet analysis  
**Version:** Current Production System  
**Date:** June 8, 2025

---

## System Overview

Figure Markets operates a sophisticated HASH token wallet management system on the Provenance Blockchain. This documentation describes the existing production system to enable Claude MCP server integration for wallet information retrieval and analysis.

## Technical Requirements

**Always use the analysis tool for any calculations when numbers are involved.**
**Always convert date-time values to UTC before any comparison or duration calculations.**
**Always use the local time zone for displaying and presenting date-time values.**
**Always convert all tokens to their smallest denom units, like nhash, neth, and uusd, and keep them in memory like that.**
**All token calculations must be done after their amounts are converted to smallest denom units, like nhash, nbtc, uylds, uusdc.**
**Always display and present the amount of any token in the standard token denom, like HASH, ETH, BTC, YLDS or USDC.**

## Token Denomination System

### Provenance Blockchain Token Mapping
- **nhash**: nano-HASH (1 HASH = 1,000,000,000 nhash)
- **neth.figure.se**: nano-Ethereum on Figure Markets (1 ETH = 1,000,000,000 neth.figure.se)
- **nsol.figure.se**: nano-Solana on Figure Markets (1 SOL = 1,000,000,000 nsol.figure.se)
- **uusd.trading**: micro-USD for trading (1 USD = 1,000,000 uusd.trading)
- **uusdc.figure.se**: micro-USDC on Figure Markets (1 USDC = 1,000,000 uusdc.figure.se)
- **uxrp.figure.se**: micro-XRP on Figure Markets (1 XRP = 1,000,000 uxrp.figure.se)
- **uylds.fcc**: micro-YLDS token (1 YLDS = 1,000,000 uylds.fcc)

## Wallet Architecture

Figure Markets wallets organize HASH tokens into policy-based buckets that determine allowable operations:

### Core Structure

```
wallet_total_amount (total HASH in wallet)
├── available_total_amount (non-delegated HASH - from fetch_available_total_amount())
│   ├── available_spendable_amount (fully liquid - calculated)
│   ├── available_committed_amount (exchange-only - from fetch_available_committed_amount())
│   └── available_unvested_amount (vesting-restricted - calculated, zero for most wallets)
└── delegated_total_amount (validator-delegated HASH - calculated from delegation buckets)
    ├── delegated_staked_amount (earning rewards)
    ├── delegated_rewards_amount (accumulated rewards - also earning rewards)
    ├── delegated_redelegated_amount (transitioning between validators - also earning rewards)
    └── delegated_unbonding_amount (21-day waiting period)
```

### Fundamental Relationships

```
wallet_total_amount = available_total_amount + delegated_total_amount
delegated_total_amount = delegated_staked_amount + delegated_rewards_amount + delegated_redelegated_amount + delegated_unbonding_amount
available_total_amount = available_spendable_amount + available_committed_amount + available_unvested_amount

Data Sources:
- available_total_amount: Direct from fetch_available_total_amount() (not calculated)
- available_committed_amount: Direct from fetch_available_committed_amount() (not calculated)
- available_unvested_amount: Calculated from vesting coverage logic (if vesting applies)
- available_spendable_amount: Calculated as (available_total - available_committed - available_unvested)
- delegated_total_amount: Calculated by summing individual delegation bucket amounts
```

## Vesting System Implementation (HASH Only)

### HASH-Exclusive Vesting

Only HASH tokens can be subject to vesting restrictions on the Figure Markets platform. Other assets (ETH, SOL, USDC, XRP, YLDS, USD) are never subject to vesting schedules and are always fully liquid for trading and transfers.

**Important Note**: Most wallets and accounts are NOT subject to any vesting schedules. Vesting restrictions typically apply only to specific HASH token grants (such as employee compensation, investor allocations, or partnership agreements). The majority of Figure Markets users will have `available_unvested_amount = 0` and can ignore vesting-related functionality entirely.

### Vesting Coverage Logic (HASH Only)

Figure Markets implements a sophisticated vesting system where unvested HASH can be "covered" by delegated HASH amounts:

```
vesting_coverage_deficit = vesting_unvested_amount - delegated_total_amount

IF vesting_coverage_deficit <= 0
THEN available_unvested_amount = 0

IF vesting_coverage_deficit > 0
THEN available_unvested_amount = vesting_coverage_deficit
```

**Key Insight**: Delegated and unvested HASH have identical restrictions (cannot trade/transfer), so HASH delegation can satisfy vesting requirements.

### Vesting Coverage Deficit Analysis

**Key Insight**: The vesting coverage deficit directly corresponds to the available_unvested_amount shown in wallet balances:

```
vesting_coverage_deficit = available_unvested_amount
```

**Critical Investment Limitation**: Available unvested HASH tokens face significant ROI constraints:
- **Cannot be traded** for other assets until vested
- **Cannot be transferred** to other wallets until vested  
- **Cannot be committed** for exchange trading until vested
- **The only mechanism to generate ROI** from available_unvested_amount is through **delegation to Provenance Blockchain validators**

**Strategic Implication**: Since unvested HASH tokens are restricted from all liquidity operations, staking represents the exclusive opportunity to earn returns on this portion of the portfolio. Delegation of available_unvested_amount simultaneously:
1. Generates staking rewards (ROI)
2. Improves vesting coverage ratio
3. Reduces future available_unvested_amount through coverage logic

### HASH Vesting Schedule Parameters
- **vesting_initial_amount**: Total HASH subject to vesting
- **vesting_start_date**: When HASH vesting begins
- **vesting_end_date**: When all HASH becomes fully vested
- **Continuous vesting**: HASH vests with every blockchain block (approximately every 4 seconds)
- **Linear approximation**: Vesting progress calculated as a linear function over time
- **Vesting calculation**: `vested_amount = vesting_initial_amount × (time_elapsed / total_vesting_duration)`
- **Typical duration**: 4-year vesting schedule from start to end date

**Note**: Vesting schedules apply exclusively to HASH tokens. All other assets in the wallet remain fully liquid regardless of any HASH vesting restrictions.

## Operational Categories

### Available HASH Operations

#### `available_spendable_amount` (Calculated)
- **Calculation**: available_total - available_committed - available_unvested
- **Capabilities**: Transfer, delegate, commit for trading
- **Restrictions**: Cannot buy/sell directly (must commit first)
- **Use Cases**: General wallet operations, preparing for trading or staking

#### `available_committed_amount`  
- **Capabilities**: Buy/sell HASH for USD, uncommit back to spendable
- **Restrictions**: Cannot transfer or delegate
- **Use Cases**: Active trading on Figure Markets exchange

#### `available_unvested_amount`
- **Capabilities**: Delegate to validators only
- **Restrictions**: Cannot trade, transfer, or commit
- **Use Cases**: Satisfying vesting requirements through staking

### Delegated HASH Operations

#### `delegated_staked_amount`
- **Function**: HASH actively staked with Provenance Blockchain validators
- **Rewards**: Earns daily staking rewards (auto-compounding)
- **Restrictions**: 21-day unbonding period to withdraw

#### `delegated_rewards_amount`
- **Function**: Accumulated staking rewards (actively earning additional rewards)
- **Behavior**: Continues earning rewards while maintained as separate bucket for tax accounting
- **Growth**: Increases `delegated_total_amount`, improving vesting coverage
- **Tax Purpose**: Tracked separately to maintain detailed records of reward earning dates, amounts, and validator attribution for income reporting

#### `delegated_unbonding_amount`  
- **Function**: HASH in mandatory 21-day waiting period
- **Destination**: After 21 days, flows to available buckets based on vesting coverage
- **Complexity**: May split between spendable and unvested based on coverage calculation

## Multi-Asset Wallet System

### Supported Assets

Besides HASH tokens, Figure Markets wallets can hold various digital assets and tokens that can be traded on the exchange and transferred to/from other wallets:

**Supported Assets:**
- **ETH** (Ethereum) - `neth.figure.se`
- **SOL** (Solana) - `nsol.figure.se`  
- **USDC** (USD Coin) - `uusdc.figure.se`
- **XRP** (Ripple) - `uxrp.figure.se`
- **YLDS** (Yieldstreet token) - `uylds.fcc`
- **USD** (Trading USD) - `uusd.trading`

### Asset Commitment Model

#### HASH Token Commitment (Explicit)
HASH tokens require **explicit commitment and uncommitment** operations:

```
Manual Process for HASH:
available_spendable_amount --commit_for_trading()--> available_committed_amount
available_committed_amount --uncommit_from_exchange()--> available_spendable_amount
```

**Rationale**: HASH serves as the native utility token for Provenance Blockchain operations. Explicit commitment provides operational stability and prevents accidental trading of tokens needed for network fees, staking, and governance participation.

#### Non-HASH Asset Commitment (Automatic)

For all other tokens and assets, commitment is **automatic and transparent**:

**Automatic Commitment:**
- When wallet connects to Figure Markets exchange
- All eligible non-HASH assets automatically become available for trading
- No explicit user action required

**Automatic Uncommitment:**
- Triggered automatically before any transfer operation
- Ensures assets are in proper state for wallet-to-wallet transfers
- Seamless user experience with no manual intervention

```
Automatic Process for Non-HASH Assets:
wallet_connection --> auto_commit_for_trading()
transfer_initiation --> auto_uncommit_before_transfer() --> execute_transfer()
```

### Operational Differences by Asset Type

| Operation | HASH Tokens | Other Assets |
|-----------|-------------|--------------|
| **Trading Preparation** | Manual `commit_for_trading()` | Automatic on exchange connection |
| **Trading Execution** | Requires committed state | Direct trading from wallet |
| **Transfer Preparation** | Manual `uncommit_from_exchange()` | Automatic before transfer |
| **Transfer Execution** | From spendable amount | Direct from wallet balance |
| **Staking/Delegation** | Available (Provenance validators) | Not applicable |
| **Vesting Restrictions** | Supported with complex logic | Not applicable |

### Asset-Specific Capabilities

#### HASH Tokens (Native Provenance Blockchain Utility)
HASH tokens have unique capabilities as the native utility token of Provenance Blockchain:

**Exclusive HASH Capabilities:**
- **Delegation/Staking**: Only HASH can be delegated to Provenance Blockchain validators for network security and rewards
- **Vesting Restrictions**: Only HASH tokens can be subject to vesting schedules and restrictions
- **Governance Participation**: Only staked HASH provides voting power in blockchain governance
- **Network Fees**: Only HASH can pay transaction fees on Provenance Blockchain

#### Other Assets (Trading and Transfer Only)
Non-HASH assets (ETH, SOL, USDC, XRP, YLDS, USD) have limited functionality:

**Available Operations:**
- Buy/sell trading on Figure Markets exchange
- Transfer to/from other wallets
- Portfolio holdings and balance management

**Not Available:**
- ❌ Cannot be delegated to validators
- ❌ Cannot be subject to vesting restrictions  
- ❌ Cannot participate in blockchain governance
- ❌ Cannot pay Provenance Blockchain network fees

### Operational Differences by Asset Type

| Operation | HASH Tokens | Other Assets |
|-----------|-------------|--------------|
| **Trading Preparation** | Manual `commit_for_trading()` | Automatic on exchange connection |
| **Trading Execution** | Requires committed state | Direct trading from wallet |
| **Transfer Preparation** | Manual `uncommit_from_exchange()` | Automatic before transfer |
| **Transfer Execution** | From spendable amount | Direct from wallet balance |
| **Staking/Delegation** | ✓ Available (Provenance Blockchain validators) | ❌ Not available |
| **Vesting Restrictions** | ✓ Supported with complex logic | ❌ Not applicable |
| **Governance Voting** | ✓ Through staked HASH | ❌ Not available |
| **Network Fee Payment** | ✓ Required for all transactions | ❌ Cannot be used |

### Asset-Specific Bucket Structure

#### HASH Tokens (Complex Structure with Delegation & Vesting)
```
hash_wallet_balance
├── available_total_amount (from fetch_available_total_amount() - direct data)
│   ├── available_spendable_amount (calculated: total - committed - unvested)
│   ├── available_committed_amount (from fetch_available_committed_amount() - direct data)
│   └── available_unvested_amount (calculated from vesting coverage - zero for most wallets)
└── delegated_total_amount (calculated: sum of delegation buckets)
    ├── delegated_staked_amount (from fetch_delegated_staked_amount() - direct data)
    ├── delegated_rewards_amount (from fetch_delegated_rewards_amount() - direct data)
    ├── delegated_redelegated_amount (from fetch_delegated_redelegation_amount() - direct data)
    └── delegated_unbonding_amount (from fetch_delegated_unbonding_amount() - direct data)
```

#### Other Assets (Simplified Structure - Trading & Transfer Only)
```
asset_wallet_balance
├── available_amount (spendable/transferable)
└── committed_amount (auto-managed, trading-ready)

Note: No delegation buckets - staking not available
Note: No vesting buckets - vesting restrictions not applicable
```

### Exchange Trading Implications

**HASH Trading Flow:**
1. User manually commits HASH: `commit_for_trading()`
2. Execute trades using committed HASH
3. Optionally uncommit: `uncommit_from_exchange()`

**Other Asset Trading Flow:**
1. Connect wallet to exchange (auto-commit occurs)
2. Execute trades directly
3. Transfer triggers auto-uncommit if needed

### Provenance Blockchain Stability

The explicit commitment model for HASH tokens ensures Provenance Blockchain operational stability:

**Network Fee Requirements:**
- HASH needed for transaction fees on Provenance Blockchain
- Explicit commitment prevents accidental depletion of fee reserves
- Users maintain control over operational vs. trading allocations

**Governance Participation:**
- HASH required for voting on blockchain proposals
- Staked HASH provides voting power in network governance
- Commitment model protects governance participation capability

**Validator Operations:**
- HASH staking secures the Provenance Blockchain network
- Unbonding periods ensure network security
- Explicit management prevents accidental unstaking

**Economic Stability:**
- HASH serves as native currency for Provenance Blockchain ecosystem
- Controlled commitment reduces market volatility
- Protects users from inadvertent large-scale trading

## Provenance Blockchain Staking (HASH Only)

### Validator Delegation (HASH Exclusive)
Only HASH tokens can participate in Provenance Blockchain consensus through validator delegation:

- **Minimum Delegation**: 1 HASH (1,000,000,000 nhash)
- **Rewards**: Daily HASH distribution based on validator performance
- **Commission**: Variable by validator (typically 5-10%)
- **Unbonding**: Exactly 21 days, cannot be accelerated
- **Governance**: Staked HASH provides voting power in network decisions

### Redelegation Benefits (HASH Only)

#### Validator Switching Without Penalty
HASH holders can switch validators without losing rewards or facing unbonding periods:

- **No Loss**: Redelegation maintains full token value
- **No Penalty**: No fees or waiting periods for switching
- **Continuous Rewards**: Starts earning with new validator immediately upon completion
- **Flexibility**: Optimize validator selection based on performance and commission rates

#### Stopping Unbonding Process
Users can cancel unbonding at any time by redelegating to a validator:

- **Rescue Unbonding Tokens**: Redirect unbonding HASH back to active staking
- **Resume Rewards**: Immediately restart earning staking rewards
- **Strategic Timing**: Respond to market conditions or validator changes
- **No Time Lost**: Full 21-day unbonding period avoided

#### Use Cases for Redelegation
- **Validator Performance**: Switch from underperforming to high-performing validators
- **Commission Optimization**: Move to validators with lower commission rates
- **Network Diversification**: Spread delegation across multiple validators for risk management
- **Emergency Response**: React quickly to validator issues or slashing events
- **Unbonding Recovery**: Change decision during unbonding period

**Important**: Redelegation maintains the same vesting coverage benefits as regular staking, ensuring delegated amounts continue to satisfy vesting requirements. During the redelegation transition period, tokens continue earning rewards and remain part of the active delegation pool.

### Tax Accounting Structure

**All Delegation Buckets Earn Rewards**: The Provenance Blockchain system separates delegated HASH into multiple buckets (`delegated_staked_amount`, `delegated_rewards_amount`, `delegated_redelegated_amount`) not for functional reasons, but for tax compliance and accounting purposes. All buckets actively earn staking rewards, but are tracked separately to maintain detailed records required for tax reporting:

- **Reward Earning Dates**: When specific rewards were earned for income recognition
- **Duration Tracking**: How long tokens have been generating taxable income  
- **Amount Attribution**: Principal vs. income distinction for tax basis calculations
- **Validator Attribution**: Which validator generated specific rewards for detailed reporting
- **Income Recognition**: Staking rewards may be taxable as ordinary income in many jurisdictions

This granular tracking enables users to have complete staking income records for accurate tax compliance while ensuring all delegated HASH continues earning rewards regardless of bucket categorization.

- HASH rewards automatically restake to maximize returns
- Growing HASH delegation improves vesting coverage over time
- No manual claiming required for HASH rewards
- Compound growth increases validator security participation

**Important**: Other assets (ETH, SOL, USDC, XRP, YLDS) cannot be staked or delegated on Provenance Blockchain. They exist solely for trading and portfolio holdings on Figure Markets.

## System State Transitions

### Manual Operations (User-Initiated)

#### HASH Token Operations
```
buy_hash_with_usd(): USD → available_committed_amount
sell_hash_for_usd(): available_committed_amount → USD
transfer_hash_to_wallet(): available_spendable_amount → external_wallet
receive_hash_from_wallet(): external_wallet → available_spendable_amount
commit_for_trading(): available_spendable_amount → available_committed_amount
uncommit_from_exchange(): available_committed_amount → available_spendable_amount
stake_with_validator(): available_spendable/unvested → delegated_staked_amount
unstake_from_validator(): delegated_staked/rewards/redelegated → delegated_unbonding_amount
redelegate_to_validator(): delegated_staked_amount → delegated_redelegated_amount
redelegate_from_unbonding(): delegated_unbonding_amount → delegated_redelegated_amount
```

#### Other Asset Operations (ETH, SOL, USDC, XRP, YLDS, USD)
```
buy_asset_with_usd(): USD → asset_available_amount (auto-committed for trading)
sell_asset_for_usd(): asset_available_amount → USD (auto-uncommitted if needed)
transfer_asset_to_wallet(): asset_available_amount → external_wallet (auto-uncommit)
receive_asset_from_wallet(): external_wallet → asset_available_amount
```

**Note**: Other assets do not support delegation, vesting, or explicit commitment operations.

### Automatic Operations (System-Triggered)

#### HASH-Specific Automatic Operations
```
accumulate_staking_rewards(): validator_rewards → delegated_rewards_amount (daily)
compound_rewards_to_staking(): delegated_rewards → delegated_staked_amount (daily)
complete_redelegation(): delegated_redelegated → delegated_staked_amount (epoch completion)
complete_unbonding_period(): delegated_unbonding → available buckets (after 21 days)
vest_scheduled_tokens(): available_unvested → available_spendable (continuous, ~every 4 sec)
apply_governance_slashing(): delegated amounts → destroyed (penalty events)
```

#### Multi-Asset Automatic Operations
```
auto_commit_on_connection(): asset_available → asset_committed (all non-HASH assets)
auto_uncommit_before_transfer(): asset_committed → asset_available (before transfers)
```

**Important**: Delegation, vesting, and staking-related operations apply exclusively to HASH tokens. Other assets only support basic trading and transfer operations.

## MCP Server Integration

### Available API Functions

#### Account Information
- `fetch_current_fm_account_info(wallet_address)`: Account details and vesting status flag - **includes 'isVesting' boolean to indicate if wallet has vesting restrictions**
- `fetch_current_fm_account_balance_data(wallet_address)`: All token balances (HASH and other assets)
- `fetch_vesting_total_unvested_amount(wallet_address, date_time)`: HASH vesting schedule details for specific date (uses linear approximation of continuous vesting) - **Note: Only call if 'isVesting' = true, most wallets have no vesting**

#### HASH Amount Calculations
- `fetch_available_total_amount(wallet_address)`: Direct HASH account data (non-delegated amounts) - **returns actual blockchain data, not calculated**

#### Delegation Information (HASH-specific)
- `fetch_delegated_staked_amount(wallet_address)`: Currently staked HASH
- `fetch_delegated_rewards_amount(wallet_address)`: Accumulated HASH rewards
- `fetch_delegated_redelegation_amount(wallet_address)`: HASH transitioning between validators
- `fetch_delegated_unbonding_amount(wallet_address)`: HASH in unbonding period

#### Exchange Information
- `fetch_available_committed_amount(wallet_address)`: HASH committed for trading - **returns actual blockchain data, not calculated**
- `fetch_current_fm_data()`: Market data and trading pairs for all assets
- `fetch_last_crypto_token_price(token_pair, count)`: Recent prices for any trading pair

#### Asset Information
- `fetch_figure_markets_assets_info()`: All supported assets (HASH, ETH, SOL, USDC, XRP, YLDS) and denominations

### Data Retrieval Sequence

For comprehensive wallet analysis, follow this sequence:

1. **Account Overview**: `fetch_current_fm_account_info()` - **Check 'isVesting' flag to determine if vesting calculations are needed**
2. **All Asset Balances**: `fetch_current_fm_account_balance_data()` (includes HASH and other assets)
3. **HASH Available Amounts**: `fetch_available_total_amount()` (HASH only - returns actual account data)
4. **HASH Vesting Information**: `fetch_vesting_total_unvested_amount()` (HASH only - **only if 'isVesting' = true**)
5. **HASH Delegation Status** (HASH only):
   - `fetch_delegated_staked_amount()`
   - `fetch_delegated_rewards_amount()`
   - `fetch_delegated_redelegation_amount()`
   - `fetch_delegated_unbonding_amount()`
6. **HASH Exchange Status**: `fetch_available_committed_amount()` (HASH only)

**Important Notes:**
- **Check 'isVesting' flag first**: Use `fetch_current_fm_account_info()` to check the 'isVesting' boolean before calling vesting functions
- Delegation functions return data only for HASH tokens
- Vesting functions apply only to HASH tokens and only when 'isVesting' = true
- Other assets (ETH, SOL, USDC, XRP, YLDS) do not have delegation or vesting data
- Use `fetch_current_fm_account_balance_data()` for balances of all asset types

### Calculation Process

After retrieving data, calculate derived HASH amounts (other assets use simple available/committed structure):

#### HASH Token Calculations
```
Step 1: Calculate HASH delegated_total_amount
delegated_total = delegated_staked + delegated_rewards + delegated_redelegated + delegated_unbonding

Step 2: Determine HASH vesting coverage (only if 'isVesting' = true)
IF isVesting = true THEN:
    vesting_coverage_deficit = vesting_unvested_amount - delegated_total
    available_unvested_amount = max(0, vesting_coverage_deficit)
ELSE:
    available_unvested_amount = 0

Step 3: Retrieve direct account data and calculate spendable amount
available_total = fetch_available_total_amount() (direct blockchain data)
available_committed = fetch_available_committed_amount() (direct blockchain data)
available_spendable = available_total - available_committed - available_unvested (calculated)
```

#### Other Asset Calculations (ETH, SOL, USDC, XRP, YLDS, USD)
```
Simple Structure:
asset_wallet_balance = available_amount + committed_amount (auto-managed)

Note: No delegation or vesting calculations needed for non-HASH assets
```

## Wallet Analysis Guidelines

### Health Indicators

#### HASH-Specific Metrics
- **Liquidity ratio**: available_spendable / wallet_total_hash
- **Staking ratio**: delegated_staked / wallet_total_hash  
- **Vesting coverage**: delegated_total / vesting_unvested (if applicable)
- **Trading commitment**: available_committed / available_total_hash

#### Multi-Asset Portfolio Metrics
- **Asset diversification**: Number of different assets held
- **Portfolio balance**: Distribution across HASH vs. other assets
- **Trading activity**: Committed amounts across all tradeable assets
- **Liquidity distribution**: Available vs. committed across all assets

### Risk Factors

#### HASH-Specific Risks
- **High unbonding amounts**: HASH tokens locked for 21 days
- **Low vesting coverage**: Insufficient delegation for unvested amounts
- **Validator concentration**: All HASH delegation with single validator
- **Slashing exposure**: HASH delegation with underperforming validators

#### Multi-Asset Risks
- **Concentration risk**: Over-allocation to single asset type
- **Auto-commitment exposure**: Large amounts auto-committed for trading
- **Cross-asset correlation**: Portfolio sensitivity to market movements
- **Operational token shortage**: Insufficient HASH for network fees

### Optimization Opportunities

#### HASH Optimization
- **Uncommitted spendable HASH**: Could be earning staking rewards
- **Dust amounts**: Small HASH balances that could be consolidated

#### Multi-Asset Optimization
- **Idle asset balances**: Non-HASH assets not generating yield
- **Trading preparation**: Assets ready for trading vs. transfer needs
- **Fee reserve management**: Adequate HASH for operational requirements
- **Asset rebalancing**: Portfolio allocation adjustments

## Common Wallet Patterns

**Note**: The majority of Figure Markets wallets are NOT subject to vesting restrictions and will have `available_unvested_amount = 0`. Vesting patterns apply only to specific HASH grants and allocations.

### New User Pattern (Most Common)
- **HASH**: High `available_spendable_amount`, zero delegation, zero vesting
- **Other Assets**: Small balances, auto-committed for trading
- **Characteristics**: No vesting restrictions, minimal staking activity
- **Recommendation**: Consider HASH staking for rewards, explore asset diversification

### Active Trader Pattern  
- **HASH**: Significant `available_committed_amount`, low delegation, typically zero vesting
- **Other Assets**: Multiple asset types, frequent trading activity
- **Characteristics**: Manual HASH commitment/uncommitment, auto-trading other assets
- **Recommendation**: Balance HASH trading with long-term staking, maintain fee reserves

### Long-term Holder Pattern
- **HASH**: High `delegated_staked_amount`, growing rewards, typically zero vesting
- **Other Assets**: Buy-and-hold positions, minimal trading
- **Characteristics**: Auto-compounding HASH growth, improved vesting coverage
- **Benefit**: HASH staking rewards, asset appreciation, reduced trading fees

### Vesting User Pattern (Uncommon - Specific Grants Only)
- **HASH**: `available_unvested_amount` > 0, strategic delegation
- **Other Assets**: Normal trading and holding patterns
- **Characteristics**: Continuous HASH vesting (with each block), optimized delegation strategy
- **Strategy**: Maximize HASH delegation to minimize restrictions, diversify with other assets

### Multi-Asset Diversified Pattern
- **HASH**: Balanced between staking and trading, typically zero vesting
- **Other Assets**: Strategic allocation across ETH, SOL, USDC, XRP, YLDS
- **Characteristics**: Portfolio management approach, risk distribution
- **Optimization**: Maintain HASH for network participation, optimize other asset yields

### Institutional Pattern
- **HASH**: Large staked amounts, governance participation, may include vesting grants
- **Other Assets**: Significant balances across multiple assets
- **Characteristics**: Network validator operations, large-scale trading
- **Considerations**: Validator selection, slashing risk management, operational reserves

## Error Handling

### Common Data Issues
- **Missing vesting data**: Normal for most wallets - only specific HASH grants have vesting schedules
- **Zero balances**: New or emptied wallets
- **Network delays**: Blockchain data synchronization lag
- **Invalid addresses**: Malformed wallet addresses

### Validation Rules
- All amounts must be non-negative
- Bucket totals must equal wallet total
- Vesting amounts must not exceed initial grants
- Delegation amounts must match blockchain state

## Security Considerations

### Read-Only Operations
All MCP server functions are read-only and cannot modify wallet state or execute transactions.

### Data Privacy
- Wallet information is public on Provenance Blockchain
- No private keys or sensitive data accessed
- Analysis results should respect user privacy expectations

### Rate Limiting
- Implement reasonable request throttling
- Cache frequently accessed data appropriately
- Monitor API usage for efficiency

---

This documentation enables Claude MCP server integration to provide comprehensive HASH wallet analysis, helping users understand their token distribution, optimize their holdings, and make informed decisions about staking, trading, and vesting strategies on the Figure Markets platform.