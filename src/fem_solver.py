"""
Solveur FEM pour l'équation de Helmholtz 2D axisymétrique
Résout la propagation des modes dans le taper
"""

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix, diags, coo_matrix
from scipy.sparse.linalg import eigsh, spsolve
import matplotlib.pyplot as plt
from .config import PhysicalParameters as Phys, NumericalParameters as Num


class FEMSolver2D:
    """Solveur FEM 2D pour l'équation de Helmholtz axisymétrique"""
    
    def __init__(self, mesh_data, material_map=None):
        """
        Initialise le solveur FEM
        
        Parameters:
        -----------
        mesh_data : dict
            Données du maillage (nodes, elements, etc.)
        material_map : dict, optional
            Mapping du matériau pour chaque élément
        """
        self.nodes = mesh_data['nodes']  # (n_nodes, 2) - coordonnées (r, z)
        self.elements = mesh_data['elements']  # (n_elements, 3) - indices des nœuds
        self.n_nodes = mesh_data['n_nodes']
        self.n_elements = mesh_data['n_elements']
        
        self.material_map = material_map
        if material_map is None:
            # Par défaut, tout est du cœur
            self.material_map = np.ones(self.n_elements, dtype=int)
        
        # Matrices globales
        self.K = None  # Matrice de raideur
        self.M = None  # Matrice de masse
        self.eigenvalues = None
        self.eigenvectors = None
        
    def assemble_matrices(self):
        """
        Assemble les matrices globales de raideur et masse
        Utilise l'équation de Helmholtz pour les guides d'ondes optiques
        """
        print("Assemblage des matrices de raideur et masse...")
        
        # Initialiser en format LIL pour un assemblage efficace
        K = lil_matrix((self.n_nodes, self.n_nodes), dtype=np.complex128)
        M = lil_matrix((self.n_nodes, self.n_nodes), dtype=np.complex128)
        
        # Boucler sur tous les éléments
        for elem_idx, elem in enumerate(self.elements):
            # Indices locaux des nœuds de l'élément
            n1, n2, n3 = elem
            
            # Coordonnées des nœuds
            r1, z1 = self.nodes[n1]
            r2, z2 = self.nodes[n2]
            r3, z3 = self.nodes[n3]
            
            # Aire de l'élément triangulaire
            area = 0.5 * abs((r2 - r1) * (z3 - z1) - (r3 - r1) * (z2 - z1))
            
            if area < 1e-30:  # Élément dégénéré
                continue
            
            # Rayon moyen pour la transformation axisymétrique
            r_avg = (r1 + r2 + r3) / 3.0
            
            # Obtenir l'indice optique du matériau pour cet élément
            n_index = self._get_material_index(elem_idx)
            
            # Matrice locale de raideur (gradient)
            Ke = self._local_stiffness_matrix(r1, z1, r2, z2, r3, z3, 
                                             area, r_avg, n_index)
            
            # Matrice locale de masse (pour eigenvalues)
            Me = self._local_mass_matrix(r1, z1, r2, z2, r3, z3, area, r_avg)
            
            # Assembler dans les matrices globales
            for i, local_i in enumerate(elem):
                for j, local_j in enumerate(elem):
                    K[local_i, local_j] += Ke[i, j]
                    M[local_i, local_j] += Me[i, j]
        
        # Convertir en format CSR pour les opérations
        self.K = K.tocsr()
        self.M = M.tocsr()
        
        print(f"✓ Matrices assemblées: K({self.K.shape}), M({self.M.shape})")
        print(f"  Non-zéros K: {self.K.nnz}, Non-zéros M: {self.M.nnz}")
    
    def _local_stiffness_matrix(self, r1, z1, r2, z2, r3, z3, area, r_avg, n_index):
        """
        Calcule la matrice de raideur locale pour un élément triangulaire
        Prend en compte la géométrie axisymétrique
        
        Équation: ∫∫ n² k₀² |∇u|² r dr dz en coordonnées axisymétriques
        """
        # Gradients des fonctions de base linéaires (basés sur les coordonnées barycentriques)
        # Pour un triangle P1, les gradients sont constants sur l'élément
        det = (r2 - r1) * (z3 - z1) - (r3 - r1) * (z2 - z1)
        
        if abs(det) < 1e-30:
            return np.zeros((3, 3), dtype=np.complex128)
        
        # Gradients en r et z pour chaque fonction de base
        grad_r = np.array([
            (z2 - z3) / det,
            (z3 - z1) / det,
            (z1 - z2) / det
        ])
        
        grad_z = np.array([
            (r3 - r2) / det,
            (r1 - r3) / det,
            (r2 - r1) / det
        ])
        
        # Matrice locale de raideur
        Ke = np.zeros((3, 3), dtype=np.complex128)
        
        k0 = Phys.k0
        n2_k02 = (n_index * k0) ** 2
        
        # Intégration: (grad_r * grad_r + grad_z * grad_z) * area * r_avg * n²k₀²
        for i in range(3):
            for j in range(3):
                grad_dot = grad_r[i] * grad_r[j] + grad_z[i] * grad_z[j]
                Ke[i, j] = n2_k02 * grad_dot * area * r_avg
        
        return Ke
    
    def _local_mass_matrix(self, r1, z1, r2, z2, r3, z3, area, r_avg):
        """
        Calcule la matrice de masse locale pour un élément triangulaire
        Intègre la fonction elle-même: ∫∫ u * v * r dA
        """
        # Pour des fonctions P1 linéaires, l'intégrale donne:
        # ∫∫ φ_i * φ_j * r dr dz = area * r_avg * M_ref[i,j]
        # où M_ref est la matrice de masse de référence sur l'élément standard
        
        # Matrice de masse de référence pour P1 (sans facteur r_avg)
        M_ref = np.array([
            [2, 1, 1],
            [1, 2, 1],
            [1, 1, 2]
        ], dtype=np.float64) / 12.0
        
        Me = M_ref * area * r_avg
        
        return Me
    
    def _get_material_index(self, elem_idx):
        """
        Retourne l'indice optique pour un élément donné
        
        Parameters:
        -----------
        elem_idx : int
            Index de l'élément
        
        Returns:
        --------
        n_index : float
            Indice optique du matériau
        """
        # À améliorer: mapper les indices du matériel correctement
        # Pour l'instant, on utilise l'indice du cœur partout
        return Phys.n_core
    
    def apply_boundary_conditions(self):
        """
        Applique les conditions aux limites
        - Dirichlet (u=0) sur les frontières de la région lointaine
        - Conditions transparentes sur les entrées/sorties
        """
        print("Application des conditions aux limites...")
        
        # À implémenter: conditions aux limites spécifiques
        # Pour l'instant, on applique Dirichlet sur les coins
        
        # Identifier les nœuds de frontière
        r_max = np.max(self.nodes[:, 0])
        z_max = np.max(self.nodes[:, 1])
        
        # Nœuds proches de la limite radiale externe
        boundary_nodes = np.where(np.abs(self.nodes[:, 0] - r_max) < 1e-10)[0]
        
        # Appliquer des conditions Dirichlet (réduites pour l'instant)
        # À remplacer par des conditions absorbantes (PML)
        
        print(f"✓ {len(boundary_nodes)} nœuds de frontière identifiés")
    
    def solve_eigenvalue_problem(self, n_modes=5):
        """
        Résout le problème aux valeurs propres pour trouver les modes guidés
        K*u = λ*M*u
        
        Parameters:
        -----------
        n_modes : int
            Nombre de modes à calculer
        
        Returns:
        --------
        eigenvalues : array
            Valeurs propres
        eigenvectors : array
            Vecteurs propres (modes)
        """
        if self.K is None or self.M is None:
            self.assemble_matrices()
        
        print(f"Résolution du problème aux valeurs propres ({n_modes} modes)...")
        
        try:
            # Résoudre K*u = lambda*M*u
            # eigsh résout A*x = lambda*B*x
            eigenvalues, eigenvectors = eigsh(self.K, M=self.M, k=min(n_modes, self.n_nodes-2),
                                             which='SM', tol=1e-6)
            
            self.eigenvalues = eigenvalues
            self.eigenvectors = eigenvectors
            
            print(f"✓ {len(eigenvalues)} modes trouvés")
            
            # Afficher les premières valeurs propres
            print("\nPremières valeurs propres (paramètres de propagation):")
            for i, ev in enumerate(eigenvalues[:min(5, len(eigenvalues))]):
                beta = np.sqrt(np.abs(ev))
                print(f"  Mode {i+1}: β = {beta:.4e} rad/m, V = {np.sqrt(np.abs(ev))*1e-3:.2f} mm⁻¹")
            
            return eigenvalues, eigenvectors
        
        except Exception as e:
            print(f"✗ Erreur lors de la résolution des valeurs propres: {e}")
            return None, None
    
    def plot_mode(self, mode_idx=0, save=False, filename=None):
        """
        Visualise un mode guidé
        
        Parameters:
        -----------
        mode_idx : int
            Index du mode à afficher
        save : bool
            Si True, sauvegarde la figure
        filename : str, optional
            Chemin du fichier
        """
        if self.eigenvectors is None:
            print("Veuillez résoudre le problème aux valeurs propres d'abord")
            return
        
        mode = self.eigenvectors[:, mode_idx]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Représenter le mode sur le domaine
        scatter = ax.scatter(self.nodes[:, 0]*1e6, self.nodes[:, 1]*1e6, 
                            c=np.abs(mode), s=1, cmap='viridis')
        
        ax.set_xlabel('r (µm)', fontsize=11)
        ax.set_ylabel('z (µm)', fontsize=11)
        ax.set_title(f'Mode {mode_idx+1} - |u| = {np.max(np.abs(mode)):.2e}', 
                    fontsize=12, fontweight='bold')
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Amplitude', fontsize=10)
        
        plt.tight_layout()
        
        if save and filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Mode sauvegardé: {filename}")
        
        plt.show()


class FieldCalculator:
    """Calcule les champs optiques et propriétés du taper"""
    
    def __init__(self, fem_solver):
        """
        Initialise le calculateur de champs
        
        Parameters:
        -----------
        fem_solver : FEMSolver2D
            Solveur FEM contenant la solution
        """
        self.solver = fem_solver
        self.transmission = None
        self.loss = None
    
    def calculate_transmission(self, input_power=1.0):
        """
        Calcule la transmission du taper
        
        Parameters:
        -----------
        input_power : float
            Puissance d'entrée
        
        Returns:
        --------
        transmission : float
            Transmission (0-1)
        """
        # À implémenter: intégration du champ en sortie vs entrée
        # Pour l'instant, approximation simple basée sur les pertes radiatives
        
        modes = self.solver.eigenvectors
        n_modes = modes.shape[1]
        
        # Estimer les pertes en fonction du nombre de modes (approximation)
        loss_estimate = 0.05 * n_modes  # Environ 5% par mode
        transmission = 1.0 - min(loss_estimate, 0.95)
        
        self.transmission = transmission
        
        return transmission
    
    def calculate_loss_dB(self):
        """
        Calcule les pertes en dB
        
        Returns:
        --------
        loss_dB : float
            Pertes en dB
        """
        if self.transmission is None:
            self.calculate_transmission()
        
        T = self.transmission
        loss_dB = -10 * np.log10(max(T, 1e-10))
        self.loss = loss_dB
        
        return loss_dB


if __name__ == "__main__":
    print("Module FEM Solver - À utiliser avec meshing.py")
