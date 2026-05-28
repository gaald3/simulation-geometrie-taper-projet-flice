"""
Module de création du maillage FEM avec Gmsh
Génère un maillage adapté pour la simulation du taper
"""

import numpy as np
import gmsh
from pathlib import Path
from .config import PhysicalParameters as Phys, NumericalParameters as Num, OutputParameters


class MeshGenerator:
    """Génère le maillage FEM pour la simulation du taper"""
    
    def __init__(self, taper_geometry, profile_name="taper"):
        """
        Initialise le générateur de maillage
        
        Parameters:
        -----------
        taper_geometry : TaperGeometry
            Objet contenant la géométrie du taper
        profile_name : str
            Nom du profil (pour les fichiers)
        """
        self.geometry = taper_geometry
        self.profile_name = profile_name
        self.gmsh_model = None
        self.mesh_file = None
        
    def create_2d_axisymmetric_mesh(self):
        """
        Crée un maillage 2D axisymétrique (r, z) simplifié
        """
        gmsh.initialize()
        gmsh.model.add(f"taper_{self.profile_name}")
        
        # Récupérer le profil du taper
        if self.geometry.radius_profile is None:
            self.geometry.generate_profile(n_points=100)
        
        z_coords = self.geometry.z_coords
        r_profile = self.geometry.radius_profile
        
        z_min, z_max = 0, Phys.taper_length
        r_max_profile = np.max(r_profile)
        r_external = max(Phys.fiber_cladding_radius, 2*r_max_profile)
        
        # ===== GÉOMÉTRIE SIMPLIFIÉE =====
        # Rectangle avec profil du taper comme arête gauche
        
        # Coins du rectangle externe
        pt_bot_left = gmsh.model.geo.addPoint(0, z_min, 0, Num.mesh_element_size_core)
        pt_bot_right = gmsh.model.geo.addPoint(r_external, z_min, 0, Num.mesh_element_size_far_field)
        pt_top_right = gmsh.model.geo.addPoint(r_external, z_max, 0, Num.mesh_element_size_far_field)
        pt_top_left = gmsh.model.geo.addPoint(0, z_max, 0, Num.mesh_element_size_core)
        
        # Arêtes du rectangle externe
        line_bottom = gmsh.model.geo.addLine(pt_bot_left, pt_bot_right)
        line_right = gmsh.model.geo.addLine(pt_bot_right, pt_top_right)
        line_top = gmsh.model.geo.addLine(pt_top_right, pt_top_left)
        line_left = gmsh.model.geo.addLine(pt_top_left, pt_bot_left)
        
        # Créer une spline pour le profil du taper (plus robuste)
        # Utiliser moins de points pour éviter les problèmes de tolérance
        n_sample = 15
        indices_sample = np.unique(np.linspace(0, len(z_coords)-1, n_sample, dtype=int))
        
        profile_points = []
        for idx in indices_sample:
            pt = gmsh.model.geo.addPoint(r_profile[idx], z_coords[idx], 0,
                                         Num.mesh_element_size_core)
            profile_points.append(pt)
        
        # Créer les lignes du profil
        profile_lines = []
        for i in range(len(profile_points) - 1):
            line = gmsh.model.geo.addLine(profile_points[i], profile_points[i+1])
            profile_lines.append(line)
        
        # Fermer le profil (revenir à l'axe)
        line_close_left = gmsh.model.geo.addLine(profile_points[-1], profile_points[0])
        
        # Créer la surface du domaine (rectangle entier)
        loop = gmsh.model.geo.addCurveLoop([line_bottom, line_right, line_top, line_left])
        surface = gmsh.model.geo.addPlaneSurface([loop])
        
        # Synchroniser la géométrie
        gmsh.model.geo.synchronize()
        
        # ===== AFFECTATION DES TAILLES D'ÉLÉMENTS =====
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), Num.mesh_element_size_core)
        gmsh.model.mesh.setSize([(0, pt_top_right), (0, pt_bot_right)], 
                               Num.mesh_element_size_far_field)
        
        # ===== GÉNÉRATION DU MAILLAGE =====
        gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
        gmsh.model.mesh.generate(2)  # Maillage 2D
        gmsh.model.mesh.optimize("Laplace2D")  # Optimisation Laplace
        
        # ===== AFFECTATION DES TAGS PHYSIQUES =====
        
        # Groupe de volume (toute la surface)
        gmsh.model.addPhysicalGroup(2, [surface], 1)
        gmsh.model.setPhysicalName(2, 1, "Domain")
        
        # Groupe de frontière - Entrée (z=0)
        gmsh.model.addPhysicalGroup(1, [line_bottom], 2)
        gmsh.model.setPhysicalName(1, 2, "Inlet")
        
        # Groupe de frontière - Sortie (z=L)
        gmsh.model.addPhysicalGroup(1, [line_top], 3)
        gmsh.model.setPhysicalName(1, 3, "Outlet")
        
        # Groupe de frontière - Axe de symétrie (r=0)
        gmsh.model.addPhysicalGroup(1, [line_left], 4)
        gmsh.model.setPhysicalName(1, 4, "SymmetryAxis")
        
        # Groupe de frontière - Droite (r=r_ext)
        gmsh.model.addPhysicalGroup(1, [line_right], 5)
        gmsh.model.setPhysicalName(1, 5, "FarField")
        
        self.gmsh_model = gmsh.model
        
        return surface
    
    def extract_mesh_data(self):
        """
        Extrait les données du maillage de Gmsh
        
        Returns:
        --------
        dict : Dictionnaire contenant les coordonnées et connectivités
        """
        if self.gmsh_model is None:
            raise ValueError("Le maillage n'a pas été généré. Appelez create_2d_axisymmetric_mesh() d'abord.")
        
        # Récupérer les nœuds
        node_tags, node_coords, _ = self.gmsh_model.mesh.getNodes()
        nodes = node_coords.reshape(-1, 3)
        
        # Récupérer les éléments (triangles 2D)
        elem_type, elem_tags, elem_connectivity = self.gmsh_model.mesh.getElements(dim=2, tag=1)
        
        if len(elem_tags) == 0 or len(elem_type) == 0:
            raise ValueError("Aucun élément 2D trouvé dans le maillage")
        
        # Adapter à la structure retournée
        if isinstance(elem_connectivity, list):
            connectivity = elem_connectivity[0] if elem_connectivity else np.array([])
        else:
            connectivity = elem_connectivity
        
        elements = connectivity.reshape(-1, 3) - 1  # Indexation 0-based
        
        mesh_data = {
            'nodes': nodes[:, :2],  # Seulement (r, z)
            'elements': elements.astype(np.int32),
            'node_tags': node_tags,
            'n_nodes': len(node_tags),
            'n_elements': len(elements),
        }
        
        return mesh_data
    
    def save_mesh(self, filename=None):
        """
        Sauvegarde le maillage en format Gmsh
        
        Parameters:
        -----------
        filename : str, optional
            Chemin du fichier de sortie
        """
        if self.gmsh_model is None:
            raise ValueError("Le maillage n'a pas été généré.")
        
        if filename is None:
            path = Path(OutputParameters.output_dir)
            path.mkdir(exist_ok=True)
            filename = f"{path}/mesh_{self.profile_name}.msh"
        
        gmsh.write(filename)
        self.mesh_file = filename
        print(f"✓ Maillage sauvegardé: {filename}")
    
    def finalize(self):
        """Finalise Gmsh"""
        gmsh.finalize()
    
    def get_mesh_statistics(self, mesh_data):
        """
        Affiche les statistiques du maillage
        
        Parameters:
        -----------
        mesh_data : dict
            Données du maillage
        """
        print("\n" + "="*60)
        print("STATISTIQUES DU MAILLAGE")
        print("="*60)
        print(f"Nombre de nœuds:           {mesh_data['n_nodes']}")
        print(f"Nombre d'éléments:         {mesh_data['n_elements']}")
        print(f"Rapport nœuds/éléments:    {mesh_data['n_nodes']/mesh_data['n_elements']:.2f}")
        
        # Calcul de la taille caractéristique des éléments
        nodes = mesh_data['nodes']
        elems = mesh_data['elements']
        
        sizes = []
        for elem in elems:
            nodes_elem = nodes[elem]
            # Distance maximum entre les nœuds de l'élément
            for i in range(3):
                for j in range(i+1, 3):
                    dist = np.linalg.norm(nodes_elem[i] - nodes_elem[j])
                    sizes.append(dist)
        
        sizes = np.array(sizes)
        print(f"Taille éléments (min):     {sizes.min()*1e6:.2f} µm")
        print(f"Taille éléments (max):     {sizes.max()*1e6:.2f} µm")
        print(f"Taille éléments (moy):     {sizes.mean()*1e6:.2f} µm")
        print("="*60 + "\\n")


if __name__ == "__main__":
    from geometry import TaperGeometry
    
    # Test: créer un maillage pour chaque profil
    profiles = ["linear", "parabolic"]
    
    for profile in profiles:
        print(f"\n{'='*60}")
        print(f"Génération maillage pour profil: {profile}")
        print(f"{'='*60}")
        
        geom = TaperGeometry(profile_type=profile)
        geom.generate_profile()
        
        mesher = MeshGenerator(geom, profile_name=profile)
        mesher.create_2d_axisymmetric_mesh()
        
        mesh_data = mesher.extract_mesh_data()
        mesher.get_mesh_statistics(mesh_data)
        mesher.save_mesh()
        mesher.finalize()
