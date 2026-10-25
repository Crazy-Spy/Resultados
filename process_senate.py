"""
Módulo para coletar e consolidar os dados da Eleição do Senado 2026.
Eleição Ordinária Estadual 2026 (Código 6259, Cargo 5 - Senador).
Cada UF elege 2 senadores em 2026 (renovação de 2/3 do Senado = 54 senadores).
"""

import httpx
import json
import os
import time

UFS = [
    'ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg', 'ms', 'mt',
    'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to'
]

PARTY_COLORS = {
    'PL': '#2563eb',
    'PT': '#dc2626',
    'MDB': '#eab308',
    'PSD': '#0284c7',
    'PP': '#1d4ed8',
    'NOVO': '#ea580c',
    'PSB': '#f97316',
    'REPUBLICANOS': '#0d9488',
    'UNIÃO': '#0891b2',
    'PSDB': '#3b82f6',
    'PODE': '#14b8a6',
    'PDT': '#b91c1c',
    'REDE': '#059669',
    'OUTROS': '#64748b'
}

SENADORES_REMANESCENTES_2022 = {
    'AC': {'nome': 'Alan Rick', 'partido': 'UNIÃO'},
    'AL': {'nome': 'Renan Filho', 'partido': 'MDB'},
    'AM': {'nome': 'Omar Aziz', 'partido': 'PSD'},
    'AP': {'nome': 'Davi Alcolumbre', 'partido': 'UNIÃO'},
    'BA': {'nome': 'Otto Alencar', 'partido': 'PSD'},
    'CE': {'nome': 'Camilo Santana', 'partido': 'PT'},
    'DF': {'nome': 'Damares Alves', 'partido': 'REPUBLICANOS'},
    'ES': {'nome': 'Magno Malta', 'partido': 'PL'},
    'GO': {'nome': 'Wilder Morais', 'partido': 'PL'},
    'MA': {'nome': 'Flávio Dino', 'partido': 'PSB'},
    'MG': {'nome': 'Cleitinho', 'partido': 'PL'},
    'MS': {'nome': 'Tereza Cristina', 'partido': 'PP'},
    'MT': {'nome': 'Wellington Fagundes', 'partido': 'PL'},
    'PA': {'nome': 'Beto Faro', 'partido': 'PT'},
    'PB': {'nome': 'Efraim Filho', 'partido': 'UNIÃO'},
    'PE': {'nome': 'Teresa Leitão', 'partido': 'PT'},
    'PI': {'nome': 'Wellington Dias', 'partido': 'PT'},
    'PR': {'nome': 'Sergio Moro', 'partido': 'UNIÃO'},
    'RJ': {'nome': 'Romário', 'partido': 'PL'},
    'RN': {'nome': 'Rogério Marinho', 'partido': 'PL'},
    'RO': {'nome': 'Jaime Bagattoli', 'partido': 'PL'},
    'RR': {'nome': 'Hiran Gonçalves', 'partido': 'PP'},
    'RS': {'nome': 'Hamilton Mourão', 'partido': 'REPUBLICANOS'},
    'SC': {'nome': 'Jorge Seif', 'partido': 'PL'},
    'SE': {'nome': 'Laércio Oliveira', 'partido': 'PP'},
    'SP': {'nome': 'Marcos Pontes', 'partido': 'PL'},
    'TO': {'nome': 'Professora Dorinha', 'partido': 'UNIÃO'}
}

def coletar_senado_tse():
    ts_now = int(time.time() * 1000)
    headers = {
        "User-Agent": "TSELiveSenate/1.0 (+https://github.com; visualizador eleicoes)",
        "Accept": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    client = httpx.Client(headers=headers, timeout=15.0, follow_redirects=True)

    print("• Coletando dados atualizados do Senado Federal 2026...")
    senado_por_uf = {}
    partidos_eleitos_hoje = {}
    total_eleitos = 0

    for uf_low in UFS:
        uf = uf_low.upper()
        url = f"https://resultados.tse.jus.br/oficial/ele2026/6259/dados/{uf_low}/{uf_low}-c0005-e006259-u.json?_t={ts_now}"
        try:
            r = client.get(url)
            if r.status_code != 200:
                print(f"  [AVISO] Senado UF {uf} retornou status {r.status_code}")
                continue

            data = r.json()
            carg = data.get('carg', [])[0]
            cands = []
            for a in carg.get('agr', []):
                for p in a.get('par', []):
                    for c in p.get('cand', []):
                        vap = int(str(c.get('vap') or 0).replace('.', ''))
                        pvap = float(str(c.get('pvap') or '0').replace('.', '').replace(',', '.'))
                        cands.append({
                            'numero': c.get('n'),
                            'nome': c.get('nm'),
                            'partido': p.get('sg'),
                            'votos': vap,
                            'pct': pvap,
                            'eleito': True
                        })
            cands.sort(key=lambda x: x['votos'], reverse=True)
            top2 = cands[:2]
            total_eleitos += len(top2)

            for s in top2:
                pt = s['partido']
                partidos_eleitos_hoje[pt] = partidos_eleitos_hoje.get(pt, 0) + 1

            p1 = top2[0]['partido'] if len(top2) > 0 else 'OUTROS'
            p2 = top2[1]['partido'] if len(top2) > 1 else 'OUTROS'

            senado_por_uf[uf] = {
                'eleitos': top2,
                'partido_1': p1,
                'partido_2': p2,
                'remanescente_2022': SENADORES_REMANESCENTES_2022.get(uf, {}),
                'demais_candidatos': cands[2:6]
            }
        except Exception as e:
            print(f"  [ERRO] Senado UF {uf}: {e}")

    bancada_total_senado = {}
    for pt, count in partidos_eleitos_hoje.items():
        bancada_total_senado[pt] = bancada_total_senado.get(pt, 0) + count

    for uf, rem in SENADORES_REMANESCENTES_2022.items():
        pt = rem['partido']
        bancada_total_senado[pt] = bancada_total_senado.get(pt, 0) + 1

    ranking_eleitos_hoje = [
        {'partido': pt, 'cadeiras': cnt, 'cor': PARTY_COLORS.get(pt, '#64748b')}
        for pt, cnt in sorted(partidos_eleitos_hoje.items(), key=lambda x: x[1], reverse=True)
    ]

    ranking_bancada_total = [
        {'partido': pt, 'cadeiras': cnt, 'cor': PARTY_COLORS.get(pt, '#64748b')}
        for pt, cnt in sorted(bancada_total_senado.items(), key=lambda x: x[1], reverse=True)
    ]

    senado_dataset = {
        'total_eleitos_hoje': total_eleitos,
        'partidos_eleitos_hoje': ranking_eleitos_hoje,
        'bancada_total_senado_81': ranking_bancada_total,
        'por_uf': senado_por_uf
    }

    db_file = os.path.join(os.path.dirname(__file__), 'election_data.json')
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            database = json.load(f)
        database['senado_2026'] = senado_dataset
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)

    return senado_dataset

if __name__ == '__main__':
    coletar_senado_tse()
