# DIFERENCIAS ENTRE subtract_histograms.py y subtract_simple.py

## 1. **Escala de Colores (CRITICAL)**

### subtract_histograms.py (original):
```python
vmax = max(np.nanmax(np.abs(diffA)), np.nanmax(np.abs(diffB)))
norm = SymLogNorm(linthresh=1.0, vmin=-vmax, vmax=vmax)
```
- Usa **UN SOLO norm compartido** para ambos paneles
- `linthresh=1.0` es FIJO
- Los dos paneles comparten el rango de colores

### subtract_simple.py (mejorado):
```python
vmaxA = np.nanmax(np.abs(diffA))
vmaxB = np.nanmax(np.abs(diffB))
normA = SymLogNorm(linthresh=max(vmaxA * 0.001, 1.0), vmin=-vmaxA, vmax=vmaxA)
normB = SymLogNorm(linthresh=max(vmaxB * 0.001, 1.0), vmin=-vmaxB, vmax=vmaxB)
```
- Usa **DOS norms INDEPENDIENTES** (uno por panel)
- `linthresh` es **dinámico**: 0.1% del máximo de cada panel
- Cada panel tiene su propio rango de colores optimizado

**IMPACTO:** Si diffA tiene valores 10× más grandes que diffB, el original "comprime" diffB en la visualización.

---

## 2. **Colorbars**

### subtract_histograms.py:
```python
#cbar = fig.colorbar(ims[0], ax=axes.ravel().tolist(), label='Difference (keV) - SymLog')
```
- Comentado, **NO muestra colorbar**

### subtract_simple.py:
```python
plt.colorbar(im, ax=ax, label='Difference (keV)')
```
- **Colorbar individual para cada panel**
- Facilita leer los valores reales en cada panel

---

## 3. **Archivos a Comparar**

### subtract_histograms.py:
```python
fileA1 = "brachytherapy_bone_hetero50m.root"
fileA2 = "brachytherapy_water_homo_50m.root"
titleA = "A: Bone_Hetero - Water_Homo"

fileB1 = "brachytherapy_Lung_Homo_200m.root"
fileB2 = "brachytherapy_Water_Homo200m.root"  # ← NOTA: Water_Homo200m (con 200m)
titleB = "B: Lung_Hetero - Bone_Hetero"
```

### subtract_simple.py:
```python
fileA1 = "brachytherapy_Lung_Homo_200m.root"
fileA2 = "brachytherapy_Water_Homo.root"
titleA = "Lung_Homo_200m - Water_Homo"

fileB1 = "brachytherapy_Water_Homo.root"
fileB2 = "brachytherapy_Lung_Homo_200m.root"
titleB = "Water_Homo - Lung_Homo_200m (inverted)"
```

**DIFERENCIAS:**
- Comparan **DIFERENTES ARCHIVOS**
- subtract_histograms busca `Water_Homo200m` (¿existe?)
- subtract_simple usa `Water_Homo` (existe)

---

## CONCLUSIÓN

Las diferencias visuales se deben a:

1. **Escala diferente:** subtract_simple usa norms independientes y dinámicas
2. **Archivos diferentes:** subtract_histograms intenta usar `Water_Homo200m.root` que podría no existir o ser diferente
3. **Colorbars:** subtract_simple tiene colorbars, subtract_histograms no

**Para comparación justa:**
- Usar los MISMOS archivos en ambos scripts
- O cambiar subtract_histograms a usar norms independientes como subtract_simple
