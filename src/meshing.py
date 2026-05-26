"""
Module de création du maillage FEM avec Gmsh
Génère un maillage adapté pour la simulation du taper
"""

import numpy as np
import gmsh
from pathlib import Path
from config import PhysicalParameters as Phys, NumericalParameters as Num, OutputParameters


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
        Crée un maillage 2D axisymétrique (r, z)
        Exploite la symétrie cylindrique du problème
        """
        gmsh.initialize()
        gmsh.model.add(f"taper_{self.profile_name}")
        
        # Récupérer le profil du taper
        if self.geometry.radius_profile is None:
            self.geometry.generate_profile(n_points=200)
        
        z_coords = self.geometry.z_coords
        r_profile = self.geometry.radius_profile
        
        # ===== CRÉATION DE LA GÉOMÉTRIE =====
        
        # 1. Axe de symétrie (r = 0, de z=0 à z=L)
        z_min, z_max = 0, Phys.taper_length
        pt_axis_top = gmsh.model.geo.addPoint(0, z_max, 0, Num.mesh_element_size_core)
        pt_axis_bot = gmsh.model.geo.addPoint(0, z_min, 0, Num.mesh_element_size_core)
        line_axis = gmsh.model.geo.addLine(pt_axis_bot, pt_axis_top)
        
        # 2. Surface du taper - points sur la frontière
        taper_points = []
        
        # Bottom (z=0)
        pt_start = gmsh.model.geo.addPoint(r_profile[0], z_coords[0], 0, 
                                          Num.mesh_element_size_core)
        taper_points.append(pt_start)
        
        # Points intermédiaires le long du profil
        for i in range(1, len(z_coords)-1, max(1, len(z_coords)//50)):  # ~50 points
            pt = gmsh.model.geo.addPoint(r_profile[i], z_coords[i], 0,
                                        Num.mesh_element_size_core)
            taper_points.append(pt)
        
        # Top (z=L)
        pt_end = gmsh.model.geo.addPoint(r_profile[-1], z_coords[-1], 0,
                                        Num.mesh_element_size_core)
        taper_points.append(pt_end)
        
        # 3. Créer la ligne du profil du taper
        taper_lines = []
        for i in range(len(taper_points)-1):
            line = gmsh.model.geo.addLine(taper_points[i], taper_points[i+1])
            taper_lines.append(line)
        taper_profile_line = taper_lines[0]
        
        # 4. Rayon externe (région de calcul)
        r_external = max(Phys.fiber_cladding_radius, 2*max(r_profile)) + Num.pml_thickness
        
        # Sortie (top) - rayon externe
        pt_ext_top = gmsh.model.geo.addPoint(r_external, z_max, 0, 
                                            Num.mesh_element_size_far_field)
        # Entrée (bottom) - rayon externe  
        pt_ext_bot = gmsh.model.geo.addPoint(r_external, z_min, 0,
                                            Num.mesh_element_size_far_field)
        
        # Lignes externes
        line_ext_bottom = gmsh.model.geo.addLine(pt_end, pt_ext_bot)
        line_ext_top = gmsh.model.geo.addLine(pt_ext_top, pt_axis_top)
        line_ext_right = gmsh.model.geo.addLine(pt_ext_bot, pt_ext_top)
        
        # 5. Créer les surfaces
        # Boucle pour le domaine de calcul
        profile_loop = gmsh.model.geo.addCurveLoop([line_axis] + taper_lines + 
                                                    [line_ext_bottom, line_ext_right, 
                                                     line_ext_top])
        surface = gmsh.model.geo.addPlaneSurface([profile_loop])
        
        # Synchroniser la géométrie
        gmsh.model.geo.synchronize()
        
        # ===== AFFECTATION DES TAILLES D'ÉLÉMENTS =====
        
        # Raffinement fin près de la fibre
        r_refine = max(r_profile) * 1.5
        gmsh.model.mesh.setSize(gmsh.model.getEntities(0), Num.mesh_element_size_core)
        
        # Raffinement moins fin loin du cœur
        gmsh.model.mesh.setSize([(0, pt_ext_top), (0, pt_ext_bot)], 
                               Num.mesh_element_size_far_field)
        
        # ===== GÉNÉRATION DU MAILLAGE =====
        gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
        gmsh.option.setNumber("Mesh.SubdivisionAlgorithm", 1)  # Simplicial
        
        gmsh.model.mesh.generate(2)  # Maillage 2D
        gmsh.model.mesh.optimize("Laplace2D")  # Optimisation Laplace
        
        # ===== AFFECTATION DES TAGS PHYSIQUES =====
        
        # Groupe de volume (toute la surface)
        gmsh.model.addPhysicalGroup(2, [surface], 1)
        gmsh.model.setPhysicalName(2, 1, "Domain")
        
        # Groupe de frontière - Entrée (z=0, r externe)
        gmsh.model.addPhysicalGroup(1, [line_axis, line_ext_bottom], 2)
        gmsh.model.setPhysicalName(1, 2, "Inlet")
        
        # Groupe de frontière - Sortie (z=L, r externe)
        gmsh.model.addPhysicalGroup(1, [line_ext_top], 3)
        gmsh.model.setPhysicalName(1, 3, "Outlet")
        
        # Groupe de frontière - Axe de symétrie
        gmsh.model.addPhysicalGroup(1, [line_axis], 4)
        gmsh.model.setPhysicalName(1, 4, "SymmetryAxis")
        
        # Groupe de frontière - Droite (r=r_ext)
        gmsh.model.addPhysicalGroup(1, [line_ext_right], 5)
        gmsh.model.setPhysicalName(1, 5, "FarField")
        
        # Groupe pour le profil du taper (interface air-silice)
        gmsh.model.addPhysicalGroup(1, taper_lines, 6)
        gmsh.model.setPhysicalName(1, 6, "TaperInterface")
        
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
        elem_tags, elem_connectivity = self.gmsh_model.mesh.getElements(dim=2, tag=1)
        
        if len(elem_tags) == 0:
            raise ValueError("Aucun élément 2D trouvé dans le maillage")
        
        elements = elem_connectivity[0].reshape(-1, 3) - 1  # Indexation 0-based
        
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
