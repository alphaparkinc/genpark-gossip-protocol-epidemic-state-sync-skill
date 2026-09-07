"""
MCP Server for Gossip Protocol Epidemic State Sync Skill
"""

import json
import sys
from client import GossipNetwork

net = GossipNetwork(node_count=10, fanout=2)

def handle_call(name: str, args: dict) -> dict:
    if name == "publish_state":
        nid = args.get("node_id", "agent-00")
        k = args.get("key")
        v = args.get("value")
        if nid in net.nodes and k:
            net.nodes[nid].set(k, v)
            return {"status": "published", "node": nid, "key": k, "value": v}
        return {"error": "Invalid node or key"}
    elif name == "step_sync":
        rounds = args.get("rounds", 1)
        for _ in range(rounds):
            net.run_round()
        return {"status": "synced", "rounds": rounds}
    elif name == "check_convergence":
        k = args.get("key")
        exp = args.get("expected_value")
        ratio = net.calculate_convergence(k, exp)
        return {"key": k, "convergence_ratio": ratio}
    return {"error": f"Unknown tool: {name}"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = handle_call(req.get("method"), req.get("params", {}))
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
