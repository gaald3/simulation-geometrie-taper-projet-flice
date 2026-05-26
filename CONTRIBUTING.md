# Guide de Développement

## Architecture générale

Le projet suit une architecture modulaire avec séparation des responsabilités :

```
Configuration → Géométrie → Maillage → Solveur FEM → Analyse
   (config.py)  (geometry.py) (meshing.py) (fem_solver.py) (analysis.py)
```

## Flux de travail d'une simulation

1. **Configuration** : Charger les paramètres physiques et numériques
2. **Géométrie** : Générer le profil du taper
3. **Maillage** : Créer un maillage adaptatif avec Gmsh
4. **Assembly** : Assembler les matrices de raideur et masse
5. **Résolution** : Résoudre le problème aux valeurs propres
6. **Post-traitement** : Calculer transmission, pertes, visualiser

## Amélioration future

### Court terme (v0.2)
- [ ] Implémenter les conditions aux limites (PML) pour éviter les réflexions
- [ ] Ajouter le calcul des pertes radiatives
- [ ] Améliorer l'estimation de la transmission (intégration du champ)
- [ ] Support de la polarisation (modes TM/TE)
- [ ] Animation de la propagation du mode

### Moyen terme (v0.3)
- [ ] Optimisation automatique de la géométrie
- [ ] Analyse de sensibilité paramétrique
- [ ] Influence de la température sur les indices
- [ ] Jonctions tapers multiples
- [ ] Export vers FDTD/Comsol

### Long terme (v1.0)
- [ ] Interface graphique (PyQt/Kivy)
- [ ] Documentation interactive Jupyter
- [ ] Accélération GPU (CuPy/JAX)
- [ ] Couplage avec simulations silicium PIC
- [ ] Base de données de solutions

## Points techniques à améliorer

### FEM Solver
- [ ] Utiliser des éléments de plus haut degré (P2, P3)
- [ ] Implémenter la condensation statique
- [ ] Adaptive mesh refinement (AMR)
- [ ] Préconditionneur pour meilleure convergence

### Maillage
- [ ] Raffinement automatique selon gradient d'indice
- [ ] Support des éléments courbes
- [ ] Export en format HDF5 pour grandes simulations

### Analyse
- [ ] Calcul du champ E et H complets
- [ ] Densité de puissance (Poynting vector)
- [ ] Énergie confinée dans le cœur
- [ ] Graphiques interactifs (Plotly)

## Style de code

Respecter PEP 8 :
```bash
# Vérifier le style
pip install flake8
flake8 src/

# Formater automatiquement
pip install black
black src/
```

## Tests

Ajouter des tests unitaires :
```bash
pip install pytest
pytest tests/
```

Exemple de test :
```python
def test_taper_profile_linear():
    geom = TaperGeometry(profile_type="linear")
    z, r = geom.generate_profile()
    assert r[0] > r[-1]  # Diamètre décroissant
    assert len(z) == len(r)
```

## Documentation

- Utiliser les docstrings en format NumPy
- Générer la doc HTML : `pip install sphinx`
- Ajouter des exemples Jupyter dans `docs/`

## Debug

Mode debug activé :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Profiler les performances :
```python
import cProfile
cProfile.run('runner.run_all_simulations()')
```

## Versioning

Suivi sémantique : MAJOR.MINOR.PATCH
- PATCH : bug fixes
- MINOR : nouvelles features (rétro-compatible)
- MAJOR : changements non rétro-compatibles

## Release checklist

- [ ] Tous les tests passent
- [ ] Documentation à jour
- [ ] Changelog complété
- [ ] Version bumped
- [ ] Tag Git créé
- [ ] Release notes sur GitHub

## Communication

- Issues : bug reports et features
- Discussions : questions générales
- PRs : contributions de code

## Ressources internes

- Documentation Gmsh : https://gmsh.info/doc/texinfo/gmsh.html
- SciPy Sparse : https://docs.scipy.org/doc/scipy/reference/sparse.html
- NumPy : https://numpy.org/doc/

---

Bienvenue dans le projet FEM Taper ! 🚀
