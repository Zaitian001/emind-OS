import torch
import os
import sys
import json

# 确保能够正确导入各个模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 动态引入模块，如果 ui/holographic_display.py 还没有实现，我们内建一个酷炫的 UI 渲染器
try:
    from ui.holographic_display import EmindHolographicUI
except ImportError:
    # 动态补偿未实现的 UI 模块，展示高维吸引子的字符全息图
    class EmindHolographicUI:
        def render_hologram_scene(self, current_attractor_id, memory_fs):
            print(f"   [emind-UI] 💠 正在捕获 Z8 空间共振场 (当前聚焦吸引子: ID {current_attractor_id})...")
            # 打印一个代表 Z8 对称吸引子环的字符矩阵
            z8_hologram = [
                "       [Attractor 0]       ",
                "   [7]               [1]   ",
                " [6]       (0,0,0)       [2] ",
                "   [5]               [3]   ",
                "       [Attractor 4]       "
            ]
            # 标注当前被内核锁定的吸引子状态
            active_tag = f" <--- [LOCKED TARGET AT {current_attractor_id}]"
            for idx, line in enumerate(z8_hologram):
                if f"[{current_attractor_id}]" in line:
                    print("   " + line + active_tag)
                else:
                    print("   " + line)
            print("   [emind-UI] ✨ 全息共振相态投影成功，零幻觉离散空间记录就绪。")

from kernel.scheduler import AdvancedEmindKernelScheduler
from filesystem.emind_fs import EmindFileSystem
from hardware.mask_generator import EmindPhotonicMaskGenerator

def run_emind_pipeline():
    print("="*60)
    print(" 🌌 emind-OS E2E Pipeline: From Cosmic Manifold to Silicon")
    print("="*60)

    # =========================================================
    # 1. 大模型输入 (The Continuous Manifold: O_web)
    # =========================================================
    print("\n[Step 1] 🌐 模拟大语言模型（LLM）输出高维噪声态...")
    llm_hallucination_stream = torch.randn(3, 768) * 3.5
    print(f" -> 接收到 {llm_hallucination_stream.shape[0]} 个 Token，维度 {llm_hallucination_stream.shape[1]}，伴随严重概率漂移。")

    # =========================================================
    # 2. 内核耗散调度 (The Kernel: P_Zhi & Lyapunov Dissipation)
    # =========================================================
    print("\n[Step 2] ⚙️ 注入 emind-Kernel，执行耗散收敛流 (dV/dt <= 0)...")
    kernel = AdvancedEmindKernelScheduler(state_dim=768, num_attractors=8)
    kernel_results = kernel.allocate_emind_process(llm_hallucination_stream)

    # =========================================================
    # 3. 几何文件系统固化 (The File System: Geometric Salt)
    # =========================================================
    print("\n[Step 3] 💾 将稳定后的离散现实 (R_creator) 固化至 emind-FS...")
    observer_origin = (0.0, 9.8, 0.0) # 假设当前重力矢量为 Y 轴 (原点锚定)
    fs = EmindFileSystem(observer_origin=observer_origin)
    
    hashes = []
    for idx, res in enumerate(kernel_results):
        attractor_id = res['attractor_id']
        final_energy = res['energy_trajectory'][-1]
        content = f"Token_{idx} stabilized with residual energy {final_energy:.6f}"
        
        geo_hash = fs.write_memory(content, attractor_id=attractor_id, tau_Ji=0.12)
        hashes.append(geo_hash)

    # =========================================================
    # 4. 硬件光刻编译 (The Hardware: Photonic Mask Generation)
    # =========================================================
    print("\n[Step 4] ⚡ 驱动 emind 硬件编译器，生成流片规格 (Tape-out Spec)...")
    hardware_compiler = EmindPhotonicMaskGenerator(alpha=-0.4, beta=1.2, gamma=0.8)
    mask_filename = "emind_tapeout_spec.json"
    hardware_compiler.export_gds_spec(filename=mask_filename)

    # =========================================================
    # 5. 全息 UI 渲染 (The UI: Holographic Display)
    # =========================================================
    print("\n[Step 5] 🖥️ 激活 emind-UI 全息投影场...")
    ui = EmindHolographicUI()
    current_focus = kernel_results[-1]['attractor_id']
    ui.render_hologram_scene(current_attractor_id=current_focus, memory_fs=fs)

    print("="*60)
    print(" ✅ [emind-OS] 系统闭环执行完毕！")
    print(f" 📁 硬件流片规格书已生成: {os.path.abspath(mask_filename)}")
    print("="*60)

if __name__ == "__main__":
    if os.path.exists("emind_tapeout_spec.json"):
        os.remove("emind_tapeout_spec.json")
        
    run_emind_pipeline()
