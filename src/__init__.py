"""
Package FEM pour simulation de Tapers en Fibre Optique
======================================================

Modules disponibles:
- config:        Configuration des paramètres physiques et numériques
- geometry:      Génération des géométries de taper
- meshing:       Création du maillage FEM avec Gmsh
- fem_solver:    Solveur FEM pour l'équation de Helmholtz
- analysis:      Post-traitement et comparaison des résultats
"""

__version__ = "0.1.0"
__author__ = "FLISE Simulation Team"

from .config import (
    PhysicalParameters,
    NumericalParameters,
    TaperProfile,
    OutputParameters
)

from .geometry import TaperGeometry, DomainBuilder

from .meshing import MeshGenerator

from .fem_solver import FEMSolver2D, FieldCalculator

from .analysis import SimulationRunner, ReportGenerator

__all__ = [
    'PhysicalParameters',
    'NumericalParameters',
    'TaperProfile',
    'OutputParameters',
    'TaperGeometry',
    'DomainBuilder',
    'MeshGenerator',
    'FEMSolver2D',
    'FieldCalculator',
    'SimulationRunner',
    'ReportGenerator',
]
