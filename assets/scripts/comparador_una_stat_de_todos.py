import json
import os
import math

# --- 1. DEFINICIONES NECESARIAS (Copiadas para que el script funcione solo) ---
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

    if es_up: val_con_caracter = round(val_con_caracter * GameBalance.characterBonus)
    elif es_down: val_con_caracter = round(val_con_caracter * GameBalance.characterPenalty)

    if nivel > 1:
        level_factor = math.pow(nivel - 1, 0.95)
        growth = val_con_caracter * (GameBalance.statsGrowthPerLevel * mod_crecimiento) * level_factor
        val_leveled = round(val_con_caracter + growth)
    else:
        val_leveled = val_con_caracter

    if rango <= 0: return val_leveled

    if rango <= GameBalance.rankSoftCapPoint:
        f_rango = 1.0 + (rango * GameBalance.rankStatBonusPerPoint)
    else:
        f_rango = 1.0 + (50 * GameBalance.rankStatBonusPerPoint) + ((rango - 50) * GameBalance.rankPostCapBonus)

    if stat_name == "velocidad":
        return round(val_leveled * (1.0 + (f_rango - 1.0) * 0.25))

    return round(val_leveled * f_rango)

# --- 2. LÓGICA DE COMPARACIÓN ---
def comparar_stats_en_directorio():
    base_path = os.path.dirname(__file__)
    directorio_creatures = os.path.join(base_path, "../data/es/creatures/")

    stats_posibles = [
        "vida", "impacto", "magia", "frecuencia", "pulso",
        "barrera_fisica", "barrera_magica", "barrera_mental", "barrera_vital",
        "armadura", "velocidad"
    ]

    print(f"\nStats disponibles: {', '.join(stats_posibles)}")
    stat_elegida = input("¿Qué estadística quieres comparar?: ").lower()

    if stat_elegida not in stats_posibles:
        print("❌ Stat no válida.")
        return

    lvl = int(input("Nivel para la comparativa (1-100) [100]: ") or 100)

    lista_resultados = []

    for archivo in os.listdir(directorio_creatures):
        if archivo.startswith("E") and archivo.endswith(".json"):
            with open(os.path.join(directorio_creatures, archivo), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    base = data['stats_base'].get(stat_elegida, 0)
                    grow = data['growth_mods'].get(stat_elegida, 1.0)

                    # IV 10, sin naturaleza (Neutro)
                    valor = calcular_stat_final(stat_elegida, base, 10, grow, lvl, 0, False, False)

                    lista_resultados.append({"nombre": data['nombre'], "valor": valor})
                except KeyError as e:
                    print(f"Error procesando {archivo}: falta {e}")

    # Ordenar de mayor a menor
    lista_resultados.sort(key=lambda x: x['valor'], reverse=True)

    print(f"\n{'='*40}")
    print(f" RANKING: {stat_elegida.upper()} (Nivel {lvl})")
    print(f"{'='*40}")
    for i, item in enumerate(lista_resultados, 1):
        print(f"{i}. {item['nombre']:<20} | {item['valor']} pts")
    print(f"{'='*40}\n")

if __name__ == "__main__":
    comparar_stats_en_directorio()