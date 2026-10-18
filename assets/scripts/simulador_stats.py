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

# Ajustado a tus nuevas stats
NATURALEZAS = {
    "1": ("impacto", "barrera_fisica"),
    "2": ("magia", "barrera_magica"),
    "3": ("frecuencia", "barrera_mental"),
    "4": ("pulso", "barrera_vital"),
    "5": ("velocidad", "vida"),
    "6": ("vida", "velocidad"),
    "7": ("barrera_fisica", "barrera_magica"),
    "8": ("barrera_magica", "barrera_fisica"),
    "9": (None, None)
}

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

def simular_eco_definitivo():
    cid = (input("ID del Eco (Ej: E0001): ") or "E0001").upper()
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, f"../data/es/creatures/{cid}.json")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encuentra {cid}.json en {file_path}")
        return

    sb = data['stats_base']
    gm = data['growth_mods']

    lvl = int(input(f"Nivel (1-100) [{GameBalance.maxLevel}]: ") or 100)
    rng = int(input(f"Rango (0-10) [0]: ") or 0)
    iv_u = int(input(f"IVs deseados (0-20) [{GameBalance.maxIV}]: ") or 20)

    print("\nNaturalezas: 1:Imp/BF, 2:Mag/BMag, 3:Fre/BMen, 4:Pul/BVit, 5:Vel/Vid, 6:Vid/Vel, 7:BF/BMag, 8:BMag/BF, 9:Neutra")
    nat_id = input("Elección [9]: ") or "9"
    stat_up, stat_down = NATURALEZAS.get(nat_id, (None, None))

    # Lista sincronizada con tu nuevo JSON
    all_keys = [
        "vida", "impacto", "magia", "frecuencia", "pulso",
        "barrera_fisica", "barrera_magica", "barrera_mental", "barrera_vital",
        "armadura", "velocidad"
    ]

# 1. Cálculo de media base
# 1. Calculamos la suma total de las bases y su media
    suma_bases = sum(sb.get(k, 0) for k in all_keys)
    media_base = suma_bases / len(all_keys)

    print(f"\n{'='*130}")
    # Ahora mostramos la SUMA TOTAL y la MEDIA
    print(f" ANÁLISIS: {data['nombre']} | Nivel: {lvl} | Rango: {rng}")
    print(f" SUMA BASE TOTAL: {suma_bases} | MEDIA BASE: {media_base:.1f}")
    print(f"{'='*130}")

    # Header limpio
    print(f"{'STAT':<18} | {'BASE':<6} | {'MIN (IV0/N-)':<15} | {'TU ECO (IV'+str(iv_u)+')':<20} | {'MAX (IV20/N+)':<15} | {'BRECHA'}")
    print("-" * 130)

    t_min, t_user, t_max = 0, 0, 0

    for key in all_keys:
        base = sb.get(key, 0)
        grow = gm.get(key, 1.0)

        v_min = calcular_stat_final(key, base, 0, grow, lvl, rng, False, True)
        is_up = (key == stat_up)
        is_down = (key == stat_down)
        v_user = calcular_stat_final(key, base, iv_u, grow, lvl, rng, is_up, is_down)
        v_max = calcular_stat_final(key, base, GameBalance.maxIV, grow, lvl, rng, True, False)

        t_min += v_min
        t_user += v_user
        t_max += v_max

        diff = ((v_max - v_min) / v_min * 100) if v_min > 0 else 0

        # Corregido: Limpiamos los espacios extras
        indicador = ' ▲' if is_up else (' ▼' if is_down else '')
        user_str = f"{v_user}{indicador}"

        print(f"{key:<18} | {base:<6} | {v_min:<15} | {user_str:<20} | {v_max:<15} | {diff:>6.1f}%")
    print("-" * 130)
    total_diff = ((t_max - t_min) / t_min * 100) if t_min > 0 else 0
    print(f"{'TOTAL (BST)':<18} | {'---':<6} | {t_min:<15} | {t_user:<20} | {t_max:<15} | {total_diff:>6.1f}%")
    print(f"{'='*130}\n")

if __name__ == "__main__":
    simular_eco_definitivo()