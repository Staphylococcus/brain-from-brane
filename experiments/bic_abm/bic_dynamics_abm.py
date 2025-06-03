import random
from abm_components import InfoSys, Agent

# Simulation Parameters (Portfolio Model)
NUM_AGENTS = 50
NUM_GENERATIONS = 100
INTERACTIONS_PER_AGENT_PER_GENERATION = 5
DIRECT_EXPOSURE_PROBABILITY = 0.075 # Increased from 0.05
AGENT_MAX_COMMITMENT_CAPACITY = 1.5 # Max total strength an agent can hold
INITIAL_COMMITMENT_STRENGTH = 0.15   # Increased from 0.1
COMMITMENT_REINFORCEMENT_BONUS = 0.05 # Strength increase on re-exposure/re-adoption
COMMITMENT_GROWTH_RATE = 0.02      # Increased from 0.015
COMMITMENT_DECAY_RATE = 0.005       # Strength decay per generation for committed ISs
MIN_STRENGTH_FOR_LOCKED_IN_DECAY_MODIFIER = 0.7 # Min strength for locked-in IS to benefit from reduced decay
AFFINITY_REINFORCEMENT_MULTIPLIER = 2.0 # New global parameter for agent initialization
# AGENT_INITIAL_VITALITY = 1.0 # This will be handled by default in Agent class for now

def run_simulation():
    infosystems = [
        InfoSys(id="IS1", base_infectivity=0.1, resonance_factor=1.0, lock_in_threshold=0.6, propagation_bonus=0.2, color="blue", vitality_impact=0.0),
        InfoSys(id="IS2", base_infectivity=0.08, resonance_factor=1.2, lock_in_threshold=0.7, propagation_bonus=0.3, color="red", vitality_impact=0.002),
        InfoSys(id="IS3", base_infectivity=0.12, resonance_factor=0.9, lock_in_threshold=0.5, propagation_bonus=0.15, color="green", vitality_impact=0.0),
        InfoSys(id="IS4", base_infectivity=0.08, resonance_factor=1.5, lock_in_threshold=0.65, propagation_bonus=0.25, color="purple", vitality_impact=-0.001),
        InfoSys(id="IS5", base_infectivity=0.15, resonance_factor=0.8, lock_in_threshold=0.45, propagation_bonus=0.1, color="orange", vitality_impact=-0.003),
        InfoSys(id="IS6", base_infectivity=0.05, resonance_factor=1.0, lock_in_threshold=0.85, propagation_bonus=0.5, color="cyan", vitality_impact=0.005)
    ]
    infosystems_map = {is_obj.id: is_obj for is_obj in infosystems} # For quick lookup

    agents = [Agent(id=i,
                    susceptibility=random.uniform(0.3, 0.7),
                    max_commitment_capacity=AGENT_MAX_COMMITMENT_CAPACITY,
                    initial_commitment_strength=INITIAL_COMMITMENT_STRENGTH,
                    commitment_reinforcement_bonus=COMMITMENT_REINFORCEMENT_BONUS,
                    affinity_reinforcement_multiplier=AFFINITY_REINFORCEMENT_MULTIPLIER
                    ) for i in range(NUM_AGENTS)]

    print(f"Starting simulation with {NUM_AGENTS} agents, {len(infosystems)} InfoSys, for {NUM_GENERATIONS} generations (Portfolio Model v2 - Affinity Propagation).")
    print(f"Agent capacity: {AGENT_MAX_COMMITMENT_CAPACITY}, IS growth: {COMMITMENT_GROWTH_RATE}, IS decay: {COMMITMENT_DECAY_RATE}, Affinity Multiplier: {AFFINITY_REINFORCEMENT_MULTIPLIER}")

    history = []

    for gen in range(NUM_GENERATIONS):
        # Step 1: Direct Exposure & Adoption
        for agent in agents:
            # Allow direct exposure even if agent has commitments, relying on capacity adjustment
            if random.random() < DIRECT_EXPOSURE_PROBABILITY:
                chosen_infosys = random.choice(infosystems)
                agent.attempt_adoption(chosen_infosys, source_strength=1.0, infosystems_list=infosystems)

        # Step 2: Agent Interaction & Propagation
        for agent in agents:
            if agent.is_commitments: # Agent must have at least one IS to propagate
                for _ in range(INTERACTIONS_PER_AGENT_PER_GENERATION):
                    target_agent = random.choice(agents)
                    if target_agent.id != agent.id:
                        agent.attempt_propagation(target_agent, infosystems)
        
        # Step 3: Update IS States (growth, lock-in)
        for agent in agents:
            agent.update_is_states(infosystems,
                                   growth_rate=COMMITMENT_GROWTH_RATE)
            
        # Step 4: Decay IS States
        for agent in agents:
            agent.possibly_decay_is_states(infosystems, # infosystems might be useful for future decay logic tied to IS properties
                                           decay_rate=COMMITMENT_DECAY_RATE,
                                           min_strength_for_locked_in_decay_modifier=MIN_STRENGTH_FOR_LOCKED_IN_DECAY_MODIFIER)

        # Step 5: Update Agent Vitality
        for agent in agents:
            agent.update_vitality(infosystems_map)

        # --- Data Collection & Reporting (Portfolio Model v2 + Vitality) ---
        is_commitment_counts = {sys.id: 0 for sys in infosystems}
        is_strength_sums = {sys.id: 0.0 for sys in infosystems}
        is_locked_in_counts = {sys.id: 0 for sys in infosystems}
        
        portfolio_sizes = {i: 0 for i in range(len(infosystems) + 1)} # Count of agents holding 0, 1, ... N ISs
        uncommitted_agents = 0
        agent_vitality_sum = 0.0
        min_agent_vitality_this_gen = float('inf')
        max_agent_vitality_this_gen = float('-inf')
        
        for agent in agents:
            num_commitments = len(agent.is_commitments)
            portfolio_sizes[num_commitments] += 1
            if num_commitments == 0:
                uncommitted_agents +=1
            
            agent_vitality_sum += agent.vitality
            min_agent_vitality_this_gen = min(min_agent_vitality_this_gen, agent.vitality)
            max_agent_vitality_this_gen = max(max_agent_vitality_this_gen, agent.vitality)

            for is_id, data in agent.is_commitments.items():
                is_commitment_counts[is_id] += 1
                is_strength_sums[is_id] += data["strength"]
                if data["locked_in"]:
                    is_locked_in_counts[is_id] +=1
        
        avg_is_strengths = {
            sys_id: (is_strength_sums[sys_id] / count if count > 0 else 0)
            for sys_id, count in is_commitment_counts.items()
        }
        
        avg_agent_vitality = agent_vitality_sum / NUM_AGENTS if NUM_AGENTS > 0 else 0
        
        generation_data = {
            "generation": gen,
            "is_commitment_counts": is_commitment_counts,
            "avg_is_strengths": avg_is_strengths,
            "is_locked_in_counts": is_locked_in_counts,
            "uncommitted_agents": uncommitted_agents,
            "portfolio_size_distribution": portfolio_sizes,
            "avg_agent_vitality": avg_agent_vitality,
            "min_agent_vitality": min_agent_vitality_this_gen if NUM_AGENTS > 0 else 0,
            "max_agent_vitality": max_agent_vitality_this_gen if NUM_AGENTS > 0 else 0
        }
        history.append(generation_data)

        if gen % 10 == 0 or gen == NUM_GENERATIONS -1 :
            print(f"\n--- Generation {gen} ---")
            print(f"Uncommitted Agents (no IS): {uncommitted_agents}")
            print(f"Agent Vitality (Avg/Min/Max): {avg_agent_vitality:.2f} / {min_agent_vitality_this_gen:.2f} / {max_agent_vitality_this_gen:.2f}")
            print("IS Stats (Committed Agents | Avg Strength | Locked-in):")
            for sys_id_report in infosystems: # Iterate through infosystems to maintain order and show all
                count = is_commitment_counts[sys_id_report.id]
                avg_str = avg_is_strengths[sys_id_report.id]
                locked_c = is_locked_in_counts[sys_id_report.id]
                if count > 0: # Only print ISs that have some presence
                     print(f"  IS {sys_id_report.id}: {count} | {avg_str:.2f} | {locked_c}")
            
            print("Portfolio Size Distribution (Num ISs: Num Agents):")
            portfolio_dist_str_parts = []
            for size, num_agents_with_size in portfolio_sizes.items():
                if num_agents_with_size > 0:
                    portfolio_dist_str_parts.append(f"{size}: {num_agents_with_size}")
            print("  " + ", ".join(portfolio_dist_str_parts))
    
    print(f"\nSimulation finished for portfolio model after {NUM_GENERATIONS} generations.")
    # No promotion count to report

    # For example, print the state of a few agents at the end:
    print("\n--- Final Agent States (Sample) ---")
    for i in range(min(5, NUM_AGENTS)):
        if i < len(agents): # Ensure we don't go out of bounds if NUM_AGENTS is very small for some reason
            print(agents[i])

    return history

if __name__ == "__main__":
    simulation_history = run_simulation()
    # Further analysis or plotting would go here
    
    print("\nPortfolio Model ABM run complete. Next step would be to analyze/plot simulation_history.")