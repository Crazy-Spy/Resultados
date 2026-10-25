import json
import os

def rebuild_artifact(data=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data is None:
        db_file = os.path.join(base_dir, 'election_data.json')
        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

    json_str = json.dumps(data, ensure_ascii=False)

    artifact_html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .state-path {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      stroke-width: 1.2;
    }}
    .state-path:hover {{
      filter: brightness(1.2) drop-shadow(0 4px 6px rgba(0,0,0,0.35));
      stroke: #ffffff;
      stroke-width: 2.2;
    }}
    .state-path.selected {{
      stroke: #facc15 !important;
      stroke-width: 3 !important;
      filter: drop-shadow(0 0 10px rgba(250, 204, 21, 0.6));
    }}
    .pulse-live {{
      animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.95); }}
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: rgba(100, 116, 139, 0.4);
      border-radius: 3px;
    }}
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-2 sm:p-4">

  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-2xl p-4 sm:p-6 shadow-md space-y-5">

    <!-- HEADER -->
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)] pb-3">
      <div>
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-rose-600 pulse-live"></span>
          <h2 class="text-[var(--foreground)] font-bold text-lg tracking-tight">
            Eleições 2026: 2º Turno Presidencial & Composição do Senado
          </h2>
          <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
            TSE AO VIVO
          </span>
        </div>
        <p class="text-[var(--muted-foreground)] text-xs mt-0.5">
          Pleito de Hoje (25/10/2026) • Totalização Oficial em Tempo Real
        </p>
      </div>

      <!-- VIEW TOGGLE -->
      <div class="flex items-center bg-[var(--background)] p-1 rounded-xl border border-[var(--border)]">
        <button id="art-btn-pres" onclick="setMode('presidente')" class="px-3 py-1 rounded-lg text-xs font-bold transition bg-rose-600 text-white shadow-sm flex items-center gap-1.5">
          🗳️ Presidente (2º Turno)
        </button>
        <button id="art-btn-sen" onclick="setMode('senado')" class="px-3 py-1 rounded-lg text-xs font-semibold transition text-[var(--muted-foreground)] hover:text-[var(--foreground)] flex items-center gap-1.5">
          🏛️ Senado (Bancadas)
        </button>
      </div>
    </div>

    <!-- ================= PRESIDENTIAL VIEW (DEFAULT) ================= -->
    <div id="art-view-presidente" class="space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="bg-[var(--background)] border border-blue-500/30 rounded-xl p-3 space-y-1">
          <div class="flex justify-between text-xs">
            <span class="font-bold text-blue-500">Flávio Bolsonaro (PL)</span>
            <span id="art-pres-bolso-badge" class="px-2 py-0.5 rounded bg-blue-500/10 text-blue-500 text-xs font-bold">-</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-blue-500" id="art-pres-bolso-pct">0,00%</span>
            <span class="text-xs text-[var(--muted-foreground)] font-mono" id="art-pres-bolso-votos">0 votos</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block pt-1 border-t border-[var(--border)]" id="art-pres-bolso-estados">0 UFs à frente</span>
        </div>

        <div class="bg-[var(--background)] border border-rose-500/30 rounded-xl p-3 space-y-1">
          <div class="flex justify-between text-xs">
            <span class="font-bold text-rose-500">Lula (PT)</span>
            <span id="art-pres-lula-badge" class="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 text-xs font-bold">-</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-rose-500" id="art-pres-lula-pct">0,00%</span>
            <span class="text-xs text-[var(--muted-foreground)] font-mono" id="art-pres-lula-votos">0 votos</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block pt-1 border-t border-[var(--border)]" id="art-pres-lula-estados">0 UFs à frente</span>
        </div>

        <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">Diferença</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-emerald-500" id="art-pres-diff-pct">0,00%</span>
            <span class="text-xs text-[var(--muted-foreground)] font-mono" id="art-pres-diff-votos">0 votos</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block pt-1 border-t border-[var(--border)]" id="art-pres-valid-votos">Válidos: 0</span>
        </div>

        <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">Totalização TSE</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-[var(--foreground)] font-mono" id="art-pres-apurado-pct">0,00%</span>
            <span class="text-xs text-emerald-500 font-bold">Ao Vivo</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block pt-1 border-t border-[var(--border)]" id="art-pres-timestamp">Boletim TSE: Hoje</span>
        </div>
      </div>

      <!-- Presidential Map -->
      <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-4">
        <div class="flex justify-between items-center pb-2 border-b border-[var(--border)] text-xs mb-2">
          <span class="font-bold text-[var(--foreground)]">Mapa do 2º Turno (Azul: Bolsonaro | Vermelho: Lula | Cinza: Aguardando)</span>
          <span class="text-[var(--muted-foreground)]">Passe o mouse para inspecionar</span>
        </div>
        <div class="relative py-2 flex items-center justify-center min-h-[360px]">
          <svg id="art-pres-svg" viewBox="0 0 800 800" class="w-full h-full max-h-[440px]">
            <g id="art-pres-paths"></g>
            <g id="art-pres-labels"></g>
          </svg>
        </div>
      </div>
    </div>

    <!-- ================= SENATE VIEW ================= -->
    <div id="art-view-senado" class="hidden space-y-4">
      
      <!-- Key Stats Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="bg-[var(--background)] border border-blue-500/30 rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">Maior Bancada Eleita</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-blue-500">20</span>
            <span class="text-xs font-bold text-[var(--foreground)]">Senadores (PL)</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block">37,0% das 54 vagas de hoje</span>
        </div>

        <div class="bg-[var(--background)] border border-amber-500/30 rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">2ª & 3ª Bancadas</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-amber-500">7</span>
            <span class="text-xs text-[var(--muted-foreground)]">MDB</span>
            <span class="text-2xl font-black text-sky-500 ml-2">7</span>
            <span class="text-xs text-[var(--muted-foreground)]">PSD</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block">Grandes bancadas de centro</span>
        </div>

        <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">Vagas Renovadas</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-[var(--foreground)]">54</span>
            <span class="text-xs text-[var(--muted-foreground)]">de 81 cadeiras</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block">2/3 da Casa renovados</span>
        </div>

        <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-3 space-y-1">
          <span class="text-xs text-[var(--muted-foreground)] uppercase font-semibold">Totalização</span>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-emerald-500">100%</span>
            <span class="text-xs text-[var(--muted-foreground)]">Apurado</span>
          </div>
          <span class="text-xs text-[var(--muted-foreground)] block">54 senadores definidos no 1º T</span>
        </div>
      </div>

      <!-- Senate Proportional Bar & Grid -->
      <div class="bg-[var(--background)] border border-[var(--border)] rounded-xl p-4 space-y-3">
        <span class="text-xs font-bold text-[var(--foreground)]">Distribuição das 54 Vagas Eleitas:</span>
        <div class="w-full bg-slate-800 h-4 rounded-lg overflow-hidden flex shadow-inner" id="art-sen-bar"></div>
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 pt-1" id="art-sen-grid"></div>
      </div>

      <!-- Senate Map & Details -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
        <div class="md:col-span-7 bg-[var(--background)] border border-[var(--border)] rounded-xl p-4">
          <span class="text-xs font-bold text-[var(--foreground)] block mb-2">Mapa das Eleições para o Senado</span>
          <div class="relative py-2 flex items-center justify-center min-h-[300px]">
            <svg id="art-sen-svg" viewBox="0 0 800 800" class="w-full h-full max-h-[380px]">
              <g id="art-sen-paths"></g>
              <g id="art-sen-labels"></g>
            </svg>
          </div>
        </div>

        <div class="md:col-span-5 bg-[var(--background)] border border-[var(--border)] rounded-xl p-4 space-y-3 flex flex-col justify-between">
          <div>
            <div class="flex justify-between items-center border-b border-[var(--border)] pb-2 mb-3">
              <div>
                <span id="art-insp-uf" class="text-xl font-black text-[var(--foreground)] font-mono">SP</span>
                <span id="art-insp-nome" class="text-xs text-[var(--muted-foreground)] ml-1">São Paulo</span>
              </div>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-500">2 Eleitos</span>
            </div>

            <div class="space-y-2 text-xs">
              <div id="art-sen-card1" class="bg-[var(--card)] p-2.5 rounded-lg border border-[var(--border)] space-y-1"></div>
              <div id="art-sen-card2" class="bg-[var(--card)] p-2.5 rounded-lg border border-[var(--border)] space-y-1"></div>
            </div>
          </div>

          <div class="text-[11px] text-[var(--muted-foreground)] pt-2 border-t border-[var(--border)] flex justify-between">
            <span>Senador 2022-2030: <strong id="art-rem-nome" class="text-[var(--foreground)]">Marcos Pontes (PL)</strong></span>
          </div>
        </div>
      </div>

    </div>

  </div>

  <script>
    let DATA = {json_str};
    let currentMode = 'presidente';

    const PARTY_COLORS = {{
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
    }};

    function init() {{
      setMode('presidente');
      renderPresView();
      renderSenateBars();
      renderSenateMap();
      inspectSenateState('SP');
    }}

    function setMode(mode) {{
      currentMode = mode;
      const bSen = document.getElementById('art-btn-sen');
      const bPres = document.getElementById('art-btn-pres');
      const vSen = document.getElementById('art-view-senado');
      const vPres = document.getElementById('art-view-presidente');

      if (mode === 'presidente') {{
        bPres.className = 'px-3 py-1 rounded-lg text-xs font-bold transition bg-rose-600 text-white shadow-sm flex items-center gap-1.5';
        bSen.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition text-[var(--muted-foreground)] hover:text-[var(--foreground)] flex items-center gap-1.5';
        vPres.classList.remove('hidden');
        vSen.classList.add('hidden');
      }} else {{
        bSen.className = 'px-3 py-1 rounded-lg text-xs font-bold transition bg-blue-600 text-white shadow-sm flex items-center gap-1.5';
        bPres.className = 'px-3 py-1 rounded-lg text-xs font-semibold transition text-[var(--muted-foreground)] hover:text-[var(--foreground)] flex items-center gap-1.5';
        vSen.classList.remove('hidden');
        vPres.classList.add('hidden');
      }}
    }}

    function renderPresView() {{
      const nac = DATA.hoje_2026_nacional || {{}};
      const apurado = nac.apurado_pct !== undefined ? nac.apurado_pct : 0;
      const bPct = nac.bolsonaro_pct || 0;
      const bVotos = nac.bolsonaro_votos || 0;
      const lPct = nac.lula_pct || 0;
      const lVotos = nac.lula_votos || 0;

      document.getElementById('art-pres-bolso-pct').textContent = bPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('art-pres-bolso-votos').textContent = bVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('art-pres-bolso-estados').textContent = `${{nac.estados_bolsonaro || 0}} UFs à frente`;

      document.getElementById('art-pres-lula-pct').textContent = lPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('art-pres-lula-votos').textContent = lVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('art-pres-lula-estados').textContent = `${{nac.estados_lula || 0}} UFs à frente`;

      const bBadge = document.getElementById('art-pres-bolso-badge');
      const lBadge = document.getElementById('art-pres-lula-badge');
      if (bVotos > lVotos) {{
        bBadge.textContent = 'LÍDER';
        lBadge.textContent = '2º Lugar';
      }} else if (lVotos > bVotos) {{
        lBadge.textContent = 'LÍDER';
        bBadge.textContent = '2º Lugar';
      }} else {{
        bBadge.textContent = apurado === 0 ? 'Aguardando' : '-';
        lBadge.textContent = apurado === 0 ? 'Aguardando' : '-';
      }}

      const diff = Math.abs(bPct - lPct);
      document.getElementById('art-pres-diff-pct').textContent = diff.toFixed(2).replace('.', ',') + '%';
      document.getElementById('art-pres-diff-votos').textContent = '+' + Math.abs(bVotos - lVotos).toLocaleString('pt-BR');
      document.getElementById('art-pres-valid-votos').textContent = `Válidos: ${{(nac.votos_validos || 0).toLocaleString('pt-BR')}}`;

      document.getElementById('art-pres-apurado-pct').textContent = apurado.toFixed(2).replace('.', ',') + '%';
      document.getElementById('art-pres-timestamp').textContent = `Boletim: ${{nac.timestamp || 'Hoje'}}`;

      renderPresMap();
    }}

    function renderPresMap() {{
      const paths = document.getElementById('art-pres-paths');
      const labels = document.getElementById('art-pres-labels');
      paths.innerHTML = '';
      labels.innerHTML = '';

      Object.values(DATA.estados).forEach(st => {{
        const td = st.hoje_2026 || {{}};
        const apurado = td.apurado_pct || 0;
        const bVotos = td.bolsonaro_votos || 0;
        const lVotos = td.lula_votos || 0;

        let color = '#475569';
        if (apurado > 0 || bVotos > 0 || lVotos > 0) {{
          if (bVotos > lVotos || td.vencedor === 'Bolsonaro') color = '#2563eb';
          else if (lVotos > bVotos || td.vencedor === 'Lula') color = '#dc2626';
        }}

        const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        p.setAttribute('d', st.svg_path);
        p.setAttribute('class', 'state-path');
        p.setAttribute('stroke', '#0f172a');
        p.setAttribute('fill', color);

        paths.appendChild(p);

        const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        txt.setAttribute('x', st.label_pos[0]);
        txt.setAttribute('y', st.label_pos[1]);
        txt.setAttribute('text-anchor', 'middle');
        txt.setAttribute('dominant-baseline', 'central');
        txt.setAttribute('fill', '#ffffff');
        txt.setAttribute('font-size', '10.5');
        txt.setAttribute('font-weight', '700');
        txt.setAttribute('class', 'pointer-events-none select-none');
        txt.textContent = st.uf;

        labels.appendChild(txt);
      }});
    }}

    function renderSenateBars() {{
      if (!DATA.senado_2026) return;
      const bar = document.getElementById('art-sen-bar');
      const grid = document.getElementById('art-sen-grid');
      bar.innerHTML = '';
      grid.innerHTML = '';

      const parties = DATA.senado_2026.partidos_eleitos_hoje || [];
      const total = DATA.senado_2026.total_eleitos_hoje || 54;

      parties.forEach(p => {{
        const pct = (p.cadeiras / total) * 100;
        const seg = document.createElement('div');
        seg.style.width = pct + '%';
        seg.style.backgroundColor = p.cor;
        seg.className = 'h-full';
        seg.title = `${{p.partido}}: ${{p.cadeiras}}`;
        bar.appendChild(seg);

        const card = document.createElement('div');
        card.className = 'bg-[var(--card)] border border-[var(--border)] rounded-lg p-1.5 text-center';
        card.innerHTML = `
          <div class="flex items-center justify-center gap-1 text-[11px] font-bold">
            <span class="w-2 h-2 rounded-full" style="background-color: ${{p.cor}}"></span>
            ${{p.partido}}
          </div>
          <div class="font-black text-sm">${{p.cadeiras}}</div>
        `;
        grid.appendChild(card);
      }});
    }}

    function renderSenateMap() {{
      if (!DATA.senado_2026) return;
      const paths = document.getElementById('art-sen-paths');
      const labels = document.getElementById('art-sen-labels');
      paths.innerHTML = '';
      labels.innerHTML = '';

      Object.values(DATA.estados).forEach(st => {{
        const sen = DATA.senado_2026.por_uf[st.uf];
        const p1 = sen ? sen.partido_1 : 'OUTROS';
        const color = PARTY_COLORS[p1] || '#64748b';

        const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        p.setAttribute('id', 'art-s-path-' + st.uf);
        p.setAttribute('d', st.svg_path);
        p.setAttribute('class', 'state-path');
        p.setAttribute('stroke', '#0f172a');
        p.setAttribute('fill', color);
        p.onclick = () => inspectSenateState(st.uf);

        paths.appendChild(p);

        const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        txt.setAttribute('x', st.label_pos[0]);
        txt.setAttribute('y', st.label_pos[1]);
        txt.setAttribute('text-anchor', 'middle');
        txt.setAttribute('dominant-baseline', 'central');
        txt.setAttribute('fill', '#ffffff');
        txt.setAttribute('font-size', '10.5');
        txt.setAttribute('font-weight', '700');
        txt.setAttribute('class', 'pointer-events-none select-none');
        txt.textContent = st.uf;

        labels.appendChild(txt);
      }});
    }}

    function inspectSenateState(uf) {{
      if (!DATA.senado_2026) return;
      const st = DATA.estados[uf];
      const sen = DATA.senado_2026.por_uf[uf];
      if (!st || !sen) return;

      document.querySelectorAll('#art-sen-paths .state-path').forEach(p => p.classList.remove('selected'));
      const p = document.getElementById('art-s-path-' + uf);
      if (p) p.classList.add('selected');

      document.getElementById('art-insp-uf').textContent = uf;
      document.getElementById('art-insp-nome').textContent = st.nome;

      const e1 = sen.eleitos[0];
      const e2 = sen.eleitos[1];

      document.getElementById('art-sen-card1').innerHTML = `
        <div class="flex justify-between items-center">
          <span class="font-bold text-[var(--foreground)]">1º ${{e1.nome}}</span>
          <span class="font-bold text-white px-1.5 py-0.2 rounded text-[10px]" style="background-color: ${{PARTY_COLORS[e1.partido] || '#3b82f6'}}">${{e1.partido}}</span>
        </div>
        <div class="flex justify-between text-[11px] text-[var(--muted-foreground)] font-mono">
          <span>${{e1.pct.toFixed(2).replace('.', ',')}}%</span>
          <span>${{e1.votos.toLocaleString('pt-BR')}} votos</span>
        </div>
      `;

      document.getElementById('art-sen-card2').innerHTML = `
        <div class="flex justify-between items-center">
          <span class="font-bold text-[var(--foreground)]">2º ${{e2.nome}}</span>
          <span class="font-bold text-white px-1.5 py-0.2 rounded text-[10px]" style="background-color: ${{PARTY_COLORS[e2.partido] || '#10b981'}}">${{e2.partido}}</span>
        </div>
        <div class="flex justify-between text-[11px] text-[var(--muted-foreground)] font-mono">
          <span>${{e2.pct.toFixed(2).replace('.', ',')}}%</span>
          <span>${{e2.votos.toLocaleString('pt-BR')}} votos</span>
        </div>
      `;

      const rem = sen.remanescente_2022 || {{}};
      document.getElementById('art-rem-nome').textContent = `${{rem.nome || 'Senador'}} (${{rem.partido || '-'}})`;
    }}

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
'''

    # Target path: current active conversation or env
    target_dir = os.environ.get('ANTIGRAVITY_ARTIFACT_DIR', r"C:\Users\crazy\.gemini\antigravity\brain\3a0cdd9b-fd70-41c2-bf1b-cd2819b4ff79")
    try:
        os.makedirs(target_dir, exist_ok=True)
        target_path = os.path.join(target_dir, 'mapa_eleicoes_brasil.html')
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(artifact_html)
        print('Chat artifact rebuilt successfully in active dir! Size:', len(artifact_html))
    except Exception as e:
        print('Could not write artifact to dir:', e)

    return artifact_html

if __name__ == '__main__':
    rebuild_artifact()
