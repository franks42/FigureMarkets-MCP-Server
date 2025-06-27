# Information about Trading, Transferring, Staking, and Vesting of HASH Utility Tokens on Figure Markets and the Provenance Blockchain
## System Documentation for MCP Server Integration - UPDATED VERSION WITH VESTING CORRECTIONS

**Platform:** Figure Markets Exchange on Provenance Blockchain  
**Purpose:** Reference documentation for Claude MCP server wallet analysis  
**Version:** Current Production System + Vesting Calculation Fixes  
**Date:** June 27, 2025

---

## 🚨 **CRITICAL VESTING CALCULATION CORRECTIONS ADDED**

**MAJOR UPDATE**: This version includes critical fixes for vesting wallet analysis to prevent massive market influence calculation errors (10-100x overstatement). New "Controllable HASH" calculations ensure accurate whale status and market position assessments.

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
| wallet2     |          123 |        $3.21 |
```

**Always apply right-alignment markdown syntax (`|` followed by `-` and `:`) to numeric columns for proper decimal alignment.**

---

## 🚨 CRITICAL CALCULATIONS - MUST FOLLOW EXACT SEQUENCE

**⚠️ COMMON MISTAKE:** Do NOT use `vesting_total_unvested_amount` directly as `available_unvested_amount`
**⚠️ CRITICAL VESTING ERROR:** Do NOT treat all owned HASH as "controllable" in vesting wallets

### HASH WALLET CALCULATION SEQUENCE (Required for Accurate Analysis)

#### **Step 1: Retrieve Raw API Data**
```
// Direct blockchain data (do not calculate)
available_total_amount ← fetch_available_total_amount()
available_committed_amount ← fetch_available_committed_amount()

// New consolidated delegation API (replaces individual delegation calls)
delegation_data ← fetch_total_delegation_data()
delegated_staked_amount ← delegation_data.delegated_staked_amount
delegated_rewards_amount ← delegation_data.delegated_rewards_amount
delegated_unbonding_amount ← delegation_data.delegated_unbonding_amount
delegated_redelegated_amount ← delegation_data.delegated_redelegated_amount

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

#### **🚨 Step 6: Calculate CONTROLLABLE HASH (CRITICAL FOR MARKET ANALYSIS)**
```
IF isVesting = true THEN:
    controllable_hash = (available_total_amount + delegated_total_amount) - vesting_total_unvested_amount
    controllable_hash = max(0, controllable_hash)
ELSE:
    controllable_hash = available_total_amount + delegated_total_amount
```

**CRITICAL INSIGHT**: For vesting wallets, the CONTROLLABLE amount is what can actually be used/traded/influenced in the market. This is often DRAMATICALLY different from total holdings.

---

## ⚠️ CRITICAL TERMINOLOGY DISTINCTIONS

### API Data Values (Direct from Blockchain - Never Calculate):
- **`vesting_total_unvested_amount`** = Full amount still subject to vesting restrictions (from API)
- **`available_total_amount`** = All non-delegated HASH in wallet (from API)
- **`available_committed_amount`** = HASH committed for trading (from API)
- **`delegated_staked_amount`** = HASH actively staked with validators (from API) - **EARNS REWARDS**
- **`delegated_rewards_amount`** = Accumulated staking rewards (from API) - **DOES NOT EARN REWARDS**
- **`delegated_redelegated_amount`** = HASH in redelegation waiting period (from API) - **EARNS REWARDS**
- **`delegated_unbonding_amount`** = HASH in unbonding waiting period (from API) - **DOES NOT EARN REWARDS**

### Calculated Values (Must Be Computed Using Formulas Above):
- **`available_unvested_amount`** = Only the vesting deficit NOT covered by delegation (calculated)
- **`available_spendable_amount`** = Freely transferable HASH amount (calculated)
- **`delegated_total_amount`** = Sum of all delegation buckets (calculated)
- **`total_hash_in_wallet`** = Complete HASH holdings (calculated)
- **🚨 `controllable_hash`** = HASH that can actually influence markets/trading (calculated)

**🚨 NEVER use `vesting_total_unvested_amount` as `available_unvested_amount` directly!**
**🚨 NEVER use `total_hash_in_wallet` as `controllable_hash` for vesting wallets!**

---

## 🎯 DELEGATION MECHANICS & STRATEGIC INSIGHTS

### **Reward Earning Behavior (CRITICAL FOR ROI OPTIMIZATION)**

**ONLY these delegation states earn rewards:**
- **`delegated_staked_amount`** - Actively staked HASH earns rewards continuously
- **`delegated_redelegated_amount`** - Redelegated HASH earns rewards **immediately** at destination validator

**These delegation states DO NOT earn rewards:**
- **`delegated_rewards_amount`** - Accumulated rewards do not compound
- **`delegated_unbonding_amount`** - Unbonding HASH stops earning rewards immediately

### **Optimal Reward Strategy**
Since `delegated_rewards_amount` does not earn rewards, the optimal strategy is:
1. **Monitor rewards regularly** across all validators
2. **Claim rewards frequently** (immediate transfer to wallet via claim operation)
3. **Restake claimed rewards immediately** to convert them into earning `delegated_staked_amount`

**Key Insight**: Allowing rewards to accumulate with validators is a missed ROI opportunity since rewards don't compound.

### **Two Distinct 21-Day Waiting Periods**

#### **1. Redelegation Waiting Period**
- **Duration**: 21 days
- **Purpose**: Anti-validator-hopping protection
- **State**: `delegated_redelegated_amount`
- **Earnings**: ✅ **Earns rewards immediately** at destination validator
- **Restrictions**: 
  - ❌ **Cannot redelegate** during waiting period
  - ✅ **Can undelegate** (transitions to unbonding state)
- **Completion**: **Automatically transitions to `delegated_staked_amount` on day 22**

**⏰ Redelegation Completion (Day 22):**
- **Automatic State Change**: `delegated_redelegated_amount` → `delegated_staked_amount`
- ✅ **Rewards continue uninterrupted** throughout and after transition
- ✅ **All redelegation restrictions removed** (can redelegate again)
- ✅ **Full operational flexibility restored**
- ✅ **No user action required** - transition happens automatically

#### **2. Unbonding Waiting Period**  
- **Duration**: 21 days
- **Purpose**: Network security mechanism
- **State**: `delegated_unbonding_amount`
- **Earnings**: ❌ **No rewards** during unbonding
- **Restrictions**: 
  - ❌ **Cannot trade or transfer** until completion
  - ❌ **Cannot redelegate** back to validators
- **Completion**: Automatically moves to `available_spendable_amount`

### **Per-Validator vs Aggregated Understanding**

**For wallet analysis**, we use **aggregated totals** across all validators:
- `delegated_staked_amount` = sum of all `staked_i` across validators
- `delegated_redelegated_amount` = sum of all `redelegated_i` across validators  
- `delegated_rewards_amount` = sum of all `rewarded_i` across validators

**For understanding mechanics**, each validator maintains separate buckets:
- `staked_i` = HASH staked with validator_i
- `redelegated_i` = HASH redelegated TO validator_i  
- `rewarded_i` = rewards earned from validator_i
- `unbonding_i` = HASH unbonding from validator_i

### **State Transition Flow**
```
available → staked_i → redelegate_i_to_j → redelegated_j → staked_j (automatic after 21 days)
                ↓                                      ↓
            unbonding_i ← ← ← ← ← ← ← ← ← ← ← ← unbonding_j
                ↓                                      ↓  
            available ← ← ← ← ← ← ← ← ← ← ← ← ← ← available

rewards_i → available (claim operation - immediate)

REDELEGATION LIFECYCLE:
Day 1-21: redelegated_j (earning rewards, cannot redelegate)
Day 22+:  staked_j (earning rewards, full flexibility restored)
```

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

### MISTAKE #5: Ignoring Reward Optimization
❌ **WRONG:** Assuming all delegated HASH earns the same returns
✅ **CORRECT:** Only staked and redelegated HASH earn rewards; rewards should be claimed and restaked

**Consequence:** Suboptimal ROI from delegation strategy

### MISTAKE #6: Misunderstanding Redelegation Outcomes
❌ **WRONG:** Treating redelegated HASH as permanently restricted
✅ **CORRECT:** Redelegated HASH automatically becomes normal staked HASH after 21 days with full flexibility

**Consequence:** Incorrect long-term delegation planning and liquidity assessments

### MISTAKE #7: Treating All Owned HASH as Controllable in Vesting Wallets
❌ **WRONG:** `controllable_hash = available_total_amount + delegated_total_amount` (for vesting wallets)
✅ **CORRECT:** `controllable_hash = (available_total_amount + delegated_total_amount) - vesting_total_unvested_amount`

**Consequence:** MASSIVE overstatement of market influence and actionable positions. In extreme cases, this can show whale-level influence when actual control is minimal.

**Example Error Impact:** A wallet with 34M HASH total might appear to control 1.2% of circulating supply, when actual controllable amount is only 1.4M HASH (0.05% of circulating) due to vesting restrictions.

---

## WORKED CALCULATION EXAMPLE

**Example: Vesting Wallet with Strong Delegation Strategy**

**Raw API Data:**
- `vesting_total_unvested_amount`: 20,607,331 HASH (from fetch_vesting_total_unvested_amount)
- `available_total_amount`: 8,607,554 HASH (from fetch_available_total_amount)  
- `available_committed_amount`: 123 HASH (from fetch_available_committed_amount)
- **Delegation data** (from fetch_total_delegation_data):
  - `delegated_staked_amount`: 12,000,000 HASH
  - `delegated_rewards_amount`: 12,548 HASH
  - `delegated_unbonding_amount`: 0 HASH
  - `delegated_redelegated_amount`: 1,000 HASH

**Step-by-Step Correct Calculation:**

1. **Calculate delegated total:**
   `delegated_total_amount = 12,000,000 + 12,548 + 0 + 1,000 = 12,013,548 HASH`

2. **Apply vesting coverage logic:**
   `vesting_coverage_deficit = 20,607,331 - 12,013,548 = 8,593,783 HASH`
   `available_unvested_amount = max(0, 8,593,783) = 8,593,783 HASH`

3. **Calculate available spendable:**
   `available_spendable = 8,607,554 - 123 - 8,593,783 = 13,648 HASH`

4. **Calculate total HASH:**
   `total_hash_in_wallet = 8,607,554 + 12,013,548 = 20,621,102 HASH`

5. **🚨 Calculate controllable HASH (CRITICAL FOR MARKET ANALYSIS):**
   `controllable_hash = (8,607,554 + 12,013,548) - 20,607,331 = 13,771 HASH`

**✅ CORRECT RESULT:** 
- 13,648 HASH spendable (positive!)
- 8,593,783 HASH in coverage deficit  
- **13,771 HASH controllable** (only 0.067% of total holdings!)

**Strategic Insights**: 
- The 12,548 HASH in `delegated_rewards_amount` should be claimed and restaked to optimize ROI
- The 1,000 HASH in `delegated_redelegated_amount` will automatically become normal staked HASH after 21 days with full flexibility restored
- **CRITICAL**: Despite owning 20.6M HASH, only 13,771 HASH (0.067%) is actually controllable due to vesting restrictions
- **Market Analysis**: This wallet would have minimal market influence (not whale status) despite large total holdings

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
- **Redelegation Completions**: 21-day redelegation periods ending, **automatically moving HASH from `delegated_redelegated_amount` to `delegated_staked_amount` with full flexibility restored**
- **Reward Claims**: Immediate transfers from `delegated_rewards_amount` to `available_spendable_amount`

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
    ├── delegated_staked_amount (earning rewards) ⭐ EARNS REWARDS
    ├── delegated_rewards_amount (accumulated rewards) ❌ DOES NOT EARN REWARDS
    ├── delegated_redelegated_amount (transitioning between validators) ⭐ EARNS REWARDS  
    │   └── (automatically becomes delegated_staked_amount after 21 days)
    └── delegated_unbonding_amount (21-day waiting period) ❌ DOES NOT EARN REWARDS

🚨 controllable_hash = (available_total_amount + delegated_total_amount) - vesting_total_unvested_amount
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

Reward Earning Status:
- delegated_staked_amount: ⭐ EARNS REWARDS (should maintain)
- delegated_redelegated_amount: ⭐ EARNS REWARDS (should maintain, automatically becomes staked after 21 days)  
- delegated_rewards_amount: ❌ DOES NOT EARN REWARDS (should claim and restake)
- delegated_unbonding_amount: ❌ DOES NOT EARN REWARDS (waiting for completion)
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

**Strategic Liquidity Insight**: When `vesting_coverage_deficit <= 0`, the absolute value of this deficit represents **excess delegation** beyond vesting requirements:

```
excess_delegation_amount = abs(vesting_coverage_deficit) when vesting_coverage_deficit <= 0

This excess_delegation_amount could potentially be undelegated to become 
available_spendable_amount (freely tradable and transferable) without 
violating vesting restrictions.
```

**Important Note on Redelegated HASH**: When calculating vesting coverage, `delegated_redelegated_amount` provides the same coverage as staked HASH since both are locked and earning. After 21 days, redelegated HASH automatically becomes staked HASH with full operational flexibility restored.

**Example**: If `vesting_total_unvested_amount = 10,000 HASH` and `delegated_total_amount = 15,000 HASH` (including 1,000 redelegated):
- `vesting_coverage_deficit = 10,000 - 15,000 = -5,000 HASH`
- `available_unvested_amount = 0 HASH` (no coverage deficit)
- **Liquidity opportunity**: 5,000 HASH could be undelegated to increase `available_spendable_amount` while maintaining full vesting coverage
- **Future flexibility**: 1,000 redelegated HASH will automatically gain full flexibility after 21 days

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

## 🎯 CONTROLLABLE HASH CALCULATION (CRITICAL FOR MARKET ANALYSIS)

### **The Critical Distinction: Owned vs Controllable**

**MOST COMMON ANALYSIS ERROR**: Treating all owned HASH as "controllable" when analyzing market influence, whale status, or trading power.

**For Non-Vesting Wallets:**
```
controllable_hash = available_total_amount + delegated_total_amount
(All owned HASH is controllable)
```

**For Vesting Wallets (CRITICAL):**
```
controllable_hash = (available_total_amount + delegated_total_amount) - vesting_total_unvested_amount
controllable_hash = max(0, controllable_hash)
```

### **Why This Matters for Analysis**

**Market Influence Calculations:**
- ❌ **WRONG**: `market_share = total_owned_hash / network_circulating_supply`
- ✅ **CORRECT**: `market_share = controllable_hash / network_circulating_supply`

**Whale Status Determination:**
- ❌ **WRONG**: Base whale status on total holdings
- ✅ **CORRECT**: Base whale status on controllable holdings

**Trading Power Assessment:**
- ❌ **WRONG**: Assume all owned HASH can influence markets
- ✅ **CORRECT**: Only controllable HASH provides actual market influence

### **Real-World Impact Example**

**Scenario**: Vesting wallet with large total holdings
- `available_total_amount`: 616,369 HASH
- `delegated_total_amount`: 20,009,475 HASH  
- `total_owned`: 20,625,844 HASH
- `vesting_total_unvested_amount`: 20,536,693 HASH

**Wrong Calculation**: 20,625,844 HASH controllable (whale status)
**Correct Calculation**: (616,369 + 20,009,475) - 20,536,693 = 89,151 HASH controllable (standard holder)

**Analysis Impact**: 
- Wrong: 1.2% of circulating supply (whale)
- Correct: 0.05% of circulating supply (standard holder)
- **Error magnitude**: 24x overstatement of market influence

### **When to Use Each Calculation**

**Use Total Owned HASH for:**
- Portfolio valuation
- Long-term wealth assessment  
- Tax calculations
- Net worth analysis

**Use Controllable HASH for:**
- Market influence analysis
- Whale status determination
- Trading power assessment
- Liquidity planning
- Strategic position evaluation

### **Implementation Guidelines**

```javascript
function calculateControllableHash(walletData) {
  const totalOwned = walletData.available_total_amount + walletData.delegated_total_amount;
  
  if (walletData.isVesting) {
    const controllable = totalOwned - walletData.vesting_total_unvested_amount;
    return Math.max(0, controllable);
  } else {
    return totalOwned;
  }
}

function getMarketInfluence(controllableHash, networkCirculatingSupply) {
  return (controllableHash / networkCirculatingSupply) * 100;
}
```

**🚨 CRITICAL REMINDER**: Always use controllable HASH (not total owned) when analyzing market position, influence, or trading capabilities.

## MCP Server Integration

### Available API Functions

#### Account Information
- `fetch_current_fm_account_info(wallet_address)`: Account details and vesting status flag - **includes 'isVesting' boolean to indicate if wallet has vesting restrictions**
- `fetch_current_fm_account_balance_data(wallet_address)`: All token balances (HASH and other assets)
- `fetch_vesting_total_unvested_amount(wallet_address, date_time)`: HASH vesting schedule details for specific date (uses linear approximation of continuous vesting) - **Note: Only call if 'isVesting' = true, most wallets have no vesting**

#### HASH Amount Calculations
- `fetch_available_total_amount(wallet_address)`: Direct HASH account data (non-delegated amounts) - **returns actual blockchain data, not calculated**

#### Delegation Information (HASH-specific)
- `fetch_total_delegation_data(wallet_address)`: **NEW CONSOLIDATED API** - Returns complete delegation data including:
  - `delegated_staked_amount`: Currently staked HASH - ⭐ **EARNS REWARDS**
  - `delegated_rewards_amount`: Accumulated HASH rewards - ❌ **DOES NOT EARN REWARDS** - **should be claimed and restaked**
  - `delegated_redelegated_amount`: HASH transitioning between validators - ⭐ **EARNS REWARDS** - **automatically becomes staked after 21 days**
  - `delegated_unbonding_amount`: HASH in unbonding period - ❌ **DOES NOT EARN REWARDS**
  - `delegated_total_delegated_amount`: Total delegated amount (calculated)
  - `delegated_earning_amount`: Earning delegation amount (staked + redelegated)
  - `delegated_not_earning_amount`: Non-earning delegation amount (rewards + unbonding)

**Benefits of Consolidated API:**
- **Single API call** instead of four separate calls reduces network overhead
- **Consistent data state** - all delegation amounts from same blockchain block
- **Additional calculated fields** provided automatically
- **Better performance** for wallet analysis workflows

**DEPRECATED APIs (no longer use):**
- ~~`fetch_delegated_staked_amount(wallet_address)`~~ - **REPLACED by fetch_total_delegation_data()**
- ~~`fetch_delegated_rewards_amount(wallet_address)`~~ - **REPLACED by fetch_total_delegation_data()**
- ~~`fetch_delegated_redelegation_amount(wallet_address)`~~ - **REPLACED by fetch_total_delegation_data()**
- ~~`fetch_delegated_unbonding_amount(wallet_address)`~~ - **REPLACED by fetch_total_delegation_data()**

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
   - `fetch_total_delegation_data()` - **NEW CONSOLIDATED API** returns all delegation buckets:
     - `delegated_staked_amount` - ⭐ **EARNS REWARDS**
     - `delegated_rewards_amount` - ❌ **DOES NOT EARN REWARDS** - **recommend claiming**
     - `delegated_redelegated_amount` - ⭐ **EARNS REWARDS** - **automatically becomes staked after 21 days**
     - `delegated_unbonding_amount` - ❌ **DOES NOT EARN REWARDS**
6. **HASH Exchange Status**: `fetch_available_committed_amount()` (HASH only)

**Important Notes:**
- **Check 'isVesting' flag first**: Use `fetch_current_fm_account_info()` to check the 'isVesting' boolean before calling vesting functions
- **Use new consolidated API**: `fetch_total_delegation_data()` replaces four individual delegation APIs for better performance and data consistency
- Delegation functions return data only for HASH tokens
- Vesting functions apply only to HASH tokens and only when 'isVesting' = true
- Other assets (ETH, SOL, USDC, XRP, YLDS) do not have delegation or vesting data
- Use `fetch_current_fm_account_balance_data()` for balances of all asset types
- **Monitor `delegated_rewards_amount` for optimization opportunities** - recommend claiming and restaking
- **Understand `delegated_redelegated_amount` lifecycle** - automatically becomes fully flexible staked HASH after 21 days

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

**📋 SUMMARY: Always follow the CRITICAL CALCULATIONS sequence above to ensure accurate wallet analysis and avoid common mistakes that lead to negative available amounts. Remember that only staked and redelegated HASH earn rewards - accumulated rewards should be claimed and restaked for optimal ROI. Redelegated HASH automatically transitions to fully flexible staked HASH after 21 days with no user action required. MOST IMPORTANTLY: For vesting wallets, always calculate controllable HASH = (available + delegated) - vesting_unvested to determine actual market influence and actionable positions.**