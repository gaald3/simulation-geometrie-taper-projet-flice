"""
Module de génération des géométries de taper pour la simulation FEM
"""

import numpy as np
import matplotlib.pyplot as plt
from .config import PhysicalParameters as Phys, TaperProfile, OutputParameters


class TaperGeometry:
    """Classe pour gérer la géométrie du taper"""
    
    def __init__(self, profile_type="linear"):
        """
        Initialise la géométrie du taper
        
        Parameters:
        -----------
        profile_type : str
            Type de profil : "linear", "parabolic", "exponential", "photonic_wire_bond"
        """
        self.profile_type = profile_type
        self.z_coords = None
        self.radius_profile = None
        
    def generate_profile(self, n_points=500):
        """
        Génère le profil radial du taper en fonction de z
        
        Parameters:
        -----------
        n_points : int
            Nombre de points pour discrétiser le profil
            
        Returns:
        --------
        z : array
            Positions axiales (m)
        radius : array
            Rayon en fonction de z (m)
        """
        z = np.linspace(0, Phys.taper_length, n_points)
        
        # Sélectionner le profil approprié
        if self.profile_type == "linear":
            radius = TaperProfile.linear(z, Phys.taper_length, 
                                        Phys.fiber_core_radius, 
                                        Phys.taper_radius_final)
        
        elif self.profile_type == "parabolic":
            radius = TaperProfile.parabolic(z, Phys.taper_length,
                                           Phys.fiber_core_radius,
                                           Phys.taper_radius_final)
        
        elif self.profile_type == "exponential":
            radius = TaperProfile.exponential(z, Phys.taper_length,
                                             Phys.fiber_core_radius,
                                             Phys.taper_radius_final)
        
        elif self.profile_type == "sigmoidal":
            radius = TaperProfile.sigmoidal(z, Phys.taper_length,
                                           Phys.fiber_core_radius,
                                           Phys.taper_radius_final)
        
        elif self.profile_type == "photonic_wire_bond":
            radius = np.array([TaperProfile.photonic_wire_bond(zi, Phys.taper_length,
                                                              Phys.fiber_core_radius,
                                                              Phys.taper_radius_final)
                              for zi in z])
        else:
            raise ValueError(f"Profil inconnu: {self.profile_type}")
        
        self.z_coords = z
        self.radius_profile = radius
        
        return z, radius
    
    def get_adiabaticty(self):
        """
        Calcule l'adiabaticité du taper
        Paramètre important pour évaluer les pertes
        
        Returns:
        --------
        adiabaticty : float
            Mesure d'adiabaticité (plus élevé = mieux)
        """
        if self.radius_profile is None:
            self.generate_profile()
        
        # Gradient radial
        dR_dz = np.gradient(self.radius_profile, self.z_coords)
        
        # Paramètre d'adiabaticité: A = (n_eff^2 * k0 * dR/dz)^(-1)
        # Approximation simpifiée: on utilise l'indice du cœur
        n_eff = Phys.n_core
        k0 = Phys.k0
        
        # Valeur maximale de |dR/dz| (transition la plus abrupte)
        max_dR_dz = np.max(np.abs(dR_dz))
        
        # Adiabaticité
        adiabaticity = 1.0 / (n_eff * Phys.k0 * max_dR_dz + 1e-20)
        
        return adiabaticity, max_dR_dz
    
    def get_radius_at_z(self, z_value):
        """
        Retourne le rayon du taper par interpolation linéaire pour une position z donnée
        Utilisée pour déterminer si un point est à l'intérieur ou l'extérieur du taper
        
        Parameters:
        -----------
        z_value : float
            Position axiale (en mètres)
        
        Returns:
        --------
        radius : float
            Rayon du taper à cette position
        """
        if self.radius_profile is None:
            self.generate_profile()
        
        # Interpolation linéaire
        radius = np.interp(z_value, self.z_coords, self.radius_profile)
        
        return radius
    
    def plot_geometry(self, save=False):
        """
        Visualise la géométrie du taper
        
        Parameters:
        -----------
        save : bool
            Si True, sauvegarde la figure
        """
        if self.radius_profile is None:
            self.generate_profile()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Profil du taper
        z_um = self.z_coords * 1e6  # Convertir en µm
        r_um = self.radius_profile * 1e6  # Convertir en µm
        
        ax1.plot(z_um, r_um, 'b-', linewidth=2, label='Rayon du taper')
        ax1.fill_between(z_um, -r_um, r_um, alpha=0.2)
        ax1.set_xlabel('Position axiale z (µm)', fontsize=11)
        ax1.set_ylabel('Rayon r (µm)', fontsize=11)
        ax1.set_title(f'Profil du Taper - {self.profile_type.capitalize()}', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Gradient de rayon (adiabaticité)
        dR_dz = np.gradient(self.radius_profile, self.z_coords)
        
        ax2.plot(z_um, np.abs(dR_dz), 'r-', linewidth=2)
        ax2.set_xlabel('Position axiale z (µm)', fontsize=11)
        ax2.set_ylabel('|dR/dz|', fontsize=11)
        ax2.set_title('Gradient de rayon (abruptité)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            filename = f'{OutputParameters.output_dir}geometry_{self.profile_type}.png'
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Géométrie sauvegardée: {filename}")
        
        plt.show()
    
    def get_domain_info(self):
        """
        Retourne les informations du domaine de simulation
        
        Returns:
        --------
        dict : Dictionnaire avec les infos du domaine
        """
        adiabaticity, max_slope = self.get_adiabaticty()
        
        return {
            'profile_type': self.profile_type,
            'taper_length': Phys.taper_length * 1e6,  # µm
            'initial_diameter': Phys.fiber_core_diameter * 1e6,  # µm
            'final_diameter': Phys.taper_diameter_final * 1e6,  # µm
            'wavelength': Phys.wavelength * 1e9,  # nm
            'n_core': Phys.n_core,
            'n_cladding': Phys.n_cladding,
            'n_air': Phys.n_air,
            'adiabaticity': adiabaticity,
            'max_slope': max_slope,
        }


class DomainBuilder:
    """Classe pour construire le domaine de simulation complet"""
    
    def __init__(self, taper_geometry):
        """
        Initialise le constructeur de domaine
        
        Parameters:
        -----------
        taper_geometry : TaperGeometry
            Objet contenant la géométrie du taper
        """
        self.geometry = taper_geometry
        self.domain_boundaries = None
        
    def build_2d_domain(self):
        """
        Construit le domaine 2D axisymétrique
        (on exploite la symétrie cylindrique)
        
        Returns:
        --------
        dict : Description du domaine 2D
        """
        # En 2D axisymétrique: (r, z)
        domain = {
            'type': '2d_axisymmetric',
            'z_extent': [0, Phys.taper_length],
            'r_extent': [0, max(Phys.fiber_cladding_radius, 
                               Phys.pml_thickness) * 2],
            'regions': {
                'taper': {
                    'material': 'air',
                    'n_index': Phys.n_air,
                    'description': 'Région du taper (air)'
                },
                'surrounding': {
                    'material': 'cladding',
                    'n_index': Phys.n_cladding,
                    'description': 'Gaine autour du taper'
                },
                'pml': {
                    'material': 'pml',
                    'n_index': Phys.n_cladding,
                    'description': 'Couche absorbante (PML)'
                }
            }
        }
        
        return domain
    
    def print_summary(self):
        """Affiche un résumé des paramètres"""
        info = self.geometry.get_domain_info()
        
        print("\n" + "="*60)
        print("RÉSUMÉ DE LA SIMULATION TAPER - FEM")
        print("="*60)
        print(f"Profil du taper:           {info['profile_type'].upper()}")
        print(f"Longueur:                  {info['taper_length']:.1f} µm")
        print(f"Diamètre initial:          {info['initial_diameter']:.1f} µm")
        print(f"Diamètre final:            {info['final_diameter']:.1f} µm")
        print(f"Longueur d'onde:           {info['wavelength']:.0f} nm (Bande C)")
        print(f"\nIndices optiques:")
        print(f"  - Cœur fibre:            {info['n_core']:.4f}")
        print(f"  - Gaine fibre:           {info['n_cladding']:.4f}")
        print(f"  - Air du taper:          {info['n_air']:.4f}")
        print(f"\nAdiabaticité du taper:     {info['adiabaticity']:.2e}")
        print(f"Gradient max (dR/dz):      {info['max_slope']:.4f}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Test des différents profils
    profiles = ["linear", "parabolic", "exponential", "photonic_wire_bond"]
    
    for profile in profiles:
        print(f"\nGénération profil: {profile}")
        geom = TaperGeometry(profile_type=profile)
        geom.generate_profile()
        
        domain = DomainBuilder(geom)
        domain.print_summary()
        
        # geom.plot_geometry(save=True)
