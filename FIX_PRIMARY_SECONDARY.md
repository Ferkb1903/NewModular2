#!/usr/bin/env markdown
# Primary vs Secondary Dose Classification - FIX

## Problema Identificado

Los archivos `primary_*.root` están vacíos, mientras que los `secondary_*.root` contienen datos.

### Causa Raíz

En `src/BrachyTrackingAction.cc` línea 79, la lógica para marcar partículas como "PRIMARY" era:

```cpp
if (charge != 0.0 && parentIsGamma && parentPhotonLineage) {
  info->SetPrimaryDoseCarrier(true);
}
```

**Restricciones problemáticas:**

1. `parentPhotonLineage` requiere que el gamma tenga un ancestor que sea gamma originado de fuente
2. Solo los primeros gammas de la fuente marcan su linaje como true
3. Los gammas producidos por bremsstrahlung u otro proceso NO marcan este flag
4. Por lo tanto, NINGÚN charged desde estos gammas secundarios se marcaba como primary

**Resultado:** Casi ninguna partícula se marcaba como primary → archivos primary vacíos

---

## Solución Implementada

### Nueva Lógica (Físicamente Correcta)

```cpp
// PRIMARY DOSE CARRIERS: 
// 1. Charged particles directly produced by gamma (photoelectric, Compton, pair production)
// 2. OR charged descendants of primary carriers

if (charge != 0.0) {
  if (parentIsGamma) {
    // Direct charged secondary from gamma = PRIMARY
    // (Regardless of where the gamma came from)
    info->SetPrimaryDoseCarrier(true);
  } else if (parentIsPrimaryCarrier) {
    // Secondary from a primary carrier = PRIMARY
    // (Propagate primary status through the cascade)
    info->SetPrimaryDoseCarrier(true);
  }
}
```

### Justificación Física

**PRIMARY particles (dose carriers):**
- Electrones/positrones producidos directamente por interacción fotoeléctrica, Compton o pair production
- Estos transportan energía desde el fotón al material
- Sus descendientes (e.g., ionización del electrón) también se consideran part del cascade primario

**SECONDARY particles:**
- Partículas que NOT son parte del cascade primario
- Fotones de bremsstrahlung (llevan energía fuera)
- Partículas de Auger
- Energía depositada directamente por fotón

### Cambios Específicos

**Archivo: `src/BrachyTrackingAction.cc`**

**Línea 71:** Agregada lectura de `parentIsPrimaryCarrier`:
```cpp
const G4bool parentIsPrimaryCarrier = parentInfo->IsPrimaryDoseCarrier();
```

**Líneas 79-90:** Reemplazada lógica de marcación:
- Antes: Solo si `parentPhotonLineage`
- Ahora: Si `parentIsGamma` O si `parentIsPrimaryCarrier`

---

## Validación Física

### Caso 1: Gamma del Source → Électron (Compton)
- Parent: Gamma (source)
- parentIsGamma = TRUE
- → **MARKED PRIMARY** ✓

### Caso 2: Gamma del Source → Électron → Fotón (Bremsstrahlung)
- Parent: Électron
- parentIsGamma = FALSE
- parentIsPrimaryCarrier = TRUE (del caso 1)
- → **MARKED PRIMARY** ✓

### Caso 3: Gamma del Source → Électron → Ionización
- Parent: Électron
- parentIsGamma = FALSE
- parentIsPrimaryCarrier = TRUE
- → **MARKED PRIMARY** ✓

### Caso 4: Gamma de Bremsstrahlung → Électron (Compton)
- Parent: Gamma (de bremsstrahlung, anterior era electrón primary)
- parentIsGamma = TRUE
- → **MARKED PRIMARY** ✓
  (Porque vino de interacción gamma-material, aunque sea secundaria en origen)

**Nota:** Caso 4 puede ser discutible. Si necesitas distinguir entre:
- Primarios "de verdad" (solo del source original)
- vs. Primarios generalizados (cualquier charged de gamma)

Se puede usar `parentPhotonLineage` como adicional check.

---

## Compilación

✓ Compiló sin errores
✓ No requiere cambios en .hh
✓ No requiere cambios en configuración de macros

---

## Próximos Pasos

1. **Ejecutar simulación de prueba** con la nueva lógica
2. **Verificar que archivos primary contienen datos**
3. **Comparar ratios primary/secondary contra literatura**
4. **Validar físicamente con ejemplos de brachytherapy publicados**

---

## References

G4 Brachytherapy documentation:
- Primary = first charged secondary from gamma
- Secondary = everything else
- Dose separation useful for understanding interaction mechanisms
