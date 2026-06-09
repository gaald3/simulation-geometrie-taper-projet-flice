"""
Configuration des paramètres physiques et numériques de la simulation FEM Taper
"""

import numpy as np

# ============================================================================
# PARAMÈTRES PHYSIQUES
# ============================================================================

class PhysicalParameters:
    """Paramètres physiques de la fibre SMF28 et du taper"""
    
    # Longueur d'onde
    wavelength = 1550e-9  # m (1550 nm - Bande C)
    omega = 2 * np.pi * 3e8 / wavelength  # Pulsation
    k0 = 2 * np.pi / wavelength  # Nombre d'onde dans le vide
    
    # Fibre SMF28
    fiber_cladding_diameter = 125e-6  # m (125 µm)
    fiber_cladding_radius = fiber_cladding_diameter / 2
    n_cladding = 1.4440  # Indice de la gaine (SMF-28 @ 1550nm)
    
    fiber_core_diameter = 8.5e-6  # m (8.5 µm)
    fiber_core_radius = fiber_core_diameter / 2
    n_core = 1.4492  # Indice du cœur (SMF-28 @ 1550nm)
    
    # Taper
    taper_length = 200e-6  # m (200 µm max)
    taper_diameter_initial = 8.5e-6  # m (égal au cœur initial)
    taper_diameter_final = 2e-6  # m (à ajuster entre 1-5 µm)
    taper_radius_final = taper_diameter_final / 2
    
    # Air dans le taper
    n_air = 1.0000


class NumericalParameters:
    """Paramètres numériques pour la FEM"""
    
    # Maillage
    mesh_element_size_core = 1.0e-6  # m (1 µm) - Maillage rapide ~1000 éléments
    mesh_element_size_cladding = 2.0e-6  # m (2 µm) - Plus large en gaine
    mesh_element_size_far_field = 5e-6  # m (5 µm) - Région lointaine
    
    # Domaine de calcul
    pml_thickness = 10e-6  # m (épaisseur de la couche absorbante PML)
    pml_strength = 1e2  # Force d'atténuation du PML
    
    # Résolution FEM
    polynomial_degree = 2  # Degré des polynômes d'interpolation (P1, P2, etc.)
    
    # Paramètres d'itération
    max_iterations = 1000
    tolerance = 1e-6


class TaperProfile:
    """Différents profils de taper à explorer"""
    
    @staticmethod
    def linear(z, z_max, r_initial, r_final):
        """Cône linéaire simple"""
        return r_initial - (r_initial - r_final) * (z / z_max)
    
    @staticmethod
    def parabolic(z, z_max, r_initial, r_final):
        """Profil parabolique (plus adiabatique)"""
        normalized_z = z / z_max
        return r_initial - (r_initial - r_final) * normalized_z**2
    
    @staticmethod
    def exponential(z, z_max, r_initial, r_final):
        """Profil exponentiel (encore plus adiabatique)"""
        normalized_z = z / z_max
        exp_factor = np.exp(-3 * normalized_z)
        return r_final + (r_initial - r_final) * exp_factor
    
    @staticmethod
    def sigmoidal(z, z_max, r_initial, r_final):
        """
        Profil sigmoidal en forme de S (transition lisse et progressive)
        Plus adiabatique que linéaire, utile pour réduire les pertes
        """
        normalized_z = z / z_max
        # Fonction sigmoïde centrée au milieu, raideur k=10
        k = 10.0  # Contrôle la raideur de la transition
        z_mid = 0.5
        sigmoid = 1.0 / (1.0 + np.exp(-k * (normalized_z - z_mid)))
        return r_initial - (r_initial - r_final) * sigmoid

    @staticmethod
    def photonic_wire_bond(z, z_max, r_initial, r_final):
        """
        Profil complexe avec goulot et légère redilation
        (style photonic wire bonds)
        """
        normalized_z = z / z_max
        # Phase 1 : rétrécissement rapide (0 à 0.7*z_max)
        # Phase 2 : goulot fin (0.7 à 0.85*z_max)
        # Phase 3 : légère redilation (0.85 à 1.0*z_max)
        
        if normalized_z < 0.7:
            return r_initial - (r_initial - r_final * 0.9) * (normalized_z / 0.7)**2
        elif normalized_z < 0.85:
            plateau_z = (normalized_z - 0.7) / 0.15
            return r_final * 0.9 - r_final * 0.4 * plateau_z
        else:
            final_z = (normalized_z - 0.85) / 0.15
            return r_final * 0.5 + r_final * 0.5 * np.sin(final_z * np.pi / 2)


# ============================================================================
# PARAMÈTRES DE SORTIE ET VISUALISATION
# ============================================================================

class OutputParameters:
    """Paramètres pour la visualisation et export"""
    
    output_dir = "./output/"
    save_mesh = True
    save_fields = True
    plot_geometry = True
    plot_modes = True
    plot_transmission = True
