import re
import os
import itertools

def ejecutar_auditoria_maestra():
    # --- CONFIGURACIÓN DE RUTAS ---
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "../../lib/core/constants/type_chart.dart")

    if not os.path.exists(file_path):
        print(f"❌ ERROR: No se encuentra el archivo en {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- EXTRACCIÓN DE DATOS ---
    type_blocks = re.findall(r'AttackType\.(\w+):\s*\{([^}]+)\}', content)
    matrix = {}
    tipos = set()

    for attacker, inner in type_blocks:
        matrix[attacker] = {}
        matches = re.findall(r'AttackType\.(\w+):\s*([\d.]+)', inner)
        for defender, value in matches:
            matrix[attacker][defender] = float(value)
            tipos.add(defender)
        tipos.add(attacker)

    lista_tipos = sorted(list(tipos))
    n = len(lista_tipos)

    # --- 1. RANKING INDIVIDUAL COMPLETO ---
    print("\n" + "═"*115)
    print(f"📊 REPORTE GLOBAL DE BALANCE INDIVIDUAL (Total Tipos: {n})")
    print("═"*115)
    print(f"{'TIPO':<15} | {'OFENSA':<8} | {'DEFENSA':<8} | {'NETO':<8} | {'DEB++':<5} | {'RES++':<5} | {'INMU':<4} | {'STATUS'}")
    print("-" * 115)

    reporte_ind = []
    for t in lista_tipos:
        of_sum = sum(matrix.get(t, {}).get(d, 1.0) for d in lista_tipos)
        df_sum = sum(matrix.get(a, {}).get(t, 1.0) for a in lista_tipos)
        deb_heavy = sum(1 for a in lista_tipos if matrix.get(a, {}).get(t, 1.0) >= 1.7)
        res_heavy = sum(1 for a in lista_tipos if 0.0 < matrix.get(a, {}).get(t, 1.0) <= 0.3)
        inmunes = sum(1 for a in lista_tipos if matrix.get(a, {}).get(t, 1.0) == 0.0)

        neto = of_sum - df_sum
        status = "🔥 [OP]" if neto > 8 else ("💀 [DEBIL]" if neto < -8 else "⚖️ [OK]")

        reporte_ind.append({
            't': t, 'of': of_sum, 'df': df_sum, 'neto': neto,
            'dh': deb_heavy, 'rh': res_heavy, 'in': inmunes, 'st': status
        })

    # Ordenar por Neto de mayor a menor
    reporte_ind.sort(key=lambda x: x['neto'], reverse=True)

    for r in reporte_ind:
        print(f"{r['t']:<15} | {r['of']:<8.2f} | {r['df']:<8.2f} | {r['neto']:>7.2f} | {r['dh']:<5} | {r['rh']:<5} | {r['in']:<4} | {r['st']}")

    # --- 2. AUDITORÍA DE DÚOS (COMBINACIONES) ---
    print("\n" + "═"*115)
    print("⚔️  RANKING DE DÚOS: SINERGIAS, MUROS Y PELIGROS (Top 25)")
    print("═"*115)

    combos = list(itertools.combinations(lista_tipos, 2))
    res_duos = []

    for t1, t2 in combos:
        df_total = 0.0
        vulnerabilidades_x4 = []
        resistencias_x025 = []
        sinergia_anulacion = 0 # Uno es débil y el otro lo salva

        for atk in lista_tipos:
            v1 = matrix.get(atk, {}).get(t1, 1.0)
            v2 = matrix.get(atk, {}).get(t2, 1.0)
            final = v1 * v2
            df_total += final

            if final >= 3.0: vulnerabilidades_x4.append(f"{atk}(x{final:.1f})")
            if 0.0 < final <= 0.25: resistencias_x025.append(atk)
            if (v1 > 1.0 and v2 < 1.0) or (v1 < 1.0 and v2 > 1.0):
                sinergia_anulacion += 1

        res_duos.append({
            'nombre': f"{t1}/{t2}",
            'df_total': df_total,
            'crit': vulnerabilidades_x4,
            'res_ext': resistencias_x025,
            'siner': sinergia_anulacion
        })

    # --- RANKING A: LOS MUROS (Menor daño recibido total) ---
    print(f"\n🛡️  TOP 15: MUROS IMPENETRABLES (Menos daño recibido total)")
    res_duos.sort(key=lambda x: x['df_total'])
    for i, d in enumerate(res_duos[:15], 1):
        print(f"{i:>2}. {d['nombre']:<25} | Score Def: {d['df_total']:>6.2f} | Res++: {len(d['res_ext'])}")

    # --- RANKING B: SINERGIA (Mejor cobertura mutua) ---
    print(f"\n🤝 TOP 15: SINERGIA PERFECTA (Tipos que se cubren entre sí)")
    res_duos.sort(key=lambda x: x['siner'], reverse=True)
    for i, d in enumerate(res_duos[:15], 1):
        print(f"{i:>2}. {d['nombre']:<25} | Debilidades Anuladas: {d['siner']}")

    # --- RANKING C: VULNERABILIDAD (Los más fáciles de matar) ---
    print(f"\n💀 TOP 15: COMBOS FRÁGILES (Más debilidades x3.0 o x4.0)")
    res_duos.sort(key=lambda x: len(x['crit']), reverse=True)
    for i, d in enumerate(res_duos[:15], 1):
        vuln_str = ", ".join(d['crit'][:3])
        print(f"{i:>2}. {d['nombre']:<25} | Debilidades Críticas: {len(d['crit'])} [{vuln_str}...]")

    # --- SECCIÓN CRÍTICA: BÚSQUEDA DE ECOS IMBATIBLES ---
    print("\n" + "═"*115)
    print("🔍 ALERTA DE DISEÑO: COMBINACIONES SIN DEBILIDADES (>1.0)")
    print("═"*115)

    imbatibles = [d for d in res_duos if not any(matrix.get(a, {}).get(d['nombre'].split('/')[0], 1.0) * matrix.get(a, {}).get(d['nombre'].split('/')[1], 1.0) > 1.0
                                              for a in lista_tipos)]

    if imbatibles:
        for p in imbatibles:
            print(f"⚠️  ALERTA: {p['nombre']} no tiene debilidades. Es un 'God-Tier'.")
    else:
        print("✅ No hay combinaciones invencibles. Todos los Ecos tienen al menos un punto débil.")

if __name__ == "__main__":
    ejecutar_auditoria_maestra()