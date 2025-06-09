# Information about Trading, Transferring, Staking, and Vesting of HASH Utility Tokens on Figure Markets and the Provenance Blockchain
## System Documentation for MCP Server Integration - CORRECTED VERSION

**Platform:** Figure Markets Exchange on Provenance Blockchain  
**Purpose:** Reference documentation for Claude MCP server wallet analysis  
**Version:** Current Production System  
**Date:** June 8, 2025

---

## Technical Requirements

**Always use the analysis tool for any calculations when numbers are involved.**
**Always convert date-time values to UTC before any comparison or duration calculations.**
**Always use the local time zone for displaying and presenting date-time values.**
**Always convert all tokens to their smallest denom units, like nhash, neth, and uusd, and keep them in memory like that.**
**All token calculations must be done after their amounts are converted to smallest denom units, like nhash, nbtc, uylds, uusdc.**
**Always display and present the amount of any token in the standard token denom, like HASH, ETH, BTC, YLDS or USDC.**

### Table Formatting Requirements

**All generated tables must follow these formatting standards:**
- **Decimal Alignment**: All numeric columns must be right-aligned to align numbers on decimal points
- **Currency Formatting**: Use proper currency notation ($XXX.XX format)
- **Denomination Headers**: Place token denominations (HASH, ETH, etc.) in column headers, not repeated in cells
- **Consistent Spacing**: Maintain consistent decimal places for similar value types
- **Professional Layout**: Use right-alignment (`:`) in markdown table syntax for numeric columns

**Example Table Header Formatting:**
```markdown
| Wallet Name | Amount (HASH) | Value (USD) |
|-------------|-------------:|------------:|
| wallet1     |    1,234,567 |   $32,100.43 |
| wallet2     |          123 |      $3.21 |
```

**Always apply right-alignment markdown syntax (`|` followed by `-` and `:`) to numeric columns for proper decimal alignment.**

---

## 🚨 CRITICAL CALCULATIONS - MUST FOLLOW EXACT SEQUENCE

**⚠️ COMMON MISTAKE:** Do NOT use `vesting_total_unvested_amount` directly as `available_unvested_amount`

### HASH WALLET CALCULATION SEQUENCE (Required for Accurate Analysis)

#### **Step 1: Retrieve Raw API Data**
```
// Direct blockchain data (do not calculate)
available_total_amount ← fetch_available_total_amount()
available_committed_amount ← fetch_available_committed_amount()
delegated_staked_amount ← fetch_delegated_staked_amount()
delegated_rewards_amount ← fetch_delegated_rewards_amount()
delegated_unbonding_amount ← fetch_delegated_unbonding_amount()
delegated_redelegated_amount ← fetch_delegated_redelegation_amount()

// Vesting data (only if isVesting = true)
vesting_total_unvested_amount ← fetch_vesting_total_unvested_amount()
```

#### **Step 2: Calculate Delegated Total**
```
delegated_total_amount = delegated_staked_amount + delegated_rewards_amount + 
                        delegated_unbonding_amount + delegated_redelegated_amount
```

#### **Step 3: Apply Vesting Coverage Logic (CRITICAL - Most Common Error Point)**
```
IF isVesting = true THEN:
    vesting_coverage_deficit = vesting_total_unvested_amount - delegated_total_amount
    available_unvested_amount = max(0, vesting_coverage_deficit)
ELSE:
    available_unvested_amount = 0
```

#### **Step 4: Calculate Available Spendable**
```
available_spendable_amount = available_total_amount - available_committed_amount - available_unvested_amount
```

#### **Step 5: Calculate Total HASH Holdings**
```
total_hash_in_wallet = available_total_amount + delegated_total_amount
```

---

## ⚠️ CRITICAL TERMINOLOGY DISTINCTIONS

### API Data Values (Direct from Blockchain - Never Calculate):
- **`vesting_total_unvested_amount`** = Full amount still subject to vesting restrictions (from API)
- **`available_total_amount`** = All non-delegated HASH in wallet (from API)
- **`available_committed_amount`** = HASH committed for trading (from API)
- **`delegated_staked_amount`** = HASH actively staked with validators (from API)
- **`delegated_rewards_amount`** = Accumulated staking rewards (from API)

### Calculated Values (Must Be Computed Using Formulas Above):
- **`available_unvested_amount`** = Only the vesting deficit NOT covered by delegation (calculated)
- **`available_spendable_amount`** = Freely transferable HASH amount (calculated)
- **`delegated_total_amount`** = Sum of all delegation buckets (calculated)
- **`total_hash_in_wallet`** = Complete HASH holdings (calculated)

**🚨 NEVER use `vesting_total_unvested_amount` as `available_unvested_amount` directly!**

---

## ⚠️ COMMON CALCULATION MISTAKES

### MISTAKE #1: Using Full Vesting Amount Instead of Coverage Deficit
❌ **WRONG:** `available_unvested_amount = vesting_total_unvested_amount`
✅ **CORRECT:** `available_unvested_amount = max(0, vesting_total_unvested_amount - delegated_total_amount)`

**Consequence:** Results in massive negative `available_spendable_amount` values

### MISTAKE #2: Skipping Vesting Coverage Logic
❌ **WRONG:** Assuming all unvested HASH is restricted
✅ **CORRECT:** Delegation "covers" vesting requirements, reducing restrictions

**Consequence:** Severely overstates restricted amounts, understates available liquidity

### MISTAKE #3: Incorrect Calculation Order
❌ **WRONG:** Calculate `available_spendable` before applying vesting coverage
✅ **CORRECT:** Always calculate vesting coverage deficit first, then `available_spendable`

**Consequence:** Negative spendable amounts indicate this error

### MISTAKE #4: Terminology Confusion
❌ **WRONG:** Using API field names directly in wallet analysis
✅ **CORRECT:** Distinguish between raw API data and calculated wallet amounts

**Consequence:** Using wrong values in calculations and user reports

---

## WORKED CALCULATION EXAMPLE

**Example: Vesting Wallet with Strong Delegation Strategy**

**Raw API Data:**
- `vesting_total_unvested_amount`: 20,607,331 HASH (from fetch_vesting_total_unvested_amount)
- `available_total_amount`: 8,607,554 HASH (from fetch_available_total_amount)  
- `available_committed_amount`: 123 HASH (from fetch_available_committed_amount)
- `delegated_staked_amount`: 12,000,000 HASH (from fetch_delegated_staked_amount)
- `delegated_rewards_amount`: 12,548 HASH (from fetch_delegated_rewards_amount)
- `delegated_unbonding_amount`: 0 HASH
- `delegated_redelegated_amount`: 0 HASH

**Step-by-Step Correct Calculation:**

1. **Calculate delegated total:**
   `delegated_total_amount = 12,000,000 + 12,548 + 0 + 0 = 12,012,548 HASH`

2. **Apply vesting coverage logic:**
   `vesting_coverage_deficit = 20,607,331 - 12,012,548 = 8,594,783 HASH`
   `available_unvested_amount = max(0, 8,594,783) = 8,594,783 HASH`

3. **Calculate available spendable:**
   `available_spendable = 8,607,554 - 123 - 8,594,783 = 12,648 HASH`

4. **Calculate total HASH:**
   `total_hash_in_wallet = 8,607,554 + 12,012,548 = 20,620,102 HASH`

**✅ CORRECT RESULT:** 12,648 HASH spendable (positive!), 8,594,783 HASH in coverage deficit

**❌ WRONG CALCULATION (Common Mistake):**
If you incorrectly used: `available_unvested_amount = 20,607,331 HASH`
Then: `available_spendable = 8,607,554 - 123 - 20,607,331 = -12,000,000 HASH` (negative!)

---

## System Overview

Figure Markets operates a sophisticated HASH token wallet management system on the Provenance Blockchain. This documentation describes the existing production system to enable Claude MCP server integration for wallet information retrieval and analysis.

## Dynamic Live System Behavior

**CRITICAL: Figure Markets and Provenance Blockchain are dynamic, live systems** where wallet amounts change continuously with every blockchain block (approximately every 4 seconds).

### Real-Time State Changes

Each block written to the Provenance Blockchain may contain transactions that affect wallet balances across all HASH buckets:

- **Trading Transactions**: Buy/sell orders affecting `available_committed_amount`
- **Transfer Operations**: Wallet-to-wallet movements changing `available_spendable_amount`
- **Staking Rewards**: Daily validator rewards increasing `delegated_rewards_amount`
- **Delegation Changes**: Staking/unstaking operations modifying `delegated_staked_amount`
- **Unbonding Completions**: 21-day periods ending, moving HASH from `delegated_unbonding_amount` to available buckets
- **Continuous Vesting**: Block-by-block vesting reducing `vesting_coverage_deficit` (if applicable)
- **Redelegation Transitions**: HASH moving between validators affecting `delegated_redelegated_amount`

### Data Consistency Considerations

**Important**: API function calls may return data from slightly different blockchain blocks, potentially causing minor inconsistencies in wallet analysis:

- **Normal Behavior**: Small discrepancies (typically <1% of total amounts) are expected due to the live nature of the system
- **Timing Differences**: Different API calls may reflect different block states, especially during periods of high network activity
- **Acceptable Variance**: Minor inconsistencies in bucket totals or calculated amounts are normal system behavior

### When to Request Fresh Data

**Guideline**: If observed discrepancies seem unusually large (>5% of expected amounts or significant bucket mismatches), request a complete re-evaluation of the wallet information:

- **Large Discrepancies**: May indicate major transactions occurred between API calls
- **Bucket Mismatches**: Significant differences between calculated totals and expected amounts
- **Fresh Block State**: Re-fetching data will capture a more consistent state from later blocks
- **System Activity**: High trading volumes or network events may cause larger temporary inconsistencies

**Best Practice**: For critical wallet analysis or when precise calculations are needed, consider fetching all related API data in quick succession to minimize block-state differences, or request fresh data if initial results appear inconsistent.

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
│   ├── available_spendable_amount (fully liquid - calculated using vesting coverage logic)
│   ├── available_committed_amount (exchange-only - from fetch_available_committed_amount())
│   └── available_unvested_amount (vesting coverage deficit only - calculated)
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

## Figure Markets AUM Calculation Limitation

**CRITICAL: Figure Markets' `accountAum` value is INCOMPLETE and excludes staked/delegated assets.**

The `accountAum.amount` returned by `fetch_current_fm_account_info()` only includes:
- Available HASH amounts
- Committed HASH amounts  
- Other liquid assets (USD, YLDS, ETH, etc.)

**It EXCLUDES:**
- Delegated/staked HASH (`delegated_staked_amount`)
- Reward HASH (`delegated_rewards_amount`)
- Unbonding HASH (`delegated_unbonding_amount`)
- Redelegating HASH (`delegated_redelegated_amount`)

### Correct Total Wallet Value Calculation

**Always calculate TRUE total wallet value using this formula:**

```
true_wallet_value = sum_of_all_asset_values

Where sum_of_all_asset_values includes:
- All available asset amounts × current prices
- All committed HASH × HASH price
- All delegated HASH buckets × HASH price
  (staked + rewards + unbonding + redelegating)
- All other assets × their respective prices
```

**Never rely on `accountAum` alone for total wallet value - it severely understates wallets with significant staking activity.**

**When presenting wallet summaries, always show:**
1. Figure Markets AUM (for reference)
2. Calculated True Total Value (the accurate number)
3. Note the discrepancy if significant (>10% difference)

### Implementation Guidelines

```
// Example calculation for true wallet value
const trueWalletValue = 
  (available_total_hash + committed_hash + delegated_staked_hash + 
   delegated_rewards_hash + delegated_unbonding_hash + delegated_redelegated_hash) * hash_price +
  other_asset_1_amount * other_asset_1_price +
  other_asset_2_amount * other_asset_2_price +
  // ... continue for all assets

// Compare with Figure Markets AUM
const discrepancy = trueWalletValue - figureMarketsAUM;
const discrepancyPercent = (discrepancy / trueWalletValue) * 100;

if (discrepancyPercent > 10) {
  // Note significant discrepancy in analysis
}
```

## Vesting System Implementation (HASH Only)

### HASH-Exclusive Vesting

Only HASH tokens can be subject to vesting restrictions on the Figure Markets platform. Other assets (ETH, SOL, USDC, XRP, YLDS, USD) are never subject to vesting schedules and are always fully liquid for trading and transfers.

**Important Note**: Most wallets and accounts are NOT subject to any vesting schedules. Vesting restrictions typically apply only to specific HASH token grants (such as employee compensation, investor allocations, or partnership agreements). The majority of Figure Markets users will have `available_unvested_amount = 0` and can ignore vesting-related functionality entirely.

### Vesting Coverage Logic (HASH Only)

Figure Markets implements a sophisticated vesting system where unvested HASH can be "covered" by delegated HASH amounts:

```
vesting_coverage_deficit = vesting_total_unvested_amount - delegated_total_amount

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

After retrieving data, calculate derived HASH amounts using the CRITICAL CALCULATIONS sequence above.

**⚠️ MUST follow the exact step-by-step sequence to avoid negative spendable amounts and incorrect analysis.**

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
- **If available_spendable_amount is negative: CALCULATION ERROR - check vesting coverage logic**

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

**📋 SUMMARY: Always follow the CRITICAL CALCULATIONS sequence above to ensure accurate wallet analysis and avoid common mistakes that lead to negative available amounts.**