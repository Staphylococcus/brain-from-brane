# Agent-Based Model of Bio-Informational Complex (BIC) Dynamics

## 1. Purpose

This model simulates the formation, spread, and competition of Bio-Informational Complexes (BICs) within a population of agents. It aims to explore the lifecycle of BICs, as described in the project's theoretical documents (specifically `docs/05-competitive-dynamics/5e-bio-informational-complex.md`), including phases like Exposure, Adoption, Lock-In, Propagation, and potentially Drift/Breakdown.

The model allows for experimentation with different parameters for both agents and information systems to observe how these affect BIC prevalence and agent states.

## 2. Model Components

### 2.1. Agents

-   **ID:** Unique identifier.
-   **State Variables:**
    -   `current_bic_id`: The ID of the BIC the agent currently adheres to (e.g., None, IS1, IS2).
    -   `bic_strength`: A float (0.0 to 1.0) representing the strength of adherence to the current BIC.
    -   `susceptibility`: A float (0.0 to 1.0) representing the agent's general openness to adopting new BICs.
    -   `is_locked_in`: A boolean indicating if the agent is in the "Lock-In" phase with their current BIC.
-   **Interactions:** Agents can be exposed to BICs through direct interaction with "pure" information system sources or through propagation attempts by other agents.

### 2.2. Information Systems (Proto-BICs)

-   **ID:** Unique identifier (e.g., IS1, IS2).
-   **Properties:**
    -   `base_infectivity`: Base probability of adoption upon exposure.
    -   `resonance_factor`: Multiplier affecting infectivity based on agent susceptibility.
    -   `lock_in_threshold`: `bic_strength` required for an agent to become "locked-in."
    -   `propagation_bonus`: Factor increasing an agent's ability to propagate the BIC once locked-in.
    -   `color`: For visualization purposes.

## 3. Simulation Loop

The simulation proceeds in discrete time steps (generations). In each generation, the following phases occur:

1.  **Direct Exposure:** Agents (especially those not locked-in) have a chance to be exposed directly to "pure" InfoSys sources and potentially adopt them.
2.  **Agent Interaction & Propagation:** Agents with an active BIC attempt to propagate it to other randomly chosen agents. The success of propagation depends on the propagator's BIC strength (and lock-in status) and the target's susceptibility and current BIC state.
3.  **BIC Strength Update & Lock-In:** Agents update their `bic_strength` for their current BIC. If strength crosses the `lock_in_threshold`, they become `is_locked_in`. Locked-in agents may see further strength increases.
4.  **BIC Decay:** `bic_strength` can slowly decay if not reinforced, potentially leading to an agent abandoning a BIC if strength drops to zero. Locked-in agents are more resistant to decay.

## 4. Parameters

### 4.1. Simulation Parameters
-   `NUM_AGENTS`: Total number of agents in the simulation.
-   `NUM_GENERATIONS`: Number of time steps the simulation runs for.
-   `INTERACTIONS_PER_AGENT_PER_GENERATION`: Number of other agents an agent attempts to propagate its BIC to in a single generation.
-   `DIRECT_EXPOSURE_PROBABILITY`: Probability per generation that an agent (not locked-in) is exposed to a pure InfoSys source.

### 4.2. Agent Parameters (Initial)
-   `susceptibility`: Typically randomized within a range for each agent at creation.

### 4.3. InfoSys Parameters (Example)
-   `IS1`: `base_infectivity=0.1`, `resonance_factor=1.0`, `lock_in_threshold=0.6`, `propagation_bonus=0.2`
-   `IS2`: `base_infectivity=0.08`, `resonance_factor=1.2`, `lock_in_threshold=0.7`, `propagation_bonus=0.3`
-   `IS3`: `base_infectivity=0.12`, `resonance_factor=0.9`, `lock_in_threshold=0.5`, `propagation_bonus=0.15`

## 5. Outputs & Data Collection

-   The simulation prints summary statistics to the console every N generations (e.g., every 10 generations) and at the end.
-   Statistics include:
    -   Number of agents unaligned.
    -   Number of agents adhering to each BIC.
    -   Average `bic_strength` for adherents of each BIC.
    -   Number of agents "locked-in" to each BIC.
-   A `history` list is collected containing these stats for each generation, intended for later plotting and analysis (e.g., using Matplotlib).

## 6. Experiments & Observations (To Be Filled)

**Run 1: Initial Default Parameters (2025-06-03)**

- **Parameters Used:**
  - `NUM_AGENTS = 50`
  - `NUM_GENERATIONS = 200`
  - `INTERACTIONS_PER_AGENT_PER_GENERATION = 5`
  - `DIRECT_EXPOSURE_PROBABILITY = 0.05`
  - InfoSys Parameters:
    - IS1: `base_infectivity=0.1`, `resonance_factor=1.0`, `lock_in_threshold=0.6`, `propagation_bonus=0.2`
    - IS2: `base_infectivity=0.08`, `resonance_factor=1.2`, `lock_in_threshold=0.7`, `propagation_bonus=0.3`
    - IS3: `base_infectivity=0.12`, `resonance_factor=0.9`, `lock_in_threshold=0.5`, `propagation_bonus=0.15`
  - Agent `susceptibility`: `random.uniform(0.3, 0.7)`

- **Observed Dynamics:**
  - **Initial Phase (Gen 0-20):** Slow adoption. IS1 and IS3 gain small initial footholds.
  - **Growth Phase (Gen 30-70):** Rapid adoption. IS1 emerges as a strong contender, followed by IS3. Unaligned agents decrease significantly. Lock-in begins for IS1 and IS3.
  - **Saturation/Competition Phase (Gen 80-199):** Most agents become aligned.
    - IS1 becomes dominant (e.g., ~34 agents, ~32 locked-in by gen 199).
    - IS3 maintains a significant presence (e.g., ~15 agents, ~15 locked-in by gen 199).
    - IS2 struggles, ending with only 1 highly committed (locked-in, max strength) agent.
  - All agents were aligned with a BIC by around generation 80.

- **Interpretation:**
  - The model successfully demonstrates BIC lifecycle phases: exposure, adoption, lock-in, and propagation leading to competitive exclusion/coexistence.
  - IS1's balanced parameters provided a strong advantage.
  - IS3's higher `base_infectivity` and lower `lock_in_threshold` made it a strong early competitor.
  - IS2's lower `base_infectivity` and higher `lock_in_threshold` made it difficult to gain widespread adoption, despite other potentially advantageous parameters. The emergence of a single, highly devoted IS2 adherent is an interesting edge case.

**Run 2: Increased Agents and InfoSys (2025-06-03)**

- **Parameters Used:**
  - `NUM_AGENTS = 200` (increased from 50)
  - `NUM_GENERATIONS = 200`
  - `INTERACTIONS_PER_AGENT_PER_GENERATION = 5`
  - `DIRECT_EXPOSURE_PROBABILITY = 0.05`
  - InfoSys Parameters (5 total):
    - IS1: `base_infectivity=0.1`, `resonance_factor=1.0`, `lock_in_threshold=0.6`, `propagation_bonus=0.2` (blue)
    - IS2: `base_infectivity=0.08`, `resonance_factor=1.2`, `lock_in_threshold=0.7`, `propagation_bonus=0.3` (red)
    - IS3: `base_infectivity=0.12`, `resonance_factor=0.9`, `lock_in_threshold=0.5`, `propagation_bonus=0.15` (green)
    - IS4: `base_infectivity=0.06`, `resonance_factor=1.5`, `lock_in_threshold=0.65`, `propagation_bonus=0.25` (purple, "Stealthy & Resonant")
    - IS5: `base_infectivity=0.15`, `resonance_factor=0.8`, `lock_in_threshold=0.45`, `propagation_bonus=0.1` (orange, "Aggressive Early Spreader")
  - Agent `susceptibility`: `random.uniform(0.3, 0.7)`

- **Observed Dynamics:**
  - **Early Phase (Gen 0-40):** Slower initial spread due to more agents/competition. IS5 ("Aggressive Early Spreader") quickly takes the lead. IS4 ("Stealthy & Resonant") also gains traction.
  - **Growth & IS5 Dominance (Gen 50-100):** IS5's high infectivity and low lock-in threshold allow it to rapidly expand, achieving ~76% adoption (152 agents, 109 locked-in) by Gen 100.
  - **Saturation & IS5 Hegemony (Gen 110-199):** IS5 solidifies its dominance, ending with ~81.5% of agents (163 agents, all locked-in). 
    - IS3 becomes the second largest BIC (~12%, 24 agents, all locked-in).
    - IS4 maintains a smaller niche (~5.5%, 11 agents, all locked-in).
    - IS1 (previous winner) is reduced to a very small group (2 agents).
    - IS2 is effectively eliminated.
  - All agents were aligned with a BIC by around generation 110.

- **Interpretation:**
  - The "Aggressive Early Spreader" strategy of IS5 (high initial infectivity, easy lock-in) proved highly effective in a larger, more competitive environment, allowing it to achieve critical mass and starve out competitors despite a lower propagation bonus.
  - Increased agent and InfoSys numbers led to more fragmented early competition but ultimately still resulted in a single BIC achieving strong dominance.
  - The outcome for previously successful BICs (like IS1) can change dramatically with the introduction of new, differently strategized competitors.

**Run 3: Countering the Aggressive Spreader with IS6 ("Slow Burn, High Loyalty") (2025-06-03)**

- **Parameters Used (Run 2 settings + IS6):**
  - `NUM_AGENTS = 200`
  - `NUM_GENERATIONS = 200`
  - InfoSys Parameters (6 total):
    - IS1: `base_infectivity=0.1`, `resonance_factor=1.0`, `lock_in_threshold=0.6`, `propagation_bonus=0.2` (blue)
    - IS2: `base_infectivity=0.08`, `resonance_factor=1.2`, `lock_in_threshold=0.7`, `propagation_bonus=0.3` (red)
    - IS3: `base_infectivity=0.12`, `resonance_factor=0.9`, `lock_in_threshold=0.5`, `propagation_bonus=0.15` (green)
    - IS4: `base_infectivity=0.06`, `resonance_factor=1.5`, `lock_in_threshold=0.65`, `propagation_bonus=0.25` (purple)
    - IS5: `base_infectivity=0.15`, `resonance_factor=0.8`, `lock_in_threshold=0.45`, `propagation_bonus=0.1` (orange, "Aggressive Early Spreader")
    - IS6: `base_infectivity=0.03`, `resonance_factor=1.0`, `lock_in_threshold=0.85`, `propagation_bonus=0.5` (cyan, "Slow Burn, High Loyalty")
  - Agent `susceptibility`: `random.uniform(0.3, 0.7)`

- **Observed Dynamics:**
  - **IS5 ("Aggressive Early Spreader") Dominance:** IS5 again rapidly dominated, reaching ~91.5% adoption (183 agents, all locked-in) by Gen 130 and maintaining this.
  - **IS6 ("Slow Burn, High Loyalty") Performance:** IS6 struggled significantly due to its very low initial infectivity and high lock-in threshold. It ended with only 1 agent, who was, true to design, locked-in and at maximum strength.
  - **Other BICs:** IS1 maintained a small, stable group of 12 agents. IS3 (3 agents) and IS4 (1 agent) held on with minimal presence. IS2 was eliminated.
  - The population was fully saturated with BICs by generation 100.

- **Interpretation:**
  - The "Slow Burn, High Loyalty" strategy of IS6 was ineffective against IS5's rapid acquisition in a simple, well-mixed model where early lock-in is paramount. The model may need mechanisms like spatiality, network structure, or agent heterogeneity in information processing to allow such strategies a viable niche.

**Phase 1: Multi-IS Agent Models**

Following the initial single-BIC agent models, the ABM was refactored to allow agents to engage with multiple Information Systems (ISs) simultaneously, reflecting a more realistic scenario where individuals are exposed to and can partially adopt or be influenced by several ISs concurrently. This phase explores how agents manage their limited cognitive capacity when faced with multiple ISs.

**Phase 1.a: One Dominant IS, Multiple Secondary ISs**

In this iteration, agents could have one "dominant" IS and a collection of "secondary" ISs. The dominant IS received preferential growth and was the only one an agent would attempt to propagate. Secondary ISs could grow and potentially be "promoted" to dominant status if they became significantly stronger than the current (non-locked-in) dominant IS.

**Run 4: Multi-IS Agent Model - One Dominant, Multiple Secondary (2025-06-03)**

- **Model Type:** First run with refactored `Agent` class allowing one dominant IS and multiple secondary ISs, constrained by `AGENT_MAX_COMMITMENT_CAPACITY`.
- **Key Parameters Used:**
  - `NUM_AGENTS = 50`
  - `NUM_GENERATIONS = 100`
  - `INTERACTIONS_PER_AGENT_PER_GENERATION = 5`
  - `DIRECT_EXPOSURE_PROBABILITY = 0.05`
  - `AGENT_MAX_COMMITMENT_CAPACITY = 1.5`
  - `INITIAL_SECONDARY_STRENGTH = 0.05`
  - `DOMINANT_REINFORCEMENT_BONUS = 0.05`
  - `SECONDARY_REINFORCEMENT_BONUS = 0.03`
  - `DOMINANT_GROWTH_RATE = 0.02`
  - `SECONDARY_GROWTH_RATE = 0.01`
  - `SECONDARY_TO_DOMINANT_THRESHOLD_ADVANTAGE = 0.2`
  - `DOMINANT_DECAY_RATE = 0.005`
  - `SECONDARY_DECAY_RATE = 0.01`
  - `MIN_STRENGTH_FOR_LOCKED_IN_DECAY_MODIFIER = 0.7`
  - InfoSys Parameters: IS1-IS6 unchanged from Run 3.

- **Observed Dynamics (Summary at Generation 99):**
  - **Initial Adoption:** Slow, with most agents unaligned for the first ~20-30 generations.
  - **Dominant ISs:**
    - **IS3:** Emerged as the most prevalent dominant IS (21 agents, 12 locked-in, avg dom strength ~0.46). Also held as secondary by 15 agents.
    - **IS4:** Second most prevalent (18 agents, 6 locked-in, avg dom strength ~0.47). Also held as secondary by 8 agents.
    - **IS1:** Minor presence (4 dominant, 0 locked).
    - **IS2:** Minor presence (1 dominant, 0 locked).
    - **IS5 ("Aggressive Early Spreader"):** Critically, IS5 failed to secure *any* dominant agents. Not listed as significantly held as secondary in final report for ISs with dominant holders.
    - **IS6 ("Slow Burn, High Loyalty"):** Also failed to secure any dominant agents.
  - **Secondary ISs:**
    - Agents gradually accumulated secondary ISs.
    - Avg secondary ISs per agent (overall): ~0.52.
    - Avg secondary ISs for agents *with* secondaries: ~1.13.
    - Avg strength of an individual secondary IS: ~0.06 (quite low).
  - **Promotions:** **Zero promotion events were observed throughout the 100 generations.** No secondary IS ever managed to overtake an established dominant IS.

- **Interpretation:**
  - **Fundamental Shift in Dynamics:** The introduction of multi-IS processing per agent, constrained by cognitive capacity, dramatically altered the competitive landscape compared to single-BIC agent models.
  - **"Stickiness" of Dominant IS:** Once an IS becomes dominant, it appears very difficult to dislodge under the current parameter settings, even if not locked-in. The combination of autonomous growth for dominant ISs, reinforcement bonuses, and the `SECONDARY_TO_DOMINANT_THRESHOLD_ADVANTAGE` likely contributes to this.
  - **Taming of the "Aggressive Spreader":** IS5's previous dominance was completely nullified. This could be due to:
    - Cognitive capacity limits preventing IS5 from consuming all "attention" before other ISs establish a foothold (even as weak secondaries).
    - The initial adoption strength for new ISs (dominant or secondary) being relatively low, not allowing IS5's high infectivity to translate into immediate, overwhelming strength.
  - **Viral Meme Potential (IS5):** While IS5 didn't become a widespread *secondary* IS in this run, the model structure *could* potentially capture "viral meme" behavior (wide but shallow spread, possible rapid disappearance). The fact it didn't show up here might mean its parameters aren't tuned for that under multi-IS conditions, or it's outcompeted too quickly even for secondary slots.
  - **Need for Promotion Tuning:** The lack of promotions suggests that the balance between dominant IS stability and secondary IS challenge capability needs adjustment if we want to observe more fluid transitions in dominant BICs.

**Run 5: Easier Promotions (2025-06-03)**

- **Model Type:** Same as Run 4 (One Dominant, Multiple Secondary ISs).
- **Key Parameter Change:**
  - `SECONDARY_TO_DOMINANT_THRESHOLD_ADVANTAGE` reduced from `0.2` to `0.05` (making it easier for a secondary IS to be promoted).
- **Parameters Used:** Same as Run 4, except for the threshold change.

- **Observed Dynamics (Summary at Generation 99):**
  - **Dominant ISs:**
    - **IS4:** Most prevalent dominant (13 agents, 7 locked-in, avg dom strength ~0.62).
    - **IS5:** Made a comeback as a dominant IS (11 agents, 3 locked-in, avg dom strength ~0.54).
    - **IS1:** Significant presence (10 agents, 3 locked-in, avg dom strength ~0.50).
    - IS3: Minor presence (6 dominant).
    - IS2 & IS6: No dominant agents.
  - **Secondary ISs:**
    - Slightly more prevalent overall compared to Run 4.
    - Avg secondary ISs per agent (overall): ~0.73 (up from ~0.52).
    - Avg strength of an individual secondary IS: ~0.07 (slightly up from ~0.06).
  - **Promotions:** **Still zero promotion events observed.**
  - **Unaligned Agents:** 9 agents remained unaligned.

- **Interpretation:**
  - **Promotion Threshold Not the Sole Factor:** Reducing the promotion threshold did not, by itself, lead to any secondary ISs overtaking dominant ones. This indicates that other factors, such as the differential growth rates between dominant and secondary ISs, and the lock-in mechanism for dominant ISs, contribute more significantly to the "stickiness" of dominant ISs.
  - **Shift in Dominance:** IS5 ("Aggressive Spreader") regained some dominance, suggesting that while the multi-IS capacity model initially tempered it, its inherent infectivity still plays a role. IS4 ("Stealthy & Resonant") also performed well.
  - **Persistent Stickiness:** The core challenge of dominant ISs being too hard to dislodge remains. This led to the consideration of a more fluid model where the strict dominant/secondary distinction is removed.

**Phase 1.b: Portfolio Model - Propagation of Strongest IS**

Given the persistent "stickiness" of dominant ISs and the artificiality of the strict dominant/secondary distinction, the model was further refactored. In this "Portfolio Model," agents no longer have a single dominant IS. Instead, they maintain a portfolio of commitments to multiple ISs simultaneously, each with its own strength and lock-in status, all constrained by the agent's `max_commitment_capacity`.

- **Key Changes in Agent Logic (for Run 6):**
    - No more `dominant_is_id` or `secondary_is_strengths`. Replaced by `is_commitments = {is_id: {"strength": float, "locked_in": bool}}`.
    - All ISs in an agent's portfolio grow based on a single `COMMITMENT_GROWTH_RATE`.
    - Lock-in is per-IS within the portfolio.
    - **Crucially, for this version (Run 6), agents attempt to propagate only their *strongest* IS (if multiple are equally strong, one is chosen randomly).**
    - Capacity adjustment (`_adjust_commitments_to_fit_capacity`) proportionally scales down all commitments if `max_commitment_capacity` is exceeded.
    - Promotion events are no longer applicable.

**Run 6: First Portfolio Model Run (2025-06-03)**

- **Model Type:** Portfolio Model with Propagation of Strongest IS (as described in Phase 1.b).
- **Key Parameters Used:**
  - `NUM_AGENTS = 50`
  - `NUM_GENERATIONS = 100`
  - `INTERACTIONS_PER_AGENT_PER_GENERATION = 5`
  - `DIRECT_EXPOSURE_PROBABILITY = 0.05`
  - `AGENT_MAX_COMMITMENT_CAPACITY = 1.5`
  - `INITIAL_COMMITMENT_STRENGTH = 0.1`
  - `COMMITMENT_REINFORCEMENT_BONUS = 0.05`
  - `COMMITMENT_GROWTH_RATE = 0.015`
  - `COMMITMENT_DECAY_RATE = 0.005`
  - `MIN_STRENGTH_FOR_LOCKED_IN_DECAY_MODIFIER = 0.7`
  - InfoSys Parameters: IS1-IS6 unchanged from Run 3.

- **Observed Dynamics (Summary at Generation 99):**
  - **Uncommitted Agents:** 25 agents (50% of the population) remained uncommitted (no ISs in their portfolio).
  - **IS Stats (Committed Agents | Avg Strength | Locked-in):**
    - IS1: 16 committed | 0.29 avg strength | 3 locked-in
    - IS2: 1 committed | 0.18 avg strength | 0 locked-in
    - IS3: 2 committed | 0.19 avg strength | 0 locked-in
    - IS4: 0 committed
    - IS5: 8 committed | 0.25 avg strength | 1 locked-in
    - IS6: 0 committed
  - **Portfolio Size Distribution (Num ISs: Num Agents):**
    - 0 ISs: 25 agents
    - 1 IS: 23 agents
    - 2 ISs: 2 agents
    - 3+ ISs: 0 agents

- **Interpretation:**
  - **Successful Refactor:** The portfolio model runs and produces plausible dynamics. Agents can now hold multiple ISs, and some do.
  - **IS Spread:** IS1 ("balanced") and IS5 ("Aggressive Early Spreader") are the most successful in terms of number of agents committing to them. IS4 ("Stealthy & Resonant") and IS6 ("Slow Burn, High Loyalty") failed to gain any traction, which is notable for IS4 as it had some success in previous models.
  - **Limited Portfolio Diversity:** While possible, only a small fraction of committed agents (2 out of 25) held more than one IS. Most agents with commitments specialized in a single IS. Given `AGENT_MAX_COMMITMENT_CAPACITY = 1.5` and average strengths around 0.2-0.3, there was theoretical room for larger portfolios.
  - **High Uncommitted Rate:** Half the population remained uncommitted. This could be due to a combination of factors: the `INITIAL_COMMITMENT_STRENGTH` (0.1) being modest, the net growth rate for a new, unreinforced IS being slow (0.015 growth - 0.005 decay = 0.01 net), or the `DIRECT_EXPOSURE_PROBABILITY` (0.05) being insufficient to consistently establish initial footholds.
  - **Propagation of Strongest:** The strategy of propagating only the strongest IS might contribute to single-IS specialization within agents, as the strongest IS gets further chances to spread and reinforce, potentially overshadowing weaker commitments within the same agent when it comes to external influence.

**Phase 1.c: Portfolio Model - Affinity Propagation & Reception (Portfolio v2)**

To introduce more psychological realism based on concepts like the illusory truth effect and confirmation bias, the portfolio model was evolved. The core idea is that an agent's existing affinities strongly shape how they propagate information and how they respond to incoming information.

- **Rationale:** 
    - Agents should "preach more" (amplify) ISs they are more consumed by (higher affinity).
    - Agents should be more receptive to (and more strongly reinforced by) messages about ISs for which they already have a corresponding affinity.

- **Key Changes in Agent Logic (for Run 7 onwards):**
    - New `Agent` parameter: `affinity_reinforcement_multiplier` (e.g., `2.0`).
    - **`attempt_propagation` modified:** An agent now iterates through *all* ISs in its `is_commitments`. For each IS, it calculates a specific `persuasiveness` based on its strength in the agent's portfolio and its `propagation_bonus` (if locked-in). It then attempts to make the target agent adopt *that specific IS* with that calculated persuasiveness. Thus, an agent "broadcasts" all its held beliefs with varying intensity in a single interaction.
    - **`attempt_adoption` modified:**
        - If the `candidate_infosys` is already in the target agent's `is_commitments` (Reinforcement):
            - An `affinity_bonus_factor = (1 + existing_strength * affinity_reinforcement_multiplier)` is calculated.
            - The *chance* of reinforcement (effective propensity) is boosted by this factor.
            - If reinforcement occurs, the *amount* of strength increase is also boosted by this factor (`commitment_reinforcement_bonus * affinity_bonus_factor`).
        - If the `candidate_infosys` is new to the agent, adoption proceeds based on base propensity (New Adoption).

**Run 7: Affinity Propagation Model (Portfolio v2) (2025-06-03)**

- **Model Type:** Portfolio Model with Affinity Propagation & Reception (as described in Phase 1.c).
- **Key Parameters Used (Boosted from Run 6 + New Multiplier):**
  - `NUM_AGENTS = 50`, `NUM_GENERATIONS = 100`
  - `DIRECT_EXPOSURE_PROBABILITY = 0.075` (up from 0.05 in Run 6)
  - `AGENT_MAX_COMMITMENT_CAPACITY = 1.5`
  - `INITIAL_COMMITMENT_STRENGTH = 0.15` (up from 0.1 in Run 6)
  - `COMMITMENT_REINFORCEMENT_BONUS = 0.05`
  - `COMMITMENT_GROWTH_RATE = 0.02` (up from 0.015 in Run 6)
  - `COMMITMENT_DECAY_RATE = 0.005`
  - `MIN_STRENGTH_FOR_LOCKED_IN_DECAY_MODIFIER = 0.7`
  - `AFFINITY_REINFORCEMENT_MULTIPLIER = 2.0` (New)
  - InfoSys Parameters:
    - IS4: `base_infectivity` increased to `0.08` (from 0.06)
    - IS6: `base_infectivity` increased to `0.05` (from 0.03)
    - IS1, IS2, IS3, IS5 unchanged from previous runs.

- **Observed Dynamics (Summary at Generation 99):**
  - **Uncommitted Agents:** 0. All agents became committed to at least one IS.
  - **IS Stats (Committed Agents | Avg Strength | Locked-in):**
    - IS1: 8 committed | 0.16 avg strength | 0 locked-in
    - IS2: 50 committed | 0.77 avg strength | 49 locked-in (Clearly dominant)
    - IS3: 44 committed | 0.21 avg strength | 13 locked-in
    - IS4: 48 committed | 0.29 avg strength | 7 locked-in
    - IS5: 49 committed | 0.23 avg strength | 26 locked-in
    - IS6: 0 committed
  - **Portfolio Size Distribution (Num ISs: Num Agents):**
    - 0 ISs: 0 agents
    - 1 IS: 0 agents
    - 2 ISs: 0 agents
    - 3 ISs: 7 agents
    - 4 ISs: 37 agents
    - 5 ISs: 6 agents

- **Interpretation:**
  - **Dramatic Impact of New Model & Parameters:** The combination of the affinity-driven propagation/reception model and the boosted base parameters led to full agent engagement and much larger, more diverse portfolios compared to Run 6.
  - **Emergence of a Hegemon (IS2):** IS2 (`base_infectivity=0.08`, `resonance_factor=1.2`, `lock_in_threshold=0.7`, `propagation_bonus=0.3`) became the overwhelmingly dominant IS. It is present in every agent, has a high average strength, and is almost universally locked-in. Its good resonance and propagation bonus, coupled with the new affinity mechanics, likely created a strong positive feedback loop.
  - **Widespread Coexistence of Other ISs:** Despite IS2's dominance, IS3, IS4 (benefitting from its infectivity boost), and IS5 are also highly prevalent, coexisting in most agents' portfolios as significant secondary/tertiary commitments. This suggests the model can support a dominant BIC alongside a diverse set of other influences.
  - **Confirmation Bias at Play:** The affinity-boosted reinforcement mechanism appears effective, likely accelerating the strengthening of ISs once they gain a foothold and contributing to the high lock-in rates for successful ISs like IS2 and IS5.
  - **Propagation of Multiple ISs:** Agents broadcasting all their held ISs (with varied strength) ensures that even less dominant ISs in an agent's portfolio get chances to spread, contributing to the observed portfolio diversity.
  - **IS6 Still Fails:** Even with an infectivity boost, IS6 (`base_infectivity=0.05`, very high lock-in: `0.85`) did not gain any adherents. Its high lock-in threshold might still be too difficult to overcome, even if initial adoption occurs.
  - **High Capacity Utilization:** Agents are generally using their `max_commitment_capacity` fully, with complex portfolios. The system is much more "active" or "hotter" than in previous portfolio runs.

**Phase 1.d: Introducing Agent Vitality (Portfolio v2 - Affinity Propagation + Vitality)**

Building on the Affinity Propagation model, this phase introduces the concept of `agent_vitality` to explore the direct consequences of IS commitments on the host agent, as per the BIC theory's "Functional Spectrum" (Mutualist, Commensal, Parasitic).

- **Rationale:**
    - To model how different ISs can benefit or harm their host.
    - To create a new metric (`agent_vitality`) that can be observed and, in future iterations, potentially create feedback loops influencing agent behavior or IS dynamics.

- **Key Changes in Model (for Run 8 onwards):**
    - **`InfoSys` Class:** Added `vitality_impact` attribute (float, e.g., positive for mutualistic, negative for parasitic, zero for commensal). This value represents the per-strength-point impact on agent vitality per generation.
    - **`Agent` Class:**
        - Added `initial_vitality` attribute (defaults to `1.0`) and an `initial_vitality_cap` (e.g., `initial_vitality * 2.0`).
        - Added `update_vitality(infosystems_map)` method: Calculates total vitality change based on `strength * vitality_impact` for all held ISs and updates agent's `vitality`. Vitality is capped to prevent excessive growth but can decrease (potentially below zero in this version).
    - **Simulation Loop:** A new step is added where `agent.update_vitality()` is called for all agents each generation.
    - **Data Collection:** Average, min, and max agent vitality are now tracked and reported.

**Run 8: Affinity Propagation Model with Agent Vitality (2025-06-03)**

- **Model Type:** Portfolio Model with Affinity Propagation & Reception, plus Agent Vitality (as described in Phase 1.d).
- **Parameters Used:** Same as Run 7 (boosted base parameters, `AFFINITY_REINFORCEMENT_MULTIPLIER = 2.0`), with the addition of `vitality_impact` for each InfoSys:
  - IS1 (Commensal): `vitality_impact = 0.0`
  - IS2 (Slightly Mutualistic): `vitality_impact = 0.002`
  - IS3 (Commensal): `vitality_impact = 0.0`
  - IS4 (Slightly Parasitic): `vitality_impact = -0.001`
  - IS5 (Parasitic): `vitality_impact = -0.003`
  - IS6 (Mutualistic): `vitality_impact = 0.005`

- **Observed Dynamics (Summary at Generation 99):**
  - **Uncommitted Agents:** 0. All 50 agents were committed.
  - **Agent Vitality (Initial Avg: 1.00):**
    - Average: 0.90
    - Min: 0.80
    - Max: 1.04
  - **IS Stats (Committed Agents | Avg Strength | Locked-in | Vitality Impact):**
    - IS1: 5 committed | 0.17 avg str | 0 locked | V: 0.0
    - IS2: 45 committed | 0.27 avg str | 4 locked | V: +0.002
    - IS3: 6 committed | 0.16 avg str | 0 locked | V: 0.0
    - IS4: 50 committed | 0.34 avg str | 10 locked | V: -0.001
    - IS5: 50 committed | 0.87 avg str | 50 locked | V: -0.003 (Dominant IS)
    - IS6: 0 committed | V: +0.005
  - **Portfolio Size Distribution (Num ISs: Num Agents):** Most agents held 3 ISs (36 agents) or 4 ISs (10 agents).

- **Interpretation:**
  - **Shift in Dominance to Parasitic IS5:** IS5 ("Aggressive Spreader," now defined as parasitic) became the clear dominant IS, a reversal from Run 7 where the mutualistic IS2 was dominant. This is a critical finding: the assigned vitality impact alone did not deter its spread.
  - **Degradation of Mutualistic IS2:** While still widespread, IS2's average strength and lock-in count significantly dropped compared to Run 7, overshadowed by IS5.
  - **Successful Parasitism:** IS5 and IS4 (also parasitic) are highly prevalent. The overall average agent vitality slightly declined (from 1.0 to 0.90), demonstrating the cumulative negative impact of these parasitic ISs.
  - **No Intrinsic Defense Against Parasitism (Yet):** This run highlights that if a parasitic IS is highly infectious/effective at propagation, agents will adopt and spread it, suffering vitality costs, if vitality itself doesn't feed back into core agent behaviors like susceptibility, adoption probability, or propagation ability. The current model lacks a mechanism for agents to actively resist or recover from parasitic load based on vitality alone.
  - **IS6 (Mutualistic) Still Fails:** The positive vitality impact of IS6 was not enough to overcome its low infectivity and high lock-in threshold.
  - **Model Sensitivity:** The dynamics of the system are sensitive to the interplay of infectivity, propagation mechanics, and now vitality impacts. The most infectious IS (IS5) dominated despite its parasitic nature.

*(This section will be updated with results from running the simulation with different parameters and analyzing the outcomes.)*

---
_Initial model structure and README created by AI assistant._ 