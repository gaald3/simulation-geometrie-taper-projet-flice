# 📦 Project Structure - FEM Taper Fibre Optique

## 🗂️ Arborescence complète

```
simulation-geometrie-taper-projet-flice/
│
├── 📄 Documentation
│   ├── README.md                 ← Guide principal complet
│   ├── QUICKSTART.md             ← Démarrage rapide (5 min)
│   ├── TECHNICAL_SUMMARY.md      ← Résumé technique des équations
│   ├── CONTRIBUTING.md           ← Guide de développement
│   └── LICENSE                   ← Licence MIT
│
├── 🐍 Code source principal
│   └── main.py                   ← Script de lancement CLI
│
├── 📚 Package src/ (modules)
│   ├── __init__.py              ← Initialisation du package
│   ├── config.py                ← Paramètres physiques & numériques
│   ├── geometry.py              ← Génération des profils de taper
│   ├── meshing.py               ← Création maillage Gmsh 2D
│   ├── fem_solver.py            ← Solveur FEM (Helmholtz)
│   └── analysis.py              ← Post-traitement et comparaison
│
├── 🧪 Tests & Exemples
│   └── tests/
│       └── examples.py          ← 5 exemples progressifs
│
├── 📊 Répertoire de sortie
│   └── output/                  ← Résultats, images, rapports
│       ├── *.png                (graphiques de géométrie & comparaison)
│       ├── *.csv                (résultats en tableau)
│       ├── *.msh                (maillages Gmsh)
│       ├── *.html               (rapport interactif)
│       └── *.log                (logs de simulation)
│
├── ⚙️ Configuration
│   ├── requirements.txt          ← Dépendances Python
│   └── .gitignore               ← Fichiers à ignorer Git
│
└── 📦 Contrôle de version
    └── .git/                    ← Repository Git
```

## 📄 Description des fichiers principaux

### Documentation

| Fichier | Contenu | Public |
|---------|---------|--------|
| `README.md` | Guide complet, installation, utilisation | Tous |
| `QUICKSTART.md` | Tutoriel 5-10 minutes pour démarrer | Débutants |
| `TECHNICAL_SUMMARY.md` | Équations, physique, paramètres | Chercheurs |
| `CONTRIBUTING.md` | Comment contribuer et développer | Développeurs |
| `LICENSE` | Licence MIT | Légal |

### Code source

| Module | Responsabilité | Classes principales |
|--------|-----------------|-------------------|
| `config.py` | Configuration centralisée | `PhysicalParameters`, `NumericalParameters` |
| `geometry.py` | Géométries de taper | `TaperGeometry`, `DomainBuilder` |
| `meshing.py` | Maillage FEM | `MeshGenerator` |
| `fem_solver.py` | Résolution FEM | `FEMSolver2D`, `FieldCalculator` |
| `analysis.py` | Analyse & rapport | `SimulationRunner`, `ReportGenerator` |

### Tests

| Fichier | Contenu |
|---------|---------|
| `examples.py` | 5 exemples numérotés (1=géométrie à 5=optimization) |

## 🎯 Flux de travail utilisateur

```
START (utilisateur)
  ↓
[Installation: pip install -r requirements.txt]
  ↓
[Choix utilisation]
  ├→ RAPIDE: python main.py (≈2-5 min)
  ├→ DÉTAILLÉ: python tests/examples.py --all (≈10 min)
  └→ PERSONNALISÉ: modifier config.py puis python main.py
  ↓
[Consultation des résultats]
  ├→ output/geometry_*.png (profils)
  ├→ output/comparison_results.png (graphiques)
  ├→ output/results_comparison.csv (données brutes)
  └→ output/report.html (rapport complet)
  ↓
[Analyse & interprétation]
  ├→ Quel profil donne la meilleure transmission ?
  ├→ Quel est le compromis adiabaticité/performance ?
  └→ Modifier paramètres et réitérer
  ↓
END (résultats exploitables)
```

## 🔧 Flux technique interne

```
main.py
  ↓
SimulationRunner.run_all_simulations()
  ├─ Pour chaque profil:
  │   ├→ TaperGeometry.generate_profile()
  │   ├→ DomainBuilder.print_summary()
  │   ├→ MeshGenerator.create_2d_axisymmetric_mesh()
  │   ├→ FEMSolver2D.assemble_matrices()
  │   ├→ FEMSolver2D.solve_eigenvalue_problem()
  │   └→ FieldCalculator.calculate_transmission()
  │
  ├→ SimulationRunner.print_comparison_table()
  ├→ SimulationRunner.plot_comparison()
  ├→ SimulationRunner.export_results_to_csv()
  │
  └→ ReportGenerator.generate_html_report()
  ↓
output/ (fichiers générés)
```

## 📊 Matrice des dépendances

```
main.py
  └── analysis.py
      ├── config.py
      ├── geometry.py
      │   └── config.py
      ├── meshing.py
      │   ├── config.py
      │   └── geometry.py
      └── fem_solver.py
          ├── config.py
          └── [scipy, numpy]

External:
  - gmsh (maillage)
  - numpy (calcul)
  - scipy (algèbre linéaire)
  - matplotlib (visualisation)
```

## 🧪 Cas d'usage validés

✅ **Implémenté et fonctionnel**
- Génération de 4 profils de taper
- Maillage 2D axisymétrique automatique
- Résolution FEM des modes guidés
- Calcul de transmission/pertes
- Comparaison graphique multi-profils
- Export CSV et rapport HTML

🔄 **À développer (v0.2+)**
- Conditions aux limites PML
- Optimisation géométrique automatique
- Simulations 3D complètes
- Interface graphique interactive

## 📈 Tailles typiques

| Aspect | Estimation |
|--------|-----------|
| Code source | ~2000 lignes (bien commentées) |
| Documentation | ~1500 lignes |
| Maillage typique | 3000-5000 nœuds |
| Matrice FEM | 3000×3000 creuse |
| Temps simulation/profil | 1-2 minutes |
| Taille output/profil | 2-5 MB |

## 🎓 Pour comprendre le code

Lecture recommandée dans cet ordre :

1. **QUICKSTART.md** - 5 min - Démarrer immédiatement
2. **README.md** sections "Architecture" - 15 min - Vue d'ensemble
3. **src/config.py** - 10 min - Les paramètres
4. **TECHNICAL_SUMMARY.md** - 20 min - Les équations
5. **src/geometry.py** - 15 min - Génération des géométries
6. **src/meshing.py** - 20 min - Maillage FEM
7. **src/fem_solver.py** - 20 min - Résolution
8. **src/analysis.py** - 15 min - Post-traitement

**Total : ~2 heures pour comprendre complètement le projet**

## 🚀 Extension du projet

### Ajouter un nouveau profil de taper
1. Éditer `src/config.py` → Classe `TaperProfile`
2. Ajouter une méthode `@staticmethod`
3. Appeler dans `src/geometry.py`
4. Simuler : `python main.py --profile custom_name`

### Changer le matériau
1. Éditer `src/config.py` → `PhysicalParameters`
2. Modifier `n_core`, `n_cladding`
3. Relancer les simulations

### Ajouter une nouvelle condition aux limites
1. Éditer `src/fem_solver.py` → `apply_boundary_conditions()`
2. Implémenter la condition (e.g., PML)
3. Tester sur un cas simple

## 📞 Questions fréquentes

**Q: Pourquoi 2D et pas 3D ?**
A: La symétrie cylindrique permet 2D axisymétrique = 3D physique avec coût 2D

**Q: Comment ajouter du bruit/perturbations ?**
A: Modifier le maillage dans `meshing.py` ou ajouter une perturbation dans `geometry.py`

**Q: Comment exporter vers COMSOL/Lumerical ?**
A: Les maillages `.msh` sont déjà en format standard Gmsh

**Q: Peut-on paralléliser les simulations ?**
A: Oui, modifier `analysis.py` pour utiliser `multiprocessing.Pool`

---

**Version**: 0.1.0  
**Statut**: ✅ Fonctionnel et documenté  
**Prêt pour**: Recherche, conception, optimisation
