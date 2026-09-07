"""
Demonstration of Gossip Protocol Epidemic State Sync Skill
"""

from client import GossipNetwork

def main():
    print("=== Initializing 20-Agent Decentralized Gossip Swarm ===")
    network = GossipNetwork(node_count=20, fanout=3)

    # Origin node publishes critical discovery
    origin = network.nodes["agent-00"]
    origin.set("threat_level", "ELEVATED_DEFENSE_TRIGGER")
    print(f"Origin agent-00 set 'threat_level' = '{origin.store['threat_level'].value}'")

    print("\nSimulating Epidemic Gossip Rounds:")
    for round_num in range(1, 6):
        applied = network.run_round()
        convergence = network.calculate_convergence("threat_level", "ELEVATED_DEFENSE_TRIGGER")
        print(f"  Round {round_num}: {applied} state exchanges applied, Swarm Convergence: {convergence * 100:.1f}%")
        if convergence >= 1.0:
            print(f"Full 100% Swarm Convergence achieved in {round_num} rounds!")
            break

    final_convergence = network.calculate_convergence("threat_level", "ELEVATED_DEFENSE_TRIGGER")
    assert final_convergence == 1.0
    print("Gossip Protocol Epidemic State Sync Verification PASS!")

if __name__ == "__main__":
    main()
