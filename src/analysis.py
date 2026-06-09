"""
Module d'analyse - Post-traitement et comparaison des résultats FEM
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .config import PhysicalParameters as Phys, OutputParameters
from .geometry import TaperGeometry, DomainBuilder
from .meshing import MeshGenerator
from .fem_solver import FEMSolver2D, FieldCalculator


class SimulationRunner:
    """Classe orchestrant la simulation complète"""
    
    def __init__(self, profile_types=None):
        """
        Initialise le runner de simulation
        
        Parameters:
        -----------
        profile_types : list, optional
            Liste des types de profils à simuler
        """
        if profile_types is None:
            profile_types = ["linear", "parabolic", "exponential"]
        
        self.profile_types = profile_types
        self.results = {}
        
        # Créer le répertoire de sortie
        Path(OutputParameters.output_dir).mkdir(exist_ok=True)
    
    def run_single_simulation(self, profile_type, verbose=True):
        """
        Lance une simulation pour un profil donné
        
        Parameters:
        -----------
        profile_type : str
            Type de profil ("linear", "parabolic", etc.)
        verbose : bool
            Afficher les détails
        
        Returns:
        --------
        result : dict
            Dictionnaire avec les résultats de la simulation
        """
        print(f"\n{'='*70}")
        print(f"SIMULATION: Profil {profile_type.upper()}")
        print(f"{'='*70}")
        
        # 1. GÉOMÉTRIE
        geom = TaperGeometry(profile_type=profile_type)
        geom.generate_profile(n_points=300)
        
        domain = DomainBuilder(geom)
        domain.print_summary()
        
        if OutputParameters.plot_geometry:
            geom.plot_geometry(save=True)
        
        # 2. MAILLAGE
        print("\n" + "-"*70)
        print("ÉTAPE 1: Génération du maillage")
        print("-"*70)
        
        mesher = MeshGenerator(geom, profile_name=profile_type)
        mesher.create_2d_axisymmetric_mesh()
        mesh_data = mesher.extract_mesh_data()
        mesher.get_mesh_statistics(mesh_data)
        
        if OutputParameters.save_mesh:
            mesher.save_mesh()
        
        # 3. FEM SOLVER
        print("\n" + "-"*70)
        print("ÉTAPE 2: Résolution FEM")
        print("-"*70)
        
        # Passer la géométrie du taper au solveur pour la distinction air/cœur/gaine
        solver = FEMSolver2D(mesh_data, taper_geometry=geom)
        solver.assemble_matrices()
        solver.apply_boundary_conditions()
        
        eigenvalues, eigenvectors = solver.solve_eigenvalue_problem(n_modes=3)
        
        # 4. CALCUL DES CHAMPS ET TRANSMISSION
        print("\n" + "-"*70)
        print("ÉTAPE 3: Calcul des propriétés optiques")
        print("-"*70)
        
        calc = FieldCalculator(solver)
        transmission = calc.calculate_transmission()
        loss_dB = calc.calculate_loss_dB()
        
        print(f"Transmission:              {transmission*100:.2f}%")
        print(f"Pertes:                    {loss_dB:.2f} dB")
        
        # 5. COMPILATION DES RÉSULTATS
        geom_info = geom.get_domain_info()
        
        result = {
            'profile_type': profile_type,
            'geometry': geom_info,
            'mesh': {
                'n_nodes': mesh_data['n_nodes'],
                'n_elements': mesh_data['n_elements'],
            },
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'transmission': transmission,
            'loss_dB': loss_dB,
            'solver': solver,
            'calculator': calc,
            'mesher': mesher,
        }
        
        mesher.finalize()
        
        return result
    
    def run_all_simulations(self):
        """Lance les simulations pour tous les profils"""
        for profile in self.profile_types:
            try:
                self.results[profile] = self.run_single_simulation(profile)
            except Exception as e:
                print(f"✗ Erreur dans la simulation {profile}: {e}")
                import traceback
                traceback.print_exc()
        
        return self.results
    
    def print_comparison_table(self):
        """Affiche un tableau comparatif des résultats"""
        if not self.results:
            print("Aucun résultat disponible. Lancez les simulations d'abord.")
            return
        
        print("\n" + "="*100)
        print("TABLEAU COMPARATIF DES RÉSULTATS")
        print("="*100)
        
        # En-têtes
        print(f"{'Profil':<20} | {'Adiab.':<10} | {'Gradient':<12} | {'Transmission':<14} | {'Pertes':<10}")
        print("-"*100)
        
        for profile, result in self.results.items():
            geom_info = result['geometry']
            adiab = geom_info['adiabaticity']
            gradient = geom_info['max_slope']
            trans = result['transmission']
            loss = result['loss_dB']
            
            print(f"{profile:<20} | {adiab:<10.2e} | {gradient:<12.4f} | {trans*100:>12.2f}% | {loss:>8.2f} dB")
        
        print("="*100 + "\n")
    
    def plot_comparison(self, save=False):
        """
        Crée des graphiques comparatifs
        
        Parameters:
        -----------
        save : bool
            Si True, sauvegarde les figures
        """
        if not self.results:
            print("Aucun résultat disponible.")
            return
        
        profiles = list(self.results.keys())
        transmissions = [self.results[p]['transmission'] for p in profiles]
        losses = [self.results[p]['loss_dB'] for p in profiles]
        adiabatics = [self.results[p]['geometry']['adiabaticity'] for p in profiles]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Transmission
        colors = plt.cm.viridis(np.linspace(0, 1, len(profiles)))
        ax1.bar(profiles, transmissions, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Transmission (%)', fontsize=11)
        ax1.set_title('Transmission en fonction du profil', fontsize=12, fontweight='bold')
        ax1.set_ylim([0, 1])
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Pertes
        ax2.bar(profiles, losses, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Pertes (dB)', fontsize=11)
        ax2.set_title('Pertes optiques en fonction du profil', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Adiabaticité
        ax3.bar(profiles, adiabatics, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax3.set_ylabel('Adiabaticité', fontsize=11)
        ax3.set_title('Adiabaticité du taper', fontsize=12, fontweight='bold')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3, axis='y', which='both')
        
        # 4. Synthèse: Transmission vs Adiabaticité
        for i, profile in enumerate(profiles):
            ax4.scatter(adiabatics[i], transmissions[i]*100, s=200, 
                       color=colors[i], label=profile, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax4.set_xlabel('Adiabaticité (log scale)', fontsize=11)
        ax4.set_ylabel('Transmission (%)', fontsize=11)
        ax4.set_title('Transmission vs Adiabaticité', fontsize=12, fontweight='bold')
        ax4.set_xscale('log')
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        
        if save:
            filename = f"{OutputParameters.output_dir}comparison_results.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✓ Comparaison sauvegardée: {filename}")
        
        plt.show()
    
    def export_results_to_csv(self, filename=None):
        """
        Exporte les résultats en CSV
        
        Parameters:
        -----------
        filename : str, optional
            Chemin du fichier de sortie
        """
        if not self.results:
            print("Aucun résultat à exporter.")
            return
        
        if filename is None:
            filename = f"{OutputParameters.output_dir}results_comparison.csv"
        
        # Préparer les données
        data = []
        for profile, result in self.results.items():
            geom_info = result['geometry']
            row = {
                'Profil': profile,
                'Longueur_um': geom_info['taper_length'],
                'Diametre_initial_um': geom_info['initial_diameter'],
                'Diametre_final_um': geom_info['final_diameter'],
                'Longueur_onde_nm': geom_info['wavelength'],
                'n_ceur': geom_info['n_core'],
                'n_gaine': geom_info['n_cladding'],
                'Adiabaticite': geom_info['adiabaticity'],
                'Gradient_max': geom_info['max_slope'],
                'Transmission': result['transmission'],
                'Transmission_percent': result['transmission']*100,
                'Pertes_dB': result['loss_dB'],
                'N_noeuds': result['mesh']['n_nodes'],
                'N_elements': result['mesh']['n_elements'],
            }
            data.append(row)
        
        # Écrire le CSV
        import csv
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
        
        print(f"✓ Résultats exportés: {filename}")


class ReportGenerator:
    """Génère un rapport d'analyse détaillé"""
    
    def __init__(self, simulation_runner):
        """
        Initialise le générateur de rapport
        
        Parameters:
        -----------
        simulation_runner : SimulationRunner
            Objet contenant les résultats des simulations
        """
        self.runner = simulation_runner
    
    def generate_html_report(self, filename=None):
        """
        Génère un rapport HTML complet
        
        Parameters:
        -----------
        filename : str, optional
            Chemin du fichier de sortie
        """
        if not self.runner.results:
            print("Aucun résultat disponible pour générer un rapport.")
            return
        
        if filename is None:
            filename = f"{OutputParameters.output_dir}report.html"
        
        html = self._generate_html_content()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Rapport HTML généré: {filename}")
    
    def _generate_html_content(self):
        """Génère le contenu HTML du rapport"""
        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rapport FEM - Simulation Taper Fibre Optique</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
                h1 { color: #2c3e50; text-align: center; }
                h2 { color: #34495e; margin-top: 30px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; background: white; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #3498db; color: white; }
                tr:hover { background-color: #f2f2f2; }
                .success { color: #27ae60; }
                .warning { color: #f39c12; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Rapport FEM - Simulation Taper Fibre Optique SMF28</h1>
                <p><strong>Date:</strong> """ + str(np.datetime64('today')) + """</p>
                <p><strong>Longueur d'onde:</strong> """ + str(int(Phys.wavelength*1e9)) + """ nm</p>
        """
        
        # Tableau des résultats
        html += """
                <h2>Résultats des Simulations</h2>
                <table>
                    <tr>
                        <th>Profil</th>
                        <th>Transmission (%)</th>
                        <th>Pertes (dB)</th>
                        <th>Adiabaticité</th>
                        <th>Gradient Max</th>
                    </tr>
        """
        
        for profile, result in self.runner.results.items():
            geom_info = result['geometry']
            html += f"""
                    <tr>
                        <td><strong>{profile}</strong></td>
                        <td><span class="success">{result['transmission']*100:.2f}%</span></td>
                        <td>{result['loss_dB']:.2f}</td>
                        <td>{geom_info['adiabaticity']:.2e}</td>
                        <td>{geom_info['max_slope']:.4f}</td>
                    </tr>
            """
        
        html += """
                </table>
                <h2>Conclusion</h2>
                <p>Les simulations FEM ont permis d'évaluer les performances optiques de différents profils de taper.</p>
                <p>Les profils plus adiabatiques (parabolique, exponentiel) montrent généralement une meilleure transmission
                   avec moins de pertes radiatives.</p>
            </div>
        </body>
        </html>
        """
        
        return html


if __name__ == "__main__":
    # Exemple d'utilisation
    runner = SimulationRunner(profile_types=["linear", "parabolic", "exponential"])
    
    print("\n" + "="*70)
    print("LANCEMENT DES SIMULATIONS FEM")
    print("="*70)
    
    runner.run_all_simulations()
    
    # Afficher les résultats
    runner.print_comparison_table()
    runner.plot_comparison(save=True)
    runner.export_results_to_csv()
    
    # Générer un rapport
    report = ReportGenerator(runner)
    report.generate_html_report()
    
    print("\n✓ Simulations terminées avec succès!")
