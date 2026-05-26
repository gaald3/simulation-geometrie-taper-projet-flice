"""
Exemples d'utilisation du module FEM Taper
"""

import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.geometry import TaperGeometry, DomainBuilder
from src.meshing import MeshGenerator
from src.fem_solver import FEMSolver2D, FieldCalculator
from src.analysis import SimulationRunner
from src.config import OutputParameters


def example_1_single_geometry():
    """
    Exemple 1: Créer et visualiser une géométrie de taper
    """
    print("\n" + "="*60)
    print("EXEMPLE 1: Géométrie d'un Taper")
    print("="*60)
    
    # Créer une géométrie parabolique
    geom = TaperGeometry(profile_type="parabolic")
    z, r = geom.generate_profile(n_points=500)
    
    # Afficher les infos
    info = geom.get_domain_info()
    print(f"Profil:            {info['profile_type']}")
    print(f"Longueur:          {info['taper_length']:.1f} µm")
    print(f"Diamètre initial:  {info['initial_diameter']:.1f} µm")
    print(f"Diamètre final:    {info['final_diameter']:.1f} µm")
    print(f"Adiabaticité:      {info['adiabaticity']:.2e}")
    
    # Visualiser
    geom.plot_geometry(save=True)


def example_2_mesh_generation():
    """
    Exemple 2: Générer un maillage pour un taper
    """
    print("\n" + "="*60)
    print("EXEMPLE 2: Génération du Maillage")
    print("="*60)
    
    # Créer la géométrie
    geom = TaperGeometry(profile_type="linear")
    geom.generate_profile()
    
    # Générer le maillage
    mesher = MeshGenerator(geom, profile_name="linear_test")
    mesher.create_2d_axisymmetric_mesh()
    
    # Extraire et afficher les données
    mesh_data = mesher.extract_mesh_data()
    mesher.get_mesh_statistics(mesh_data)
    
    # Sauvegarder
    mesher.save_mesh()
    mesher.finalize()


def example_3_fem_solving():
    """
    Exemple 3: Résoudre le problème FEM et trouver les modes
    """
    print("\n" + "="*60)
    print("EXEMPLE 3: Résolution FEM")
    print("="*60)
    
    # Créer la géométrie et le maillage
    geom = TaperGeometry(profile_type="exponential")
    geom.generate_profile()
    
    mesher = MeshGenerator(geom, profile_name="exponential_test")
    mesher.create_2d_axisymmetric_mesh()
    mesh_data = mesher.extract_mesh_data()
    
    # Créer et résoudre le solveur FEM
    solver = FEMSolver2D(mesh_data)
    solver.assemble_matrices()
    solver.apply_boundary_conditions()
    
    eigenvalues, eigenvectors = solver.solve_eigenvalue_problem(n_modes=3)
    
    # Calculer la transmission
    calc = FieldCalculator(solver)
    transmission = calc.calculate_transmission()
    loss_dB = calc.calculate_loss_dB()
    
    print(f"\nTransmission: {transmission*100:.2f}%")
    print(f"Pertes: {loss_dB:.2f} dB")
    
    # Visualiser le premier mode
    if eigenvectors is not None:
        solver.plot_mode(mode_idx=0, save=True, filename=f"{OutputParameters.output_dir}mode_1.png")
    
    mesher.finalize()


def example_4_comparative_analysis():
    """
    Exemple 4: Analyse comparative des différents profils
    """
    print("\n" + "="*60)
    print("EXEMPLE 4: Analyse Comparative")
    print("="*60)
    
    # Créer un runner et lancer toutes les simulations
    runner = SimulationRunner(profile_types=["linear", "parabolic", "exponential"])
    runner.run_all_simulations()
    
    # Afficher les résultats
    runner.print_comparison_table()
    runner.plot_comparison(save=True)
    runner.export_results_to_csv()


def example_5_custom_simulation():
    """
    Exemple 5: Simulation personnalisée avec paramètres modifiés
    """
    print("\n" + "="*60)
    print("EXEMPLE 5: Simulation Personnalisée")
    print("="*60)
    
    from src.config import PhysicalParameters
    
    # Modifier les paramètres
    original_diameter = PhysicalParameters.taper_diameter_final
    
    # Tester différents diamètres finaux
    diameters = [1e-6, 2e-6, 3e-6, 5e-6]
    results = {}
    
    for d in diameters:
        PhysicalParameters.taper_diameter_final = d
        PhysicalParameters.taper_radius_final = d / 2
        
        print(f"\nSimulation pour diamètre final: {d*1e6:.1f} µm")
        
        geom = TaperGeometry(profile_type="parabolic")
        geom.generate_profile()
        
        mesher = MeshGenerator(geom, profile_name=f"parabolic_d{d*1e6:.1f}")
        mesher.create_2d_axisymmetric_mesh()
        mesh_data = mesher.extract_mesh_data()
        
        solver = FEMSolver2D(mesh_data)
        solver.assemble_matrices()
        solver.solve_eigenvalue_problem(n_modes=2)
        
        calc = FieldCalculator(solver)
        transmission = calc.calculate_transmission()
        
        results[d] = transmission
        
        print(f"  Transmission: {transmission*100:.2f}%")
        
        mesher.finalize()
    
    # Restaurer les paramètres
    PhysicalParameters.taper_diameter_final = original_diameter
    PhysicalParameters.taper_radius_final = original_diameter / 2
    
    print("\nRésumé:")
    for d, trans in results.items():
        print(f"  {d*1e6:.1f} µm -> {trans*100:.2f}%")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Exemples d'utilisation du module FEM Taper")
    parser.add_argument('--example', type=int, default=1, choices=[1, 2, 3, 4, 5],
                       help='Numéro de l\'exemple à exécuter')
    parser.add_argument('--all', action='store_true', help='Exécuter tous les exemples')
    
    args = parser.parse_args()
    
    # Créer le répertoire de sortie
    Path(OutputParameters.output_dir).mkdir(exist_ok=True)
    
    if args.all:
        example_1_single_geometry()
        example_2_mesh_generation()
        example_3_fem_solving()
        example_4_comparative_analysis()
        # Exemple 5 est plus long, on peut le sauter par défaut
    else:
        examples = {
            1: example_1_single_geometry,
            2: example_2_mesh_generation,
            3: example_3_fem_solving,
            4: example_4_comparative_analysis,
            5: example_5_custom_simulation,
        }
        examples[args.example]()
    
    print("\n✓ Exemples exécutés avec succès!")
