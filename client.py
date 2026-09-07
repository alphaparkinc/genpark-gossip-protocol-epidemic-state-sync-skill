"""
Gossip Protocol Epidemic State Sync Skill Client
Pure Python Standard Library implementation of decentralized anti-entropy gossip dissemination.
Spreads agent beliefs, observations, and key-value state updates rapidly across large swarms
with logarithmic convergence time O(log N).
"""

from typing import List, Dict, Any, Tuple, Optional, Set
import random
import time


class StateItem:
    def __init__(self, key: str, value: Any, version: int, origin: str):
        self.key = key
        self.value = value
        self.version = version
        self.origin = origin
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "version": self.version,
            "origin": self.origin,
            "timestamp": self.timestamp
        }


class GossipNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.store: Dict[str, StateItem] = {}
        self.peers: List[str] = []

    def set(self, key: str, value: Any):
        curr = self.store.get(key)
        new_version = (curr.version + 1) if curr else 1
        self.store[key] = StateItem(key, value, new_version, self.node_id)

    def get_digest(self) -> Dict[str, int]:
        """Return {key: version} map for reconciliation."""
        return {k: v.version for k, v in self.store.items()}

    def prepare_diff(self, peer_digest: Dict[str, int]) -> List[Dict[str, Any]]:
        """Return items where local version is newer than peer's."""
        updates = []
        for k, item in self.store.items():
            peer_ver = peer_digest.get(k, 0)
            if item.version > peer_ver:
                updates.append(item.to_dict())
        return updates

    def merge_updates(self, updates: List[Dict[str, Any]]) -> int:
        """Merge updates from peer, keeping highest version."""
        applied = 0
        for u in updates:
            k = u["key"]
            ver = u["version"]
            curr = self.store.get(k)
            if curr is None or ver > curr.version:
                item = StateItem(k, u["value"], ver, u["origin"])
                item.timestamp = u.get("timestamp", time.time())
                self.store[k] = item
                applied += 1
        return applied


class GossipNetwork:
    def __init__(self, node_count: int, fanout: int = 2):
        self.fanout = fanout
        self.nodes: Dict[str, GossipNode] = {}
        node_ids = [f"agent-{i:02d}" for i in range(node_count)]
        for nid in node_ids:
            self.nodes[nid] = GossipNode(nid)
        # Establish peer connections
        for nid in node_ids:
            self.nodes[nid].peers = [p for p in node_ids if p != nid]

    def run_round(self) -> int:
        """Simulate one push-pull gossip round across all nodes."""
        total_applied = 0
        for nid, node in self.nodes.items():
            if not node.peers:
                continue
            # Select random peers based on fanout
            targets = random.sample(node.peers, min(self.fanout, len(node.peers)))
            for target_id in targets:
                peer = self.nodes[target_id]
                # Pull: node inspects peer digest
                peer_digest = peer.get_digest()
                updates_for_node = peer.prepare_diff(node.get_digest())
                total_applied += node.merge_updates(updates_for_node)

                # Push: peer inspects node digest
                updates_for_peer = node.prepare_diff(peer_digest)
                total_applied += peer.merge_updates(updates_for_peer)
        return total_applied

    def calculate_convergence(self, key: str, expected_value: Any) -> float:
        matching = sum(1 for node in self.nodes.values() if node.store.get(key) and node.store[key].value == expected_value)
        return matching / len(self.nodes)
