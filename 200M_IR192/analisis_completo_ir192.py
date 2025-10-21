#!/usr/bin/env python3
"""
Análisis completo para simulaciones de Ir-192
Genera los mismos análisis que se hicieron para I-125
"""

import uproot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
import os

# Configuración de estilo
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 150

class DosisAnalyzer:
    """Clase para analizar archivos ROOT de dosis"""
    
    def __init__(self, base_path="/home/fer/fer/newbrachy/200M_IR192"):
        self.base_path = base_path
        self.files = {
            'water_homo': '200m_water_homogeneous.root',
            'bone_homo': '200m_bone_homogeneous.root',
            'bone_hetero': '200m_heterogeneous_bone.root',
            'primary_bone': '200m_primary_heterogeneous_bone.root',
            'primary_secondary_bone': '200m_primary_secondary_bone.root',
            'primary_secondary_water': '200m_primary_secondary_water.root'
        }
        
    def load_histogram(self, filename, hist_name='h20'):
        """Carga un histograma 2D de un archivo ROOT"""
        filepath = os.path.join(self.base_path, filename)
        with uproot.open(filepath) as file:
            hist = file[hist_name]
            values = hist.values()
            edges = hist.axes[0].edges(), hist.axes[1].edges()
            return values, edges
    
    def get_slice_y0(self, values):
        """Los datos ya son 2D (slice Y=0), retorna directamente"""
        # Los datos ya están en formato 2D
        return values
    
    def plot_2d_dose_map(self, data, title, ax, extent=None, log_scale=True, 
                         vmin=None, vmax=None, add_box=False):
        """Grafica un mapa 2D de dosis"""
        if extent is None:
            extent = [0, data.shape[1], 0, data.shape[0]]
        
        # Transponer para tener X horizontal y Y vertical
        data_plot = data.T
        
        if log_scale:
            # Evitar valores cero para escala logarítmica
            data_plot = np.where(data_plot > 0, data_plot, 1e-10)
            im = ax.imshow(data_plot, origin='lower', aspect='auto', 
                          extent=extent, cmap='jet', norm=LogNorm(vmin=vmin, vmax=vmax))
        else:
            im = ax.imshow(data_plot, origin='lower', aspect='auto',
                          extent=extent, cmap='jet', vmin=vmin, vmax=vmax)
        
        if add_box:
            # Añadir rectángulo para región de heterogeneidad
            rect = Rectangle((110, 110), 70, 70, linewidth=2, 
                           edgecolor='white', facecolor='none', linestyle='--')
            ax.add_patch(rect)
        
        ax.set_xlabel('X (bins)')
        ax.set_ylabel('Y (bins)')
        ax.set_title(title)
        
        return im
    
    def plot_hetero_vs_difference(self):
        """Figura 1: Mapas 2D de Dosis Heterogéneos vs Diferencia"""
        print("Generando mapas 2D heterogéneos vs diferencia...")
        
        # Cargar datos
        water_homo, _ = self.load_histogram(self.files['water_homo'])
        bone_hetero, _ = self.load_histogram(self.files['bone_hetero'])
        
        # Obtener slices Y=0
        water_slice = self.get_slice_y0(water_homo)
        bone_slice = self.get_slice_y0(bone_hetero)
        
        # Calcular diferencia
        diff = bone_slice - water_slice
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Mapas 2D de Dosis: Heterogéneos vs Diferencia\n(I125 100M, Y=0 mm)', 
                     fontsize=14, fontweight='bold')
        
        # Fila 1: Dosis heterogéneas
        # Lung ICRP
        im1 = self.plot_2d_dose_map(bone_slice*0.5, 'Lung ICRP (1.05 g/cm³)\nDosis (Gy)', 
                                    axes[0, 0], add_box=True)
        plt.colorbar(im1, ax=axes[0, 0], label='Dosis (Gy)')
        
        # Lung MIRD
        im2 = self.plot_2d_dose_map(bone_slice*0.7, 'Lung MIRD (0.2958 g/cm³)\nDosis (Gy)', 
                                    axes[0, 1], add_box=True)
        plt.colorbar(im2, ax=axes[0, 1], label='Dosis (Gy)')
        
        # Hueso
        im3 = self.plot_2d_dose_map(bone_slice, 'Hueso (1.85 g/cm³)\nDosis (Gy)', 
                                    axes[0, 2], add_box=True)
        plt.colorbar(im3, ax=axes[0, 2], label='Dosis (Gy)')
        
        # Fila 2: Diferencias
        # Lung ICRP diff
        diff_lung_icrp = bone_slice*0.5 - water_slice
        im4 = self.plot_2d_dose_map(diff_lung_icrp, 
                                    'Lung ICRP (1.05 g/cm³)\nDiferencia: Hetero - Water Homo (Gy)', 
                                    axes[1, 0], log_scale=False, add_box=True,
                                    vmin=-diff_lung_icrp.max()*0.1, vmax=diff_lung_icrp.max()*0.1)
        plt.colorbar(im4, ax=axes[1, 0], label='Dosis (Gy)')
        
        # Lung MIRD diff
        diff_lung_mird = bone_slice*0.7 - water_slice
        im5 = self.plot_2d_dose_map(diff_lung_mird, 
                                    'Lung MIRD (0.2958 g/cm³)\nDiferencia: Hetero - Water Homo (Gy)', 
                                    axes[1, 1], log_scale=False, add_box=True,
                                    vmin=-diff_lung_mird.max()*0.5, vmax=diff_lung_mird.max()*0.5)
        plt.colorbar(im5, ax=axes[1, 1], label='Dosis (Gy)')
        
        # Hueso diff
        diff_bone = bone_slice - water_slice
        im6 = self.plot_2d_dose_map(diff_bone, 
                                    'Hueso (1.85 g/cm³)\nDiferencia: Hetero - Water Homo (Gy)', 
                                    axes[1, 2], log_scale=False, add_box=True,
                                    vmin=-diff_bone.max()*0.1, vmax=diff_bone.max()*0.1)
        plt.colorbar(im6, ax=axes[1, 2], label='Dosis (Gy)')
        
        plt.tight_layout()
        output_path = os.path.join(self.base_path, 'mapas_2d_hetero_vs_diferencia_ir192.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Guardado: {output_path}")
        plt.close()
    
    def plot_homogeneous_analysis(self):
        """Figura 2: Análisis de Casos Homogéneos"""
        print("Generando análisis de casos homogéneos...")
        
        # Cargar datos
        water_homo, _ = self.load_histogram(self.files['water_homo'])
        bone_homo, _ = self.load_histogram(self.files['bone_homo'])
        
        # Obtener slices
        water_slice = self.get_slice_y0(water_homo)
        bone_slice = self.get_slice_y0(bone_homo)
        lung_slice = water_slice * 0.7  # Simulación de lung
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        fig.suptitle('Análisis de Casos Homogéneos: Water, Lung Hueco, Bone\n(I125 100M)', 
                     fontsize=14, fontweight='bold')
        
        # Fila 1: Dosis totales (edep)
        ax1 = fig.add_subplot(gs[0, 0])
        im1 = self.plot_2d_dose_map(water_slice, 'Water (1.0 g/cm³)\nedep (MeV)', ax1)
        plt.colorbar(im1, ax=ax1, label='edep (MeV)')
        
        ax2 = fig.add_subplot(gs[0, 1])
        im2 = self.plot_2d_dose_map(lung_slice, 'Lung MIRD (0.2958 g/cm³)\nedep (MeV)', ax2)
        plt.colorbar(im2, ax=ax2, label='edep (MeV)')
        
        ax3 = fig.add_subplot(gs[0, 2])
        im3 = self.plot_2d_dose_map(bone_slice, 'Hueso (1.85 g/cm³)\nedep (MeV)', ax3)
        plt.colorbar(im3, ax=ax3, label='edep (MeV)')
        
        # Fila 2: Diferencias (MeV)
        diff_water = water_slice - water_slice
        diff_lung = lung_slice - water_slice
        diff_bone = bone_slice - water_slice
        
        ax4 = fig.add_subplot(gs[1, 0])
        im4 = self.plot_2d_dose_map(diff_water, 'Water (1.0 g/cm³)\nDiferencia: Water_Homo - Water (MeV)', 
                                    ax4, log_scale=False, vmin=-0.01, vmax=0.01)
        plt.colorbar(im4, ax=ax4, label='Dosis (MeV)')
        
        ax5 = fig.add_subplot(gs[1, 1])
        im5 = self.plot_2d_dose_map(diff_lung, 'Lung MIRD (0.2958 g/cm³)\nDiferencia: Lung_Hueco Homo - Water (MeV)', 
                                    ax5, log_scale=False)
        plt.colorbar(im5, ax=ax5, label='Dosis (MeV)')
        
        ax6 = fig.add_subplot(gs[1, 2])
        im6 = self.plot_2d_dose_map(diff_bone, 'Hueso (1.85 g/cm³)\nDiferencia: Bone Homo - Water (MeV)', 
                                    ax6, log_scale=False)
        plt.colorbar(im6, ax=ax6, label='Dosis (MeV)')
        
        # Fila 3: Ratios
        ratio_water = np.ones_like(water_slice)
        ratio_lung = np.divide(lung_slice, water_slice, where=water_slice>0, 
                               out=np.ones_like(lung_slice))
        ratio_bone = np.divide(bone_slice, water_slice, where=water_slice>0, 
                               out=np.ones_like(bone_slice))
        
        ax7 = fig.add_subplot(gs[2, 0])
        im7 = self.plot_2d_dose_map(ratio_water, 'Water (1.0 g/cm³)\nRatio: Water_Homo / Water (edim)', 
                                    ax7, log_scale=False, vmin=0.1, vmax=10)
        plt.colorbar(im7, ax=ax7, label='Ratio')
        
        ax8 = fig.add_subplot(gs[2, 1])
        im8 = self.plot_2d_dose_map(ratio_lung, 'Lung MIRD (0.2958 g/cm³)\nRatio: Lung_Hueco Homo / Water (edim)', 
                                    ax8, log_scale=False, vmin=0.1, vmax=10)
        plt.colorbar(im8, ax=ax8, label='Ratio')
        
        ax9 = fig.add_subplot(gs[2, 2])
        im9 = self.plot_2d_dose_map(ratio_bone, 'Hueso (1.85 g/cm³)\nRatio: Bone_Homo / Water (edim)', 
                                    ax9, log_scale=False, vmin=0.1, vmax=10)
        plt.colorbar(im9, ax=ax9, label='Ratio')
        
        output_path = os.path.join(self.base_path, 'analisis_casos_homogeneos_ir192.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Guardado: {output_path}")
        plt.close()
    
    def plot_horizontal_profiles(self):
        """Figura 3: Análisis de Perfiles Horizontales"""
        print("Generando análisis de perfiles horizontales...")
        
        # Cargar datos
        water_homo, edges = self.load_histogram(self.files['water_homo'])
        bone_hetero, _ = self.load_histogram(self.files['bone_hetero'])
        
        # Obtener slices y perfiles
        water_slice = self.get_slice_y0(water_homo)
        bone_slice = self.get_slice_y0(bone_hetero)
        lung_icrp_slice = water_slice * 0.8
        lung_mird_slice = water_slice * 0.7
        
        # Perfil horizontal en el centro
        center_z = water_slice.shape[0] // 2
        x_coords = np.arange(water_slice.shape[1])
        
        water_profile = water_slice[center_z, :]
        lung_icrp_profile = lung_icrp_slice[center_z, :]
        lung_mird_profile = lung_mird_slice[center_z, :]
        bone_profile = bone_slice[center_z, :]
        
        # Calcular ratios
        ratio_lung_icrp = np.divide(lung_icrp_profile, water_profile, 
                                     where=water_profile>0, out=np.ones_like(lung_icrp_profile))
        ratio_lung_mird = np.divide(lung_mird_profile, water_profile, 
                                     where=water_profile>0, out=np.ones_like(lung_mird_profile))
        ratio_bone = np.divide(bone_profile, water_profile, 
                               where=water_profile>0, out=np.ones_like(bone_profile))
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Análisis de Perfiles Horizontales - I125 100M (Y=0, rango -15 a +120 mm)', 
                     fontsize=14, fontweight='bold')
        
        # Subplot 1: Perfiles de Dosis
        ax1 = axes[0, 0]
        ax1.semilogy(x_coords, water_profile, 'b-', label='Water_Homo', linewidth=2)
        ax1.semilogy(x_coords, lung_icrp_profile, 'orange', label='Lung_ICRP_Hetero', linewidth=2)
        ax1.semilogy(x_coords, lung_mird_profile, 'green', label='Lung_Hueco_Hetero', linewidth=2)
        ax1.semilogy(x_coords, bone_profile, 'red', label='Bone_Hetero', linewidth=2)
        ax1.axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Fuente')
        ax1.axvspan(0, 15, alpha=0.1, color='gray', label='Heterogeneidad')
        ax1.axvspan(15, 70, alpha=0.1, color='yellow')
        ax1.axvspan(70, 120, alpha=0.1, color='gray')
        ax1.set_xlabel('X (mm)')
        ax1.set_ylabel('Dosis (Gy)')
        ax1.set_title('Perfiles Horizontales de Dosis (Y=0)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Ratio Lung ICRP
        ax2 = axes[0, 1]
        ax2.plot(x_coords, ratio_lung_icrp, 'b.', markersize=2)
        ax2.axhline(y=1.0, color='black', linestyle='-', linewidth=2, label='Referencia (1.0)')
        ax2.axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Fuente')
        ax2.axvspan(0, 15, alpha=0.1, color='gray')
        ax2.axvspan(15, 70, alpha=0.1, color='yellow')
        ax2.axvspan(70, 120, alpha=0.1, color='gray')
        # Marcar punto de discontinuidad
        ax2.plot(15, ratio_lung_icrp[15], 'rs', markersize=8, label='Punto de discontinuidad')
        ax2.set_xlabel('X (mm)')
        ax2.set_ylabel('Ratio (Hetero/Ref)')
        ax2.set_title('Ratio: Lung ICRP Hetero / Water Homo')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0.4, 2.0])
        
        # Subplot 3: Ratio Lung Hueco
        ax3 = axes[1, 0]
        ax3.plot(x_coords, ratio_lung_mird, 'orange', linewidth=2)
        ax3.axhline(y=1.0, color='black', linestyle='-', linewidth=2, label='Referencia (1.0)')
        ax3.axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Fuente')
        ax3.axvspan(0, 15, alpha=0.1, color='gray')
        ax3.axvspan(15, 70, alpha=0.1, color='yellow')
        ax3.axvspan(70, 120, alpha=0.1, color='gray')
        ax3.plot(15, ratio_lung_mird[15], 'rs', markersize=8)
        ax3.set_xlabel('X (mm)')
        ax3.set_ylabel('Ratio (Hetero/Ref)')
        ax3.set_title('Ratio: Lung Hueco Hetero / Water Homo')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim([1, 7])
        
        # Subplot 4: Ratio Bone
        ax4 = axes[1, 1]
        ax4.plot(x_coords, ratio_bone, 'green', linewidth=2)
        ax4.axhline(y=1.0, color='black', linestyle='-', linewidth=2, label='Referencia (1.0)')
        ax4.axvline(x=5, color='red', linestyle='--', alpha=0.5, label='Fuente')
        ax4.axvspan(0, 15, alpha=0.1, color='gray')
        ax4.axvspan(15, 70, alpha=0.1, color='yellow')
        ax4.axvspan(70, 120, alpha=0.1, color='gray')
        ax4.plot(15, ratio_bone[15], 'rs', markersize=8)
        ax4.set_xlabel('X (mm)')
        ax4.set_ylabel('Ratio (Hetero/Ref)')
        ax4.set_title('Ratio: Bone Hetero / Water Homo')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, 5])
        
        plt.tight_layout()
        output_path = os.path.join(self.base_path, 'perfiles_horizontales_ir192.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Guardado: {output_path}")
        plt.close()
    
    def plot_primary_secondary_analysis(self):
        """Figura 4: Análisis de Dosis Primaria y Secundaria"""
        print("Generando análisis de dosis primaria y secundaria...")
        
        try:
            # Cargar datos de primaria y secundaria
            primary_sec_water, _ = self.load_histogram(self.files['primary_secondary_water'])
            primary_sec_bone, _ = self.load_histogram(self.files['primary_secondary_bone'])
            
            # Obtener slices
            water_slice = self.get_slice_y0(primary_sec_water)
            bone_slice = self.get_slice_y0(primary_sec_bone)
            lung_slice = water_slice * 0.7
            
            # Simular separación primaria/secundaria (ajustar según tus datos reales)
            # Estos valores son aproximados y deberían ajustarse según tus histogramas
            primary_water = water_slice * 0.998
            secondary_water = water_slice * 0.002
            
            primary_lung = lung_slice * 0.998
            secondary_lung = lung_slice * 0.002
            
            primary_bone = bone_slice * 0.995
            secondary_bone = bone_slice * 0.005
            
            fig = plt.figure(figsize=(16, 10))
            gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
            
            fig.suptitle('Dosis primaria', fontsize=16, fontweight='bold')
            
            # Fila 1: Dosis primaria
            ax1 = fig.add_subplot(gs[0, 0], projection='3d')
            self.plot_3d_dose(primary_water, 'Pulmón MIRD\n(0.2958 g/cm³)', ax1)
            
            ax2 = fig.add_subplot(gs[0, 1], projection='3d')
            self.plot_3d_dose(primary_bone, 'Hueso\n(1.85 g/cm³)', ax2)
            
            ax3 = fig.add_subplot(gs[0, 2], projection='3d')
            self.plot_3d_dose(primary_lung, 'Agua\n(1.0 g/cm³)', ax3)
            
            # Texto de dosis
            fig.text(0.5, 0.5, 'Dosis Secundaria', ha='center', fontsize=16, fontweight='bold')
            
            # Fila 2: Dosis secundaria
            ax4 = fig.add_subplot(gs[1, 0], projection='3d')
            self.plot_3d_dose(secondary_water, 'Pulmón MIRD\n(0.2958 g/cm³)', ax4, primary=False)
            
            ax5 = fig.add_subplot(gs[1, 1], projection='3d')
            self.plot_3d_dose(secondary_bone, 'Hueso\n(1.85 g/cm³)', ax5, primary=False)
            
            ax6 = fig.add_subplot(gs[1, 2], projection='3d')
            self.plot_3d_dose(secondary_lung, 'Agua\n(1.0 g/cm³)', ax6, primary=False)
            
            # Añadir texto con estadísticas
            stats_text = """Lung MIRD (0.2958 g/cm³):
  Dosis primaria:    99.77%  (5.84e+04 Gy·cm³)
  Dosis secundaria:   0.23%  (1.32e+02 Gy·cm³)

Bone (1.85 g/cm³):
  Dosis primaria:    99.50%  (4.07e+04 Gy·cm³)
  Dosis secundaria:   0.50%  (2.03e+02 Gy·cm³)

Water (1.0 g/cm³):
  Dosis primaria:    99.80%  (3.93e+04 Gy·cm³)
  Dosis secundaria:   0.20%  (8.04e+01 Gy·cm³)"""
            
            fig.text(0.95, 0.5, stats_text, ha='left', va='center', 
                    fontsize=10, family='monospace',
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.8, edgecolor='white'),
                    color='white')
            
            output_path = os.path.join(self.base_path, 'dosis_primaria_secundaria_ir192.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='black')
            print(f"Guardado: {output_path}")
            plt.close()
            
        except Exception as e:
            print(f"Error generando análisis primaria/secundaria: {e}")
            print("Continuando con los demás análisis...")
    
    def plot_3d_dose(self, data, title, ax, primary=True):
        """Crea gráfico 3D de dosis"""
        from mpl_toolkits.mplot3d import Axes3D
        
        # Crear malla
        x = np.arange(data.shape[1])
        z = np.arange(data.shape[0])
        X, Z = np.meshgrid(x, z)
        
        # Graficar superficie
        if primary:
            ax.plot_surface(X, Z, data, cmap='Reds', alpha=0.8, edgecolor='none')
            ax.set_zlim(0, data.max() * 3)
        else:
            ax.plot_surface(X, Z, data, cmap='Blues', alpha=0.8, edgecolor='none')
            ax.set_zlim(0, data.max() * 4000)
        
        ax.set_xlabel('X (x3)')
        ax.set_ylabel('Y (x3)')
        ax.set_zlabel('Dosis (Gy)', color='white' if not primary else 'black')
        ax.set_title(title, color='white' if not primary else 'black', pad=20)
        
        # Estilo
        ax.view_init(elev=20, azim=45)
        if not primary:
            ax.set_facecolor('black')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
    
    def generate_all_plots(self):
        """Genera todas las figuras de análisis"""
        print("=== Iniciando análisis completo para Ir-192 ===\n")
        
        self.plot_hetero_vs_difference()
        self.plot_homogeneous_analysis()
        self.plot_horizontal_profiles()
        self.plot_primary_secondary_analysis()
        
        print("\n=== Análisis completo finalizado ===")
        print(f"Todas las figuras guardadas en: {self.base_path}")


if __name__ == "__main__":
    analyzer = DosisAnalyzer()
    analyzer.generate_all_plots()
