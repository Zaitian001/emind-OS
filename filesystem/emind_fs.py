import hashlib
import json
import time

class EmindFileSystem:
    def __init__(self, observer_origin=(0.0, 0.0, 0.0)):
        """emind-FS: 基于观测原点的几何记忆管理"""
        self.origin = observer_origin
        self.storage_volume = {}
        
    def generate_geometric_salt(self, attractor_id, tau_Ji):
        salt_str = f"origin:{self.origin}|attractor:{attractor_id}|tau:{tau_Ji}"
        return salt_str

    def write_memory(self, content, attractor_id, tau_Ji=0.1):
        salt = self.generate_geometric_salt(attractor_id, tau_Ji)
        raw_payload = f"{salt}::content::{content}".encode('utf-8')
        geo_hash = hashlib.sha256(raw_payload).hexdigest()
        
        memory_block = {
            "geo_hash": geo_hash,
            "origin": self.origin,
            "attractor_id": attractor_id,
            "content": content,
            "timestamp": time.time(),
            "salt_used": salt
        }
        
        self.storage_volume[geo_hash] = memory_block
        print(f"💾 [emind-FS] 记忆已固化。哈希: {geo_hash[:16]}... (吸引子 {attractor_id})")
        return geo_hash

    def read_by_attractor(self, attractor_id):
        recalled_memories = []
        for block in self.storage_volume.values():
            if block["attractor_id"] == attractor_id:
                recalled_memories.append(block["content"])
        return recalled_memories

if __name__ == "__main__":
    fs = EmindFileSystem(observer_origin=(1.2, -0.8, 0.4))
    fs.write_memory("地球是圆的。", attractor_id=3, tau_Ji=0.15)
    fs.write_memory("F = G(m1m2)/r^2", attractor_id=3, tau_Ji=0.12)
    fs.write_memory("星垂平野阔。", attractor_id=7, tau_Ji=0.20)
    print("\n--- 触发认知检索 (Attractor 3) ---")
    for mem in fs.read_by_attractor(3):
        print(f" -> 召回: {mem}")
