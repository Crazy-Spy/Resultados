"""
Script de Atualização Automática dos Dados da Eleição de Hoje (TSE).
Consulta a API pública do TSE em tempo real (Presidente e Senado),
atualiza a base 'election_data.json' e reconstrói o 'index.html'.

Uso:
    python atualizar_dados.py
"""

import httpx
import json
import os
import sys
import time

UFS = [
    'ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg', 'ms', 'mt',
    'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to'
]

BASE_URL = "https://resultados.tse.jus.br/oficial"
ELEICAO_ID = "6258"  # Eleição Ordinária Federal - 2026 2º Turno (Presidente)
CICLO = "ele2026"

def parse_num(val, default=0):
    try:
        return int(str(val).replace(".", "").strip())
    except Exception:
        return default

def parse_float(val, default=0.0):
    try:
        return float(str(val).replace(".", "").replace(",", ".").strip())
    except Exception:
        return default

def coletar_dados_tse():
    ts_now = int(time.time() * 1000)
    headers = {
        "User-Agent": "TSELiveCollector/1.0 (+https://github.com; visualizador eleicoes)",
        "Accept": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    client = httpx.Client(headers=headers, timeout=15.0, follow_redirects=True)

    print("=" * 68)
    print("  COLETANDO DADOS DA ELEICAO DE HOJE DIRETAMENTE DA API DO TSE")
    print("=" * 68)
    print(f"  Ciclo: {CICLO} | Codigo Eleicao: {ELEICAO_ID} (Presidente da Republica - 2º Turno)")
    print(f"  Data do Pleito: 25/10/2026 | Requisicao timestamp: {ts_now}")
    print("-" * 68)

    # 1. Obter Total Nacional (BR) com cache-buster
    url_br = f"{BASE_URL}/{CICLO}/{ELEICAO_ID}/dados/br/br-c0001-e00{ELEICAO_ID}-u.json?_t={ts_now}"
    print("[1/3] Consultando totalizacao Brasil (BR)...")
    r_br = client.get(url_br)
    r_br.raise_for_status()
    br_json = r_br.json()

    timestamp_br = f"{br_json.get('dg', '')} {br_json.get('hg', '')}".strip()
    secoes_br = br_json.get('s', {})
    apurado_pct_br = parse_float(secoes_br.get('pst', '0'))
    
    # Extrair candidatos nacionais (2º Turno: somente 2 candidatos)
    candidatos_br = []
    carg_br = br_json.get('carg', [])[0]
    for a in carg_br.get('agr', []):
        for p in a.get('par', []):
            for c in p.get('cand', []):
                candidatos_br.append({
                    'numero': c.get('n'),
                    'nome': c.get('nm'),
                    'partido': p.get('sg'),
                    'votos': parse_num(c.get('vap')),
                    'pct': parse_float(c.get('pvap')),
                    'eleito': c.get('e') == 's'
                })
    candidatos_br.sort(key=lambda x: x['votos'], reverse=True)

    # Localizar Bolsonaro e Lula
    bolso_br = next((c for c in candidatos_br if c['numero'] == '22'), {'votos': 0, 'pct': 0.0, 'nome': 'FLAVIO NANTES BOLSONARO'})
    lula_br = next((c for c in candidatos_br if c['numero'] == '13'), {'votos': 0, 'pct': 0.0, 'nome': 'LUIZ INÁCIO LULA DA SILVA'})

    votos_info = br_json.get('v', {})
    eleitorado_info = br_json.get('e', {})

    if bolso_br['votos'] > lula_br['votos']:
        vencedor_nacional = 'Bolsonaro'
    elif lula_br['votos'] > bolso_br['votos']:
        vencedor_nacional = 'Lula'
    else:
        vencedor_nacional = 'Aguardando' if apurado_pct_br == 0 else 'Empate'

    nacional_hoje = {
        'timestamp': timestamp_br,
        'turno': 2,
        'pleito_data': '25/10/2026',
        'descricao': '2º Turno Presidencial (25/10/2026)',
        'apurado_pct': apurado_pct_br,
        'secoes_total': parse_num(secoes_br.get('ts')),
        'secoes_apuradas': parse_num(secoes_br.get('st')),
        'lula_votos': lula_br['votos'],
        'lula_pct': lula_br['pct'],
        'lula_nome': lula_br['nome'],
        'bolsonaro_votos': bolso_br['votos'],
        'bolsonaro_pct': bolso_br['pct'],
        'bolsonaro_nome': bolso_br['nome'],
        'outros_candidatos': [],
        'votos_validos': parse_num(votos_info.get('vv')),
        'brancos_votos': parse_num(votos_info.get('vb')),
        'brancos_pct': parse_float(votos_info.get('pvb')),
        'nulos_votos': parse_num(votos_info.get('tvn')),
        'nulos_pct': parse_float(votos_info.get('ptvn')),
        'abstencao_votos': parse_num(eleitorado_info.get('a')),
        'abstencao_pct': parse_float(eleitorado_info.get('pa')),
        'eleitorado_total': parse_num(eleitorado_info.get('te')),
        'vencedor': vencedor_nacional,
        'estados_lula': 0,
        'estados_bolsonaro': 0
    }

    # 2. Obter Dados de Cada UF
    print("[2/3] Consultando dados das 27 UFs para Presidente (2º Turno)...")
    estados_hoje = {}

    for uf_low in UFS:
        uf = uf_low.upper()
        url_uf = f"{BASE_URL}/{CICLO}/{ELEICAO_ID}/dados/{uf_low}/{uf_low}-c0001-e00{ELEICAO_ID}-u.json?_t={ts_now}"
        try:
            r_uf = client.get(url_uf)
            if r_uf.status_code != 200:
                print(f"  [AVISO] UF {uf} retornou status {r_uf.status_code}")
                continue

            uf_json = r_uf.json()
            carg_uf = uf_json.get('carg', [])[0]
            
            cands_uf = {}
            for a in carg_uf.get('agr', []):
                for p in a.get('par', []):
                    for c in p.get('cand', []):
                        num = c.get('n')
                        cands_uf[num] = {
                            'nome': c.get('nm'),
                            'partido': p.get('sg'),
                            'votos': parse_num(c.get('vap')),
                            'pct': parse_float(c.get('pvap'))
                        }

            b_uf = cands_uf.get('22', {'votos': 0, 'pct': 0.0, 'nome': 'FLAVIO NANTES BOLSONARO'})
            l_uf = cands_uf.get('13', {'votos': 0, 'pct': 0.0, 'nome': 'LUIZ INÁCIO LULA DA SILVA'})

            v_uf = uf_json.get('v', {})
            e_uf = uf_json.get('e', {})
            s_uf = uf_json.get('s', {})

            if b_uf['votos'] > l_uf['votos']:
                vencedor = 'Bolsonaro'
                nacional_hoje['estados_bolsonaro'] += 1
            elif l_uf['votos'] > b_uf['votos']:
                vencedor = 'Lula'
                nacional_hoje['estados_lula'] += 1
            else:
                vencedor = 'Aguardando'

            margem_pct = round(abs(l_uf['pct'] - b_uf['pct']), 2)
            margem_votos = abs(l_uf['votos'] - b_uf['votos'])

            estados_hoje[uf] = {
                'timestamp': f"{uf_json.get('dg', '')} {uf_json.get('hg', '')}".strip(),
                'secoes_total': parse_num(s_uf.get('ts')),
                'secoes_apuradas': parse_num(s_uf.get('st')),
                'apurado_pct': parse_float(s_uf.get('pst')),
                'eleitorado': parse_num(e_uf.get('te')),
                'abstencao': parse_num(e_uf.get('a')),
                'abstencao_pct': parse_float(e_uf.get('pa')),
                'lula_votos': l_uf['votos'],
                'lula_pct': l_uf['pct'],
                'lula_nome': l_uf.get('nome', 'LUIZ INÁCIO LULA DA SILVA'),
                'bolsonaro_votos': b_uf['votos'],
                'bolsonaro_pct': b_uf['pct'],
                'bolsonaro_nome': b_uf.get('nome', 'FLAVIO NANTES BOLSONARO'),
                'vencedor': vencedor,
                'margem_pct': margem_pct,
                'margem_votos': margem_votos,
                'brancos_votos': parse_num(v_uf.get('vb')),
                'brancos_pct': parse_float(v_uf.get('pvb')),
                'nulos_votos': parse_num(v_uf.get('tvn')),
                'nulos_pct': parse_float(v_uf.get('ptvn')),
                'votos_validos': parse_num(v_uf.get('vv')),
                'outros': []
            }
        except Exception as e:
            print(f"  [ERRO] UF {uf}: {e}")

    # 3. Atualizar election_data.json preservando 1º turno de 2026
    db_file = os.path.join(os.path.dirname(__file__), 'election_data.json')
    with open(db_file, 'r', encoding='utf-8') as f:
        database = json.load(f)

    # Preservar dados consolidados do 1º turno de 2026 (04/10) caso ainda não salvos
    if 'turno1_2026_nacional' not in database and 'hoje_2026_nacional' in database:
        database['turno1_2026_nacional'] = database['hoje_2026_nacional']
    for uf_k in database.get('estados', {}):
        if 'turno1_2026' not in database['estados'][uf_k] and 'hoje_2026' in database['estados'][uf_k]:
            database['estados'][uf_k]['turno1_2026'] = database['estados'][uf_k]['hoje_2026']

    # Gravar o 2º Turno como os dados ativos de hoje
    database['hoje_2026_nacional'] = nacional_hoje
    for uf, d_uf in estados_hoje.items():
        if uf in database['estados']:
            database['estados'][uf]['hoje_2026'] = d_uf

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

    # 4. Dados do Senado 2026 (eleitos no 1º turno, já definidos)
    if 'senado_2026' not in database or not database['senado_2026']:
        print("[3/3] Consultando dados do Senado Federal (Eleicao 6259)...")
        try:
            from process_senate import coletar_senado_tse
            coletar_senado_tse()
        except Exception as e:
            print(f"  [AVISO] Falha ao coletar dados do Senado: {e}")
    else:
        print("[3/3] Bancada do Senado já consolidada com 54 eleitos do 1º Turno.")

    # Recarregar database completa
    with open(db_file, 'r', encoding='utf-8') as f:
        database = json.load(f)

    # 5. Reconstruir index.html e chat artifact
    try:
        import importlib
        import build_html
        importlib.reload(build_html)
        build_html.rebuild_html(database)
    except Exception as e:
        print(f"  [AVISO] Nao foi possivel reconstruir index.html: {e}")

    try:
        import importlib
        import build_artifact
        importlib.reload(build_artifact)
        build_artifact.rebuild_artifact(database)
    except Exception as e:
        print(f"  [AVISO] Nao foi possivel reconstruir chat artifact: {e}")

    print("\n[OK] Base de dados e interface index.html atualizadas com sucesso!")
    print("-" * 68)
    print(f"  STATUS NACIONAL HOJE ({nacional_hoje['timestamp']}):")
    print(f"  - Apuracao: {nacional_hoje['apurado_pct']}%")
    print(f"  - {bolso_br['nome']}: {bolso_br['pct']}% ({bolso_br['votos']:,} votos)")
    print(f"  - {lula_br['nome']}: {lula_br['pct']}% ({lula_br['votos']:,} votos)")
    print(f"  - Estados: Bolsonaro {nacional_hoje['estados_bolsonaro']} x {nacional_hoje['estados_lula']} Lula")
    print("=" * 68)

    return database

if __name__ == '__main__':
    coletar_dados_tse()
