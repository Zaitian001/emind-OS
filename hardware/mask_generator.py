import numpy as np

class EmindPhotonicMaskGenerator:
    """
    emind-OS 硬件底座：硅光 MZI 拓扑逆向设计生成器
    将公式 (1) 的 A 矩阵映射为硅光芯片波导的物理参数
    """
    def __init__(self, alpha=-0.4, beta=1.2, gamma=0.8):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        # 构建公式 (1) 的 skew-symmetric 矩阵 A
        self.A = np.array([
            [0.0, -gamma, beta],
            [gamma, 0.0, -alpha],
            [-beta, alpha, 0.0]
        ])
        
    def decompose_to_mzi_parameters(self):
        """
        将反对称矩阵 A 映射为光子芯片中的 MZI 相位与耦合系数
        """
        print("--- [Emind Hardware Compiler] 正在进行硅光拓扑逆向映射 ---")
        
        # 1. 计算罗德里格斯旋转轴与旋转模长 (公式 4)
        omega_0 = np.sqrt(self.alpha**2 + self.beta**2 + self.gamma**2)
        axis = np.array([self.alpha, self.beta, self.gamma]) / omega_0
        
        print(f"🌀 旋转主轴 (Axis): {axis}")
        print(f"⚡ 特征频率模长 (Omega_0): {omega_0:.4f}")
        
        # 2. 将矩阵非对角线元素映射为波导定向耦合系数 kappa
        # MZI 的分束比由耦合区长度和间距决定
        coupler_coeffs = {
            "kappa_xy": abs(self.gamma),  # 对应 -0.8 / 0.8
            "kappa_yz": abs(self.alpha),  # 对应 1.2 / -1.2 (归一化)
            "kappa_zx": abs(self.beta)    # 对应 0.4 / -0.4
        }
        
        # 3. 生成虚拟 GDSII 掩膜版坐标描述
        gds_layout = []
        for key, kappa in coupler_coeffs.items():
            # 物理转换：耦合系数 kappa 决定波导间距 gap (纳米级)
            waveguide_gap_nm = max(100, int(500 * (1.0 - kappa)))
            gds_layout.append({
                "component": f"MZI_Coupler_{key}",
                "target_kappa": kappa,
                "lithography_gap_nm": waveguide_gap_nm,
                "phase_shift_rad": omega_0
            })
            
        return gds_layout

    def export_mask_spec(self, filename="emind_silicon_cong_mask.json"):
        """导出流片掩膜版规格书"""
        layout_data = self.decompose_to_mzi_parameters()
        spec = {
            "architecture": "Silicon Jade Cong - emind Core",
            "matrix_A": self.A.tolist(),
            "fabrication_nodes": "TSMC 65nm Silicon Photonics",
            "origin_structure": "Zhi-Grating (Center Aligned)",
            "layout_elements": layout_data
        }
        
        import json
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
        print(f"✅ 掩膜版拓扑规格已成功导出至: {filename}")

if __name__ == "__main__":
    # 实例化生成器，输入论文公式 (1) 的核心参数
    generator = EmindPhotonicMaskGenerator(alpha=-0.4, beta=1.2, gamma=0.8)
    generator.export_mask_spec()
