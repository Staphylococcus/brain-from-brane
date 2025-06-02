#!/usr/bin/env python3
"""
H2: GEOMETRIC ORDER STABILITY TEST
Tests Hypothesis 2: "Outward Stabilization" Effect of Information Geometry on Algorithmic Execution Stability.
This experiment investigates if algorithms processing data structures with higher
"internal information-geometric order" (e.g., a balanced tree vs. a skewed tree)
exhibit lower Coefficient of Variation (CV) in their execution time.
"""

import time
import statistics
import random
import math

# --- Configuration ---
K_ARY = 3  # Branching factor for the trees
NUM_NODES = 300  # Approximate number of nodes in each tree (will be exact for balanced)
NUM_ITERATIONS_PER_TREE = 100  # Number of times to run the algorithm on each tree
NUM_DISORDERED_TREE_INSTANCES = 5 # Number of different random trees to generate and test

# --- Tree Implementation ---
class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, node):
        if len(self.children) < K_ARY:
            self.children.append(node)
            return True
        return False

def build_perfectly_balanced_tree(num_nodes, k):
    """Builds a perfectly balanced k-ary tree with approximately num_nodes."""
    if num_nodes <= 0:
        return None, 0
    
    root = Node(0) # Value can be anything, structure is what matters
    nodes_created = 1
    
    queue = [root]
    head = 0
    
    while nodes_created < num_nodes and head < len(queue):
        current_parent = queue[head]
        head += 1
        
        for i in range(k):
            if nodes_created < num_nodes:
                child = Node(nodes_created)
                current_parent.add_child(child)
                queue.append(child)
                nodes_created += 1
            else:
                break
    return root, nodes_created

def build_randomly_structured_tree(num_nodes, k):
    """Builds a randomly structured k-ary tree with num_nodes."""
    if num_nodes <= 0:
        return None
    nodes = [Node(i) for i in range(num_nodes)]
    root = nodes[0]
    
    available_parents = [root]
    
    for i in range(1, num_nodes):
        child_node = nodes[i]
        added = False
        attempts = 0
        while not added and attempts < len(available_parents) * k:
            # Try to add to a random available parent that has space
            parent_idx = random.randrange(len(available_parents))
            parent_node = available_parents[parent_idx]
            if parent_node.add_child(child_node):
                available_parents.append(child_node) # New node can also be a parent
                added = True
            else:
                # If parent is full, try another. For simplicity, remove if full.
                # A more sophisticated approach might keep track of full parents separately.
                if len(parent_node.children) == k:
                    # This is a heuristic to favor broader trees over very deep ones in random construction.
                    # Without it, it might quickly become a list if only root is available and gets full.
                    pass # Keep it for other children if it got full with this attempt
            attempts +=1
        
        if not added:
             # Fallback: if we struggle to find a parent, pick one at random and force add if possible,
             # or just add to the last available parent. This part can be tricky to make truly "random"
             # without making it too degenerate or too balanced. This is a simple heuristic.
            if available_parents: # Should always be true after root
                 # Add new node as child to a random parent from those that might still have capacity
                parent_node = random.choice(available_parents)
                if parent_node.add_child(child_node):
                     available_parents.append(child_node)
                else:
                    # As a last resort, make it a child of the root or last added node if root is full
                    # This could lead to deeper structures
                    # For this experiment, we'll assume the earlier logic is sufficient
                    # and if a node can't be added, the tree might have fewer nodes.
                    # print(f"Warning: Could not place node {i}. Tree will have <{num_nodes} nodes.")
                    pass # This node is orphaned for this simple version

    return root

# --- Algorithm to Test ---
def depth_first_traversal(node):
    """Performs a depth-first traversal and sums node values (to do some work)."""
    if node is None:
        return 0
    total = node.value
    for child in node.children:
        total += depth_first_traversal(child)
    return total

# --- Experiment Execution ---
def run_single_tree_test(tree_root, algorithm, num_iterations):
    """Runs algorithm on the tree multiple times and returns timings."""
    timings_ns = []
    if tree_root is None:
        return timings_ns
        
    for _ in range(num_iterations):
        start_time = time.perf_counter_ns()
        algorithm(tree_root) # Actual work
        end_time = time.perf_counter_ns()
        timings_ns.append(end_time - start_time)
    return timings_ns

def calculate_stats(timings_ns):
    if not timings_ns or len(timings_ns) < 2:
        return 0, 0
    mean_time_ns = statistics.mean(timings_ns)
    stdev_time_ns = statistics.stdev(timings_ns)
    cv = stdev_time_ns / mean_time_ns if mean_time_ns > 0 else 0
    return mean_time_ns, cv

def run_experiment():
    """Runs the full experiment for Hypothesis 2."""
    print("🔬 HYPOTHESIS 2: GEOMETRIC ORDER STABILITY TEST")
    print(f"K-ary factor: {K_ARY}, Target number of nodes: {NUM_NODES}")
    print(f"Iterations per tree: {NUM_ITERATIONS_PER_TREE}")
    print(f"Number of disordered tree instances: {NUM_DISORDERED_TREE_INSTANCES}")
    print("-" * 70)
    print("Tree Type,Instance,Nodes,Mean Time (ns),CV")

    # Test Ordered (Balanced) Tree
    ordered_tree_root, actual_ordered_nodes = build_perfectly_balanced_tree(NUM_NODES, K_ARY)
    if ordered_tree_root:
        timings = run_single_tree_test(ordered_tree_root, depth_first_traversal, NUM_ITERATIONS_PER_TREE)
        mean_time, cv = calculate_stats(timings)
        print(f"Ordered (Balanced),1,{actual_ordered_nodes},{mean_time:.0f},{cv:.6f}")
    else:
        print("Ordered (Balanced),1,0,0,0 --- Failed to build")

    # Test Disordered (Randomly Structured) Trees
    all_disordered_cvs = []
    for i in range(NUM_DISORDERED_TREE_INSTANCES):
        # Estimate node count for random tree; it might not reach NUM_NODES perfectly
        # with the simple builder. This is a known limitation of a simple random builder.
        # For this test, we count actual nodes after building.
        temp_nodes_for_random_build = NUM_NODES # Target same number of nodes
        disordered_tree_root = build_randomly_structured_tree(temp_nodes_for_random_build, K_ARY)
        
        # Count actual nodes in the generated random tree (traversal can do this)
        actual_disordered_nodes = 0
        if disordered_tree_root:
            queue = [disordered_tree_root]
            head = 0
            while head < len(queue):
                curr = queue[head]
                head +=1
                actual_disordered_nodes +=1
                for child in curr.children:
                    queue.append(child)

        if disordered_tree_root and actual_disordered_nodes > K_ARY : # Ensure a non-trivial tree
            timings = run_single_tree_test(disordered_tree_root, depth_first_traversal, NUM_ITERATIONS_PER_TREE)
            mean_time, cv = calculate_stats(timings)
            print(f"Disordered (Random),{i+1},{actual_disordered_nodes},{mean_time:.0f},{cv:.6f}")
            if cv > 0: all_disordered_cvs.append(cv)
        else:
            print(f"Disordered (Random),{i+1},{actual_disordered_nodes},0,0 --- Failed to build adequately or too small")

    if all_disordered_cvs:
        avg_disordered_cv = statistics.mean(all_disordered_cvs)
        print(f"Average CV for disordered trees: {avg_disordered_cv:.6f}")
    else:
        print("No valid disordered tree CVs collected.")
        
    print("-" * 70)
    print("Experiment finished.")

if __name__ == "__main__":
    run_experiment() 