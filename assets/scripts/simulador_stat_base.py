import json
import os
import math

# --- ESPEJO EXACTO DE GameBalance.dart ---
class GameBalance:
    maxLevel = 100
    maxRango = 10
    maxIV = 20
    statsGrowthPerLevel = 0.02
    rankStatBonusPerPoint = 0.01
    characterBonus = 1.10
    characterPenalty = 0.90
    rankSoftCapPoint = 50.0
    rankPostCapBonus = 0.002

def calcular_stat_final(stat_name, base_val, iv_val, mod_crecimiento, nivel, rango, es_up, es_down):
    val_genetico = base_val + iv_val
    val_con_caracter = val_genetico

    if es_up:
        val_con_caracter = round(val_con_caracter * GameBalance.characterBonus)
    elif es_down:
        val_con_caracter = round(val_con_caracter * GameBalance.characterPenalty)

    if nivel > 1:
        level_factor = math.pow(nivel - 1, 0.95)
        growth = val_con_caracter * (GameBalance.statsGrowthPerLevel * mod_crecimiento) * level_factor
        val_leveled = round(val_con_caracter + growth)
    else:
        val_leveled = val_con_caracter

    if rango <= 0:
        return val_leveled

    if rango <= GameBalance.rankSoftCapPoint:
        f_rango = 1.0 + (rango * GameBalance.rankStatBonusPerPoint)
    else:
        f_rango = 1.0 + (50 * GameBalance.rankStatBonusPerPoint) + ((rango - 50) * GameBalance.rankPostCapBonus)

    if stat_name == "velocidad":
        return round(val_leveled * (1.0 + (f_rango - 1.0) * 0.25))

    return round(val_leveled * f_rango)

def analisis_rapido_automatico():
    cid = input("ID del Eco a analizar rápidamente (Ej: E0001): ").upper()
    base_path = os.path.dirname(__file__)
    # Asegúrate de que esta ruta relativa sea correcta para tu estructura de carpetas
    file_path = os.path.join(base_path, f"../data/es/creatures/{cid}.json")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo en {file_path}")
        return

    sb = data['stats_base']
    gm = data['growth_mods']

    # Configuración fija
    lvl = 100
    rng = 0
    iv_u = 20

    all_keys = [
        "vida", "impacto", "magia", "frecuencia", "pulso",
        "barrera_fisica", "barrera_magica", "barrera_mental", "barrera_vital",
        "armadura", "velocidad"
    ]

    suma_bases = sum(sb.get(k, 0) for k in all_keys)
    media_base = suma_bases / len(all_keys)

    print(f"\n{'='*55}")
    print(f" ANÁLISIS RÁPIDO: {data['nombre']} (ID: {cid})")
    print(f" SUMA BASE TOTAL (BST): {suma_bases} | MEDIA BASE: {media_base:.1f}")
    print(f"{'='*55}")
    print(f"{'STAT':<18} | {'BASE':<6} | {'VALOR (Lvl 100)'}")
    print("-" * 55)

    for key in all_keys:
        base = sb.get(key, 0)
        grow = gm.get(key, 1.0)
        # Calculamos con los parámetros fijos: IV20, Nivel 100, Rango 0, Naturaleza Neutra
        v_final = calcular_stat_final(key, base, iv_u, grow, lvl, rng, False, False)
        print(f"{key:<18} | {base:<6} | {v_final}")

    print(f"{'='*55}\n")

if __name__ == "__main__":
    analisis_rapido_automatico()