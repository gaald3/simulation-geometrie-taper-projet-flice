#!/usr/bin/env python3
"""
Script principal - Lanceur de simulations FEM Taper Fibre Optique

Usage:
    python main.py                  # Lance les simulations par défaut
    python main.py --profile linear # Lance une simulation spécifique
    python main.py --help           # Affiche l'aide
"""

import sys
import argparse
from pathlib import Path

from src.analysis import SimulationRunner, ReportGenerator
from src.config import PhysicalParameters as Phys, OutputParameters


def main():
    """Fonction principale"""
    
    parser = argparse.ArgumentParser(
        description="Simulation FEM des Tapers en Fibre Optique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py                                    # Lance toutes les simulations
  python main.py --profile linear parabolic         # Profils spécifiques
  python main.py --profile all                      # Tous les profils disponibles
  python main.py --no-plot                          # Sans visualisation
  python main.py --output ./resultats/              # Répertoire de sortie
        """
    )
    
    parser.add_argument('--profile', nargs='+', default=['linear', 'parabolic', 'exponential', 'sigmoidal'],
                       help='Profils à simuler (linear, parabolic, exponential, sigmoidal, photonic_wire_bond)')
    parser.add_argument('--output', default=OutputParameters.output_dir,
                       help='Répertoire de sortie')
    parser.add_argument('--no-plot', action='store_true',
                       help='Ne pas afficher les graphiques')
    parser.add_argument('--no-html', action='store_true',
                       help='Ne pas générer le rapport HTML')
    parser.add_argument('--verbose', action='store_true',
                       help='Mode verbeux')
    
    args = parser.parse_args()
    
    # Mise à jour de la configuration
    OutputParameters.output_dir = args.output
    OutputParameters.plot_geometry = not args.no_plot
    OutputParameters.plot_modes = not args.no_plot
    OutputParameters.plot_transmission = not args.no_plot
    
    # Créer le répertoire de sortie
    Path(args.output).mkdir(exist_ok=True)
    
    # Affichage du bannière
    print("\n" + "="*70)
    print("SIMULATION FEM - TAPER FIBRE OPTIQUE SMF28")
    print("="*70)
    print(f"Longueur d'onde:           {Phys.wavelength*1e9:.0f} nm (Bande C)")
    print(f"Fibre:                     SMF28")
    print(f"Taper:                     {Phys.taper_diameter_initial*1e6:.1f} → {Phys.taper_diameter_final*1e6:.1f} µm")
    print(f"Longueur max du taper:     {Phys.taper_length*1e6:.0f} µm")
    print(f"Répertoire de sortie:      {args.output}")
    print("="*70 + "\n")
    
    # Gestion des profils
    profiles = args.profile
    if len(profiles) == 1 and profiles[0].lower() == 'all':
        profiles = ['linear', 'parabolic', 'exponential', 'photonic_wire_bond']
    
    print(f"Profils à simuler: {', '.join(profiles)}\n")
    
    # Créer et lancer le runner de simulations
    runner = SimulationRunner(profile_types=profiles)
    
    try:
        # Lancer les simulations
        runner.run_all_simulations()
        
        # Afficher et exporter les résultats
        print("\n" + "="*70)
        print("RÉSULTATS")
        print("="*70)
        
        runner.print_comparison_table()
        
        if not args.no_plot:
            runner.plot_comparison(save=True)
        
        runner.export_results_to_csv()
        
        # Générer le rapport HTML
        if not args.no_html:
            report = ReportGenerator(runner)
            report.generate_html_report()
        
        print("\n✓ Simulations terminées avec succès!")
        print(f"✓ Les résultats sont disponibles dans: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Simulation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Erreur lors de la simulation: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
