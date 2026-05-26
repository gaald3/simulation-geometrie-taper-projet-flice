# Simulation FEM - Taper Fibre Optique

Simulation de l'effet de différentes géométries de Taper à la sortie d'une fibre optique sur la transmission et les pertes. Modélisation par éléments finis appliquant les équations de Maxwell.

## 📋 Vue d'ensemble

Ce projet implémente un solveur FEM (Finite Element Method) complet pour simuler la propagation des modes lumineux à travers un **taper effilé en fibre optique SMF28**. Les simulations permettent de :

- **Générer différents profils de taper** : linéaire, parabolique, exponentiel, photonic wire bonds
- **Créer un maillage adaptatif** avec Gmsh
- **Résoudre l'équation de Helmholtz 2D axisymétrique** pour trouver les modes guidés
- **Calculer la transmission et les pertes optiques**
- **Comparer les performances** de différentes géométries

## 🎯 Objectifs de la simulation

Le projet vise à optimiser la géométrie du taper pour :
- **Minimiser les pertes radiatives** lors du couplage d'une fibre SMF28 (8.5 µm) vers une structure silicium (1-5 µm)
- **Maximiser l'adiabaticité** du profil pour réduire les pertes de transition
- **Trouver la géométrie optimale** pour l'insertion dans des circuits photoniques intégrés (PIC)

## 📊 Paramètres physiques

### Fibre SMF28
- **Longueur d'onde** : 1550 nm (Bande C - télécommunications)
- **Gaine** : diamètre 125 µm, n ≈ 1.439
- **Cœur** : diamètre 8.5 µm, n ≈ 1.444
- **Indice de contraste** : Δn ≈ 0.005

### Taper
- **Longueur mécanique** : jusqu'à 200 µm
- **Diamètre initial** : 8.5 µm (cœur de la fibre)
- **Diamètre final** : 1-5 µm (pour insertion PIC silicium)
- **Profils testés** : linéaire, parabolique, exponentiel, complexe (photonic wire bonds)

## 🏗️ Structure du projet

```
simulation-geometrie-taper-projet-flice/
├── src/
│   ├── __init__.py           # Package principal
│   ├── config.py             # Configuration des paramètres physiques
│   ├── geometry.py           # Génération des géométries de taper
│   ├── meshing.py            # Maillage FEM avec Gmsh
│   ├── fem_solver.py         # Solveur FEM (équation de Helmholtz)
│   └── analysis.py           # Post-traitement et comparaison
├── tests/
│   └── examples.py           # 5 exemples d'utilisation
├── output/                   # Résultats et visualisations
├── main.py                   # Script principal de lancement
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip ou conda

### Installation rapide

1. **Cloner le repository**
```bash
git clone <repo_url>
cd simulation-geometrie-taper-projet-flice
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

**Note** : Gmsh sera installé automatiquement par pip. Si vous utilisez macOS et avez des problèmes :
```bash
pip install --upgrade gmsh
```

## 💻 Utilisation

### Lancer une simulation complète

```bash
python main.py
```

### Simuler des profils spécifiques

```bash
# Profils linéaire et parabolique uniquement
python main.py --profile linear parabolic

# Tous les profils disponibles
python main.py --profile all

# Profil exponentiel uniquement
python main.py --profile exponential
```

### Options supplémentaires

```bash
# Sans affichage des graphiques
python main.py --no-plot

# Sans rapport HTML
python main.py --no-html

# Répertoire de sortie personnalisé
python main.py --output ./mes_resultats/

# Mode verbeux
python main.py --verbose
```

### Exemples de code

```bash
# Exécuter des exemples d'utilisation
python tests/examples.py --example 1    # Géométries
python tests/examples.py --example 2    # Maillage
python tests/examples.py --example 3    # FEM
python tests/examples.py --example 4    # Comparaison
python tests/examples.py --example 5    # Simulation personnalisée

# Tous les exemples
python tests/examples.py --all
```

## 📈 Résultats et sorties

Après une simulation, vous obtiendrez :

### Fichiers générés
- `geometry_*.png` : Visualisation des profils de taper
- `mesh_*.msh` : Maillage au format Gmsh
- `comparison_results.png` : Graphiques comparatifs
- `results_comparison.csv` : Tableau des résultats (CSV)
- `report.html` : Rapport complet en HTML

### Métriques calculées

Pour chaque profil de taper :

| Métrique | Description |
|----------|-------------|
| **Transmission** | Fraction de puissance transmise (0-100%) |
| **Pertes** | Atténuation en décibels (dB) |
| **Adiabaticité** | Mesure de la progressivité du rétrécissement |
| **Gradient max** | Pente maximale (dR/dz) |
| **Nombre de modes** | Modes optiques guidés dans le taper |

## 🔧 Architecture technique

### Modules

#### `config.py`
Configuration centralisée des paramètres physiques et numériques.
```python
from src.config import PhysicalParameters, TaperProfile

# Accéder aux paramètres
wavelength = PhysicalParameters.wavelength  # 1550 nm
n_core = PhysicalParameters.n_core          # 1.444
```

#### `geometry.py`
Génération des profils de taper et calcul de l'adiabaticité.
```python
from src.geometry import TaperGeometry

geom = TaperGeometry(profile_type="parabolic")
z, r = geom.generate_profile()
adiab, slope = geom.get_adiabaticty()
```

#### `meshing.py`
Création du maillage 2D axisymétrique avec Gmsh.
```python
from src.meshing import MeshGenerator

mesher = MeshGenerator(geom, profile_name="test")
mesher.create_2d_axisymmetric_mesh()
mesh_data = mesher.extract_mesh_data()
```

#### `fem_solver.py`
Solveur FEM pour l'équation de Helmholtz et calcul des modes.
```python
from src.fem_solver import FEMSolver2D, FieldCalculator

solver = FEMSolver2D(mesh_data)
solver.assemble_matrices()
eigenvalues, modes = solver.solve_eigenvalue_problem(n_modes=3)

calc = FieldCalculator(solver)
transmission = calc.calculate_transmission()
```

#### `analysis.py`
Post-traitement, comparaison et rapport des résultats.
```python
from src.analysis import SimulationRunner, ReportGenerator

runner = SimulationRunner(profile_types=["linear", "parabolic"])
runner.run_all_simulations()
runner.print_comparison_table()
runner.plot_comparison()
```

## 📚 Équations utilisées

### Équation de Helmholtz (2D axisymétrique)

Pour une fibre optique avec symétrie cylindrique :

$$\nabla^2 E + n^2 k_0^2 E = 0$$

Où :
- $n$ = indice optique du matériau
- $k_0 = 2\pi/\lambda$ = nombre d'onde dans le vide
- $E$ = champ électrique

En coordonnées cylindriques $(r, \phi, z)$ avec symétrie azimutale :

$$\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial E}{\partial r}\right) + \frac{\partial^2 E}{\partial z^2} + n^2 k_0^2 E = 0$$

### Paramètre d'adiabaticité

$$A = \frac{1}{n_{eff}^2 k_0 \left|\frac{dR}{dz}\right|_{max}}$$

- $A >> 1$ : Transition adiabatique (faibles pertes)
- $A << 1$ : Transition abrupte (fortes pertes radiatives)

## 🔬 Cas d'application

Ce code est adapté pour :
- Concevoir des **tapers pour couplage de modes**
- Optimiser les **photonic mode converters**
- Étudier le **transfert adiabatique de population**
- Analyser les **pertes radiatives** dans les tapers effilés
- Dimensionner les **interfaces fibre-PIC**

## ⚙️ Paramétrage avancé

### Modifier les paramètres physiques

Éditez `src/config.py` :

```python
# Changer la longueur d'onde
PhysicalParameters.wavelength = 1310e-9  # 1310 nm

# Changer les diamètres du taper
PhysicalParameters.taper_diameter_initial = 10e-6
PhysicalParameters.taper_diameter_final = 1e-6

# Augmenter la longueur du taper
PhysicalParameters.taper_length = 300e-6
```

### Affiner le maillage

```python
# Plus fin (plus lent mais plus précis)
NumericalParameters.mesh_element_size_core = 0.05e-6

# Plus grossier (plus rapide)
NumericalParameters.mesh_element_size_core = 0.2e-6
```

## 🐛 Dépannage

### Erreur "gmsh not found"
```bash
pip install --upgrade gmsh
```

### Simulation très lente
- Réduire la taille du maillage dans `config.py`
- Réduire le nombre de modes à calculer
- Utiliser un domaine de calcul plus petit

### Maillage dégénéré
- Augmenter la tolérance de génération du maillage
- Vérifier que le profil du taper ne s'auto-intersecte pas

## 📖 Références

- **Lumerical** : Soft commercial de simulation FEM (inspiration pour l'interface)
- **Gmsh** : https://gmsh.info/ - Mailleur open-source
- **SciPy** : Solveurs creux et eigenvalue
- **Équations de Maxwell** : Jackson, Classical Electrodynamics

## 👥 Auteurs

- Équipe FLISE (Fibre Laser et Ingénierie Système Émetteur)

## 📝 Licence

MIT License - Voir LICENSE pour les détails

## 🤝 Contribution

Les contributions sont bienvenues ! Merci de :
1. Fork le projet
2. Créer une branche pour votre feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📧 Support

Pour toute question ou problème, veuillez ouvrir une **Issue** sur le repository.

---

**Version** : 0.1.0  
**Dernière mise à jour** : Mai 2026
