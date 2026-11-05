import json

import numpy as np


class EmindPhotonicMaskGenerator:
    """Generate an emind-OS silicon photonics mask specification."""

    def __init__(self, alpha=-0.4, beta=1.2, gamma=0.8):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

        self.A = np.array([
            [0.0, -gamma, beta],
            [gamma, 0.0, -alpha],
            [-beta, alpha, 0.0],
        ])

        self.omega_0 = np.sqrt(alpha**2 + beta**2 + gamma**2)
        if self.omega_0 == 0:
            raise ValueError("alpha, beta, and gamma cannot all be zero")

        self.axis = np.array([alpha, beta, gamma]) / self.omega_0

    def rodrigues_transform(self, theta_rad):
        """Compute a rotation matrix using Rodrigues' formula."""
        K = self.A / self.omega_0
        identity = np.eye(3)
        angle = theta_rad * self.omega_0

        return (
            identity
            + np.sin(angle) * K
            + (1 - np.cos(angle)) * np.dot(K, K)
        )

    def decompose_to_mzi_mesh(self, rotation_matrix):
        """Create a simplified 3x3 rotation-to-MZI mesh decomposition."""
        mzi_layers = []
        Q, _ = np.linalg.qr(rotation_matrix)

        for layer in range(3):
            theta = np.arccos(
                np.clip(Q[layer % 3, layer % 3], -1.0, 1.0)
            )
            phi = np.arctan2(
                Q[layer % 3, (layer + 1) % 3],
                Q[layer % 3, (layer + 2) % 3],
            )
            phi_physical = phi % (2 * np.pi)
            waveguide_gap_nm = int(200 + 100 * (theta / (np.pi / 2)))

            mzi_layers.append({
                "layer_id": layer + 1,
                "type": "MZI_Coupler",
                "theta_rad": round(theta, 4),
                "phi_rad": round(phi_physical, 4),
                "lithography_waveguide_gap_nm": waveguide_gap_nm,
                "thermo_optic_phase_shifter_um": round(phi_physical * 12.5, 2),
            })

        return mzi_layers

    def generate_z8_attractor_lock(self):
        """Generate the Z8 discrete-lock microring resonator array."""
        z8_array = []
        radius_um = 5.0

        for attractor_id in range(8):
            phase_target = 2 * np.pi * attractor_id / 8
            radius_variation_nm = int(12 * np.sin(phase_target))

            z8_array.append({
                "attractor_id": attractor_id,
                "target_phase_rad": round(phase_target, 4),
                "ring_radius_um": radius_um,
                "radius_tuning_nm": radius_variation_nm,
                "coupling_gap_nm": 150,
            })

        return z8_array

    def export_gds_spec(self, filename="emind_photonic_mask.json"):
        """Export the mask specification as a JSON file."""
        print("--- [Emind Hardware Compiler] Starting silicon photonics mask compilation ---")
        print(f"Rotation axis: {self.axis.round(4)}")
        print(f"Characteristic frequency magnitude (Omega_0): {self.omega_0:.4f}")

        rotation_matrix = self.rodrigues_transform(theta_rad=np.pi / 4)
        print(f"\nSO(3) rotation matrix R(theta):\n{np.round(rotation_matrix, 3)}")

        spec = {
            "architecture": "Silicon Jade Cong - emind Kernel v0.2",
            "fabrication_nodes": "Silicon Photonics (SOI 220nm)",
            "origin_structure": "Zhi-Grating (Center Aligned)",
            "math_core": {
                "matrix_A": self.A.tolist(),
                "rotation_matrix_R": rotation_matrix.tolist(),
                "rodrigues_axis": self.axis.tolist(),
            },
            "photonic_mesh": {
                "type": "Reck_MZI_Mesh_3x3",
                "layers": self.decompose_to_mzi_mesh(rotation_matrix),
            },
            "z8_lock_ring": {
                "type": "Microring_Resonator_Array",
                "attractors": self.generate_z8_attractor_lock(),
            },
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(spec, file, indent=2, ensure_ascii=False)

        print(f"\nMask specification exported: {filename}")


if __name__ == "__main__":
    generator = EmindPhotonicMaskGenerator(alpha=-0.4, beta=1.2, gamma=0.8)
    generator.export_gds_spec("emind_silicon_jade_cong_layout.json")
