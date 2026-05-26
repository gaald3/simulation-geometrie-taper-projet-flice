# 🚀 Démarrage rapide - FEM Taper

## ⏱️ Installation (5 minutes)

### Étape 1 : Prérequis
```bash
# Vérifier Python 3.8+
python --version

# Vérifier pip
pip --version
```

### Étape 2 : Installer les dépendances
```bash
# À partir du répertoire du projet
pip install -r requirements.txt
```

**Sur macOS, si problème avec Gmsh :**
```bash
pip install --upgrade gmsh
# ou
brew install gmsh
```

## ⚡ Premier test (2 minutes)

### Lancer une simulation simple
```bash
python main.py --profile linear --no-plot
```

Vous devriez voir :
```
======================================================================
SIMULATION FEM - TAPER FIBRE OPTIQUE SMF28
======================================================================
✓ Matrices assemblées...
✓ {N} modes trouvés
Transmission: XX.XX%
Pertes: X.XX dB
```

## 📊 Simulation complète (5 minutes)

### Comparaison de tous les profils
```bash
python main.py
```

Cela va :
1. ✓ Générer les 3 profils (linéaire, parabolique, exponentiel)
2. ✓ Créer les maillages
3. ✓ Résoudre les systèmes FEM
4. ✓ Afficher les graphiques
5. ✓ Exporter les résultats

### Résultats générés
```
output/
├── geometry_*.png          (profils visuels)
├── comparison_results.png  (graphiques comparatifs)
├── results_comparison.csv  (tableau Excel-compatible)
└── report.html             (rapport complet)
```

## 🔍 Exemples pas à pas

### Exemple 1 : Visualiser les profils
```bash
python tests/examples.py --example 1
```
Affiche les 4 profils disponibles et leur adiabaticité.

### Exemple 2 : Générer un maillage
```bash
python tests/examples.py --example 2
```
Crée un maillage Gmsh et montre les statistiques.

### Exemple 3 : Résoudre FEM
```bash
python tests/examples.py --example 3
```
Calcule les modes et les pertes d'un taper.

### Exemple 4 : Comparaison complète
```bash
python tests/examples.py --example 4
```
Lance les 4 simulations et compare les résultats.

### Tous les exemples
```bash
python tests/examples.py --all
```

## 🎯 Cas d'usage courants

### Cas 1 : Tester un nouveau profil
Éditez `src/config.py` et ajoutez une nouvelle méthode dans `TaperProfile` :

```python
@staticmethod
def custom_profile(z, z_max, r_initial, r_final):
    """Votre profil personnalisé"""
    return r_initial - (r_initial - r_final) * (z/z_max)**0.5
```

Puis simulez :
```bash
python main.py --profile custom_profile
```

### Cas 2 : Changer la longueur d'onde
Éditez `src/config.py` :

```python
# Cherchez la ligne
wavelength = 1550e-9  # 1550 nm

# Changez en, par exemple :
wavelength = 1310e-9  # 1310 nm
```

Puis relancez :
```bash
python main.py
```

### Cas 3 : Affiner le maillage pour meilleure précision
Éditez `src/config.py` :

```python
# Plus fin
mesh_element_size_core = 0.05e-6  # au lieu de 0.1

# (attention: plus lent)
```

### Cas 4 : Exporter juste les résultats CSV
```bash
python main.py --no-plot --no-html
```

## 📋 Structure des résultats CSV

```
Profil;Transmission;Pertes_dB;Adiabaticite;...
linear;95.23;0.20;1.5e-7;...
parabolic;97.45;0.11;2.3e-6;...
exponential;98.67;0.06;5.1e-6;...
```

Ouvrable avec Excel, Python (pandas), ou n'importe quel outil tableur.

## 🐛 Troubleshooting rapide

### "gmsh not found"
```bash
pip install --upgrade gmsh
```

### "ModuleNotFoundError: No module named 'scipy'"
```bash
pip install scipy
```

### La simulation est très lente
→ Augmentez la taille des éléments dans `config.py` :
```python
mesh_element_size_core = 0.2e-6  # plus grossier = plus rapide
```

### Je veux comprendre un paramètre
→ Regardez les docstrings :
```python
from src.config import PhysicalParameters
help(PhysicalParameters)
```

## 📚 Prochaines étapes

1. **Lire** `README.md` pour la documentation complète
2. **Explorer** `TECHNICAL_SUMMARY.md` pour les équations
3. **Consulter** `CONTRIBUTING.md` pour développer
4. **Analyser** le code source commenté dans `src/`

## 💡 Conseils d'utilisation

✅ **Bonnes pratiques**
- Créez un répertoire `output/` pour chaque campagne de simulations
- Notez vos paramètres dans un fichier de configuration
- Exportez en CSV pour comparer avec d'autres outils

⚠️ **À éviter**
- Ne lancez pas plusieurs simulations simultanément (CPU)
- Ne modifiez pas les fichiers source sans backup
- Ne supprimez pas le dossier `output/` avant d'avoir copié les résultats

## 🎓 Apprendre la physique du problème

Si vous voulez comprendre pourquoi certains profils sont meilleurs :
- **Adiabaticité** : Plus grande = transition plus lisse = moins de pertes
- **Modes guidés** : Moins de modes = moins de pertes radiatives
- **Transmission** : En %, proportion de puissance transmise

Consultez `TECHNICAL_SUMMARY.md` pour les équations mathématiques.

## 📞 Support

Avez-vous une question ?
1. Vérifiez `README.md`
2. Cherchez dans `CONTRIBUTING.md`
3. Ouvrez une issue GitHub
4. Contactez l'équipe FLISE

---

**Prêt à commencer ? Lancez :**
```bash
python main.py
```

**Bon courage ! 🔬**
