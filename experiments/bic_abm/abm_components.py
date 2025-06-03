import random

class InfoSys:
    def __init__(self, id, base_infectivity, resonance_factor, lock_in_threshold, propagation_bonus, color="white", vitality_impact=0.0):
        self.id = id
        self.base_infectivity = base_infectivity
        self.resonance_factor = resonance_factor
        self.lock_in_threshold = lock_in_threshold
        self.propagation_bonus = propagation_bonus
        self.color = color # For potential visualization
        self.vitality_impact = vitality_impact # e.g., +0.005 for mutualist, -0.005 for parasitic per strength point per generation

class Agent:
    def __init__(self, id, susceptibility, max_commitment_capacity=1.5, initial_commitment_strength=0.1, commitment_reinforcement_bonus=0.05, affinity_reinforcement_multiplier=2.0, initial_vitality=1.0):
        self.id = id
        self.susceptibility = susceptibility
        self.max_commitment_capacity = max_commitment_capacity
        
        self.is_commitments = {}  # {is_id: {"strength": float, "locked_in": bool}}
        
        self.initial_commitment_strength = initial_commitment_strength
        self.commitment_reinforcement_bonus = commitment_reinforcement_bonus
        self.affinity_reinforcement_multiplier = affinity_reinforcement_multiplier
        
        self.vitality = initial_vitality
        self.initial_vitality_cap = initial_vitality * 2.0 # Cap vitality from growing excessively

    def __repr__(self):
        commitments_info_parts = []
        if self.is_commitments:
            for is_id, data in sorted(self.is_commitments.items(), key=lambda item: item[1]["strength"], reverse=True):
                commitments_info_parts.append(f"{is_id}(S:{data['strength']:.2f}, L:{data['locked_in']})")
        commitments_info = ", Commitments: [" + ", ".join(commitments_info_parts) + "]" if commitments_info_parts else ""
        return f"Agent({self.id}, Vit:{self.vitality:.2f}, Cap:{self.get_total_commitment():.2f}/{self.max_commitment_capacity}{commitments_info})"

    def get_total_commitment(self):
        return sum(data["strength"] for data in self.is_commitments.values())

    def _adjust_commitments_to_fit_capacity(self):
        """If total commitment exceeds capacity, reduce strengths proportionally."""
        total_commitment = self.get_total_commitment()
        overflow = total_commitment - self.max_commitment_capacity

        if overflow <= 0:
            return

        if total_commitment == 0: # Avoid division by zero if all strengths are zero (should not happen if overflow > 0)
            return

        for is_id in list(self.is_commitments.keys()): # Iterate over a copy for safe modification
            current_data = self.is_commitments[is_id]
            reduction_share = current_data["strength"] / total_commitment
            current_data["strength"] -= overflow * reduction_share
            
            if current_data["strength"] < 0.01: # Threshold to remove weak commitments
                del self.is_commitments[is_id]
            else: # Ensure locked_in status is maintained if strength is still sufficient
                # This might need refinement: if it drops below lock-in threshold, should it unlock?
                # For now, lock-in status only changes in update_is_states or if IS is removed.
                pass

    def attempt_adoption(self, candidate_infosys, source_strength=1.0, infosystems_list=None):
        # Compatibility modifier (can be enhanced later, e.g., IS-IS interactions)
        compatibility_modifier = 1.0 
        
        base_propensity = candidate_infosys.base_infectivity * \
                          candidate_infosys.resonance_factor * \
                          self.susceptibility * \
                          source_strength * \
                          compatibility_modifier

        adopted_or_reinforced = False

        if candidate_infosys.id in self.is_commitments:
            # --- Reinforcement of existing IS ---
            existing_strength = self.is_commitments[candidate_infosys.id]["strength"]
            affinity_bonus_factor = (1 + existing_strength * self.affinity_reinforcement_multiplier)
            
            effective_propensity_for_reinforcement = base_propensity * affinity_bonus_factor

            if random.random() < effective_propensity_for_reinforcement:
                strength_increase = self.commitment_reinforcement_bonus * affinity_bonus_factor
                self.is_commitments[candidate_infosys.id]["strength"] = min(1.0, existing_strength + strength_increase)
                # Lock-in status is handled by update_is_states, but reinforcement can push strength up
                adopted_or_reinforced = True
        else:
            # --- Adoption of new IS ---
            if random.random() < base_propensity: # Use base_propensity for new adoption
                self.is_commitments[candidate_infosys.id] = {
                    "strength": self.initial_commitment_strength,
                    "locked_in": False
                }
                adopted_or_reinforced = True

        if adopted_or_reinforced:
            self._adjust_commitments_to_fit_capacity()
            return True
        return False

    def update_is_states(self, infosystems_list, growth_rate=0.01):
        for is_id, data in list(self.is_commitments.items()):
            current_is_obj = next((sys for sys in infosystems_list if sys.id == is_id), None)
            if not current_is_obj:
                continue

            if not data["locked_in"]:
                data["strength"] += growth_rate
                if data["strength"] >= current_is_obj.lock_in_threshold:
                    data["locked_in"] = True
                    data["strength"] = min(1.0, max(data["strength"], current_is_obj.lock_in_threshold))
            else: 
                data["strength"] = min(1.0, data["strength"] + (growth_rate / 2))

            data["strength"] = min(1.0, data["strength"])

        self._adjust_commitments_to_fit_capacity()

    def attempt_propagation(self, target_agent, infosystems_list):
        if not self.is_commitments or not infosystems_list:
            return False # Agent has nothing to propagate or no IS list to reference

        propagated_anything = False
        for is_id, data in self.is_commitments.items():
            # Find the full InfoSys object for propagation bonus etc.
            propagating_is_obj = next((sys for sys in infosystems_list if sys.id == is_id), None)
            if not propagating_is_obj: # Should not happen if IS is in agent's commitments and infosystems_list is current
                continue

            # Calculate persuasiveness for this specific IS
            persuasiveness = data["strength"]
            if data["locked_in"]:
                persuasiveness *= (1 + propagating_is_obj.propagation_bonus)
            
            if persuasiveness <= 0.01: # Don't bother propagating if strength is negligible
                continue

            # Target agent attempts to adopt this specific IS with its calculated persuasiveness
            if target_agent.attempt_adoption(propagating_is_obj, source_strength=persuasiveness, infosystems_list=infosystems_list):
                propagated_anything = True
        
        return propagated_anything # Returns true if at least one IS was successfully propagated (or reinforced on target)

    def possibly_decay_is_states(self, infosystems_list, decay_rate=0.005, 
                                 min_strength_for_locked_in_decay_modifier=0.7):
        for is_id in list(self.is_commitments.keys()):
            data = self.is_commitments[is_id]
            
            current_decay_rate = decay_rate
            if data["locked_in"] and data["strength"] > min_strength_for_locked_in_decay_modifier:
                current_decay_rate /= 2 
            
            data["strength"] -= current_decay_rate
            
            if data["strength"] < 0.01:
                del self.is_commitments[is_id]
        
        # No need to call update_is_states or similar after decay as there's no dominant/secondary promotion cascade
        # _adjust_commitments_to_fit_capacity is also not strictly needed here as decay reduces commitment.
        # However, if an IS is removed, and another logic implies re-evaluation of commitments, it might be.
        # For now, keep it simple. 

    def update_vitality(self, infosystems_map):
        """Updates agent vitality based on the ISs in its portfolio."""
        if not self.is_commitments or not infosystems_map:
            return

        total_vitality_change_this_generation = 0.0
        for is_id, data in self.is_commitments.items():
            is_obj = infosystems_map.get(is_id)
            if is_obj:
                total_vitality_change_this_generation += data["strength"] * is_obj.vitality_impact
        
        self.vitality += total_vitality_change_this_generation
        # Cap vitality to prevent runaway positive effects, allow it to go below zero (or to a very low floor if desired later)
        self.vitality = min(self.vitality, self.initial_vitality_cap)
        # self.vitality = max(self.vitality, 0.0) # Optional floor 