#
# Análisis del Problema: PRIMARY y SECONDARY VACÍOS
#

## Definición Física Correcta

**PRIMARY particles (carriers):**
- Electrones/positrones producidos directamente por gamma (photoelectric, Compton, pair production)
- Estos son los que transportan energía desde el fotón al material

**SECONDARY particles:**
- Todas las otras partículas (bremsstrahlung, fluorescencia, etc.)
- O energía depositada por el gamma mismo

## Código Actual (PROBLEMA)

En BrachyTrackingAction::PostUserTrackingAction (línea 79):

```cpp
if (charge != 0.0 && parentIsGamma && parentPhotonLineage) {
  info->SetPrimaryDoseCarrier(true);
}
```

**Restricciones problemáticas:**
1. Requiere parentPhotonLineage = true
2. Requiere parentIsGamma = true
3. Requiere charge != 0

**Problema 1:** Si el electrón es el primer charged que lo marca como primary,
pero ese electrón puede haber sido creado en múltiples pasos (ionización, colisión).

**Problema 2:** No toda la energía que deposits el electrón es "primary" - 
algunos depósitos pueden ser secundarios.

## Solución Correcta

La definición debe ser:
- **PRIMARY:** Energía depositada DIRECTAMENTE por primeros charged secundarios del gamma
- **SECONDARY:** Todo lo demás

Esto se implementa mejor con:
1. Marcar el PRIMER charged que viene de un gamma como "primary"
2. Todos los descendientes de ese primary también son "primary"
3. Todo lo que NOT viene de ese linaje es "secondary"

O más simple:
- Si el padre inmediato es un gamma: PRIMARY
- Si no: SECONDARY

## Implementación Recomendada

Cambiar la lógica a:

```cpp
// A charged particle whose direct parent is a gamma
// is a primary dose carrier
if (charge != 0.0 && parentIsGamma) {
  info->SetPrimaryDoseCarrier(true);
}

// All descendants of a primary inherit the primary status
if (charge != 0.0 && !parentIsGamma && parentInfo->IsPrimaryDoseCarrier()) {
  info->SetPrimaryDoseCarrier(true);
}
```

Esto NO requiere photonLineage check.
