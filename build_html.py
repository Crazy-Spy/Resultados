import json
import os

def rebuild_html(data=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if data is None:
        db_file = os.path.join(base_dir, 'election_data.json')
        with open(db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

    json_str = json.dumps(data, ensure_ascii=False)

    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Eleições 2026 — 2º Turno Presidencial (Ao Vivo do TSE) & Senado</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .font-mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    .state-path {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      stroke-width: 1.2;
    }}
    .state-path:hover {{
      filter: brightness(1.2) drop-shadow(0 4px 8px rgba(0,0,0,0.4));
      stroke: #ffffff;
      stroke-width: 2.2;
    }}
    .state-path.selected {{
      stroke: #facc15 !important;
      stroke-width: 3 !important;
      filter: drop-shadow(0 0 10px rgba(250, 204, 21, 0.6));
    }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-track {{
      background: rgba(30, 41, 59, 0.5);
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: rgba(100, 116, 139, 0.5);
      border-radius: 3px;
    }}
    .pulse-live {{
      animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.95); }}
    }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased selection:bg-rose-500 selection:text-white">

  <!-- TOP HEADER -->
  <header class="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
      
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-600 via-amber-500 to-blue-600 flex items-center justify-center shadow-lg font-black text-white text-lg">
          26
        </div>
        <div>
          <h1 class="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
            Eleições Gerais 2026 • 2º Turno
            <span class="flex items-center gap-1.5 text-xs px-2.5 py-0.5 rounded-full font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
              <span class="w-2 h-2 rounded-full bg-rose-500 pulse-live"></span>
              AO VIVO DO TSE
            </span>
          </h1>
          <p class="text-xs text-slate-400 flex items-center gap-2">
            <span>Tribunal Superior Eleitoral • Apuração Presidencial (25/10/2026)</span>
            <span class="text-slate-600">•</span>
            <span id="last-updated-text" class="text-emerald-400 font-mono text-[11px]">Carregando...</span>
          </p>
        </div>
      </div>

      <!-- MAIN CARGO SWITCHER (PRESIDENTE vs SENADO) -->
      <div class="flex items-center bg-slate-800/90 p-1 rounded-xl border border-slate-700/80 shadow-inner">
        <button id="nav-btn-presidente" onclick="setCargoMode('presidente')" class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 bg-rose-600 text-white shadow-md flex items-center gap-1.5">
          🗳️ Presidente (2º Turno Ao Vivo)
        </button>
        <button id="nav-btn-senado" onclick="setCargoMode('senado')" class="px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 text-slate-400 hover:text-white flex items-center gap-1.5">
          🏛️ Bancada do Senado (1º Turno)
        </button>
      </div>

      <!-- Actions & Auto-refresh -->
      <div class="flex items-center gap-3">
        <label class="hidden sm:flex items-center gap-1.5 text-xs text-slate-300 cursor-pointer select-none">
          <input type="checkbox" id="chk-auto-refresh" onchange="toggleAutoRefresh(this.checked)" class="rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-0">
          <span>Auto (60s)</span>
        </label>
        <button id="btn-refresh" onclick="atualizarDadosAoVivo()" class="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1.5 shadow-md shadow-emerald-950/40">
          <svg id="refresh-icon" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          <span id="refresh-label">Atualizar Agora</span>
        </button>
        <button onclick="downloadCSV()" class="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
          CSV
        </button>
      </div>

    </div>
  </header>

  <!-- ALERT BANNER (If file:// protocol detected) -->
  <div id="file-protocol-alert" class="hidden bg-amber-500/10 border-b border-amber-500/30 px-4 py-2 text-xs text-amber-300 text-center">
    ⚠️ <strong>Aviso:</strong> Você está visualizando diretamente o arquivo local (file://). Para atualizar automaticamente em 1 clique pelo navegador, inicie o servidor executando <code>python server.py</code> no terminal, ou atualize via terminal com <code>python atualizar_dados.py</code>.
  </div>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

    <!-- ======================================================== -->
    <!-- VIEW 1: ELEIÇÃO PRESIDENCIAL 2026 (2º TURNO AO VIVO) -->
    <!-- ======================================================== -->
    <div id="view-presidente" class="space-y-6">
      
      <!-- Live Progress Banner -->
      <div class="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-700/60 rounded-2xl p-4 shadow-lg flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-3 h-3 rounded-full bg-emerald-400 pulse-live"></div>
          <div>
            <div class="text-xs uppercase font-bold text-slate-300 tracking-wider flex items-center gap-2">
              <span id="pres-banner-title">Apuração Presidencial 2026 • 2º Turno</span>
              <span id="pres-banner-status-badge" class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full font-mono text-[11px] font-bold">
                AO VIVO
              </span>
            </div>
            <p class="text-xs text-slate-400" id="pres-banner-subtitle">
              Totalização oficial direta dos servidores do Tribunal Superior Eleitoral
            </p>
          </div>
        </div>

        <div class="flex-1 max-w-md w-full space-y-1">
          <div class="flex justify-between text-xs text-slate-300 font-mono">
            <span>Seções Totalizadas:</span>
            <span id="pres-banner-progress-text" class="font-bold text-emerald-400">0,00%</span>
          </div>
          <div class="w-full bg-slate-700/50 h-2.5 rounded-full overflow-hidden">
            <div id="pres-banner-progress-bar" class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: 0%"></div>
          </div>
        </div>
      </div>

      <!-- PLEITO / TURNO SELECTOR -->
      <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-2.5 rounded-2xl border border-slate-800">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs font-semibold text-slate-400 pl-1">Exibindo:</span>
          <div class="flex flex-wrap items-center gap-1.5">
            <button id="btn-turno-hoje" onclick="setPresTurno('hoje_2026')" class="px-3 py-1 rounded-xl text-xs font-bold transition-all bg-rose-600 text-white shadow-md flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-white pulse-live"></span>
              2º Turno (Hoje — 25/10/2026 Ao Vivo)
            </button>
            <button id="btn-turno-2026-1" onclick="setPresTurno('turno1_2026')" class="px-3 py-1 rounded-xl text-xs font-semibold transition-all text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700">
              1º Turno (04/10/2026)
            </button>
            <button id="btn-turno-2022-2" onclick="setPresTurno('turno2')" class="px-3 py-1 rounded-xl text-xs font-semibold transition-all text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700">
              2022 (2º Turno Histórico)
            </button>
            <button id="btn-turno-2022-1" onclick="setPresTurno('turno1')" class="px-3 py-1 rounded-xl text-xs font-semibold transition-all text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700">
              2022 (1º Turno Histórico)
            </button>
          </div>
        </div>
        <div class="text-[11px] text-slate-400 font-mono pr-2" id="pres-current-turno-desc">
          Disputa direta: Flávio Bolsonaro (PL) x Lula (PT)
        </div>
      </div>

      <!-- Presidential Scoreboard (4 Cards) -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- CARD 1: BOLSONARO -->
        <div class="bg-gradient-to-br from-blue-950/40 via-slate-900 to-slate-900 border border-blue-900/40 rounded-2xl p-4 shadow-lg">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-blue-500"></span>
              <span id="pres-bolso-title" class="font-bold text-white text-base">Bolsonaro (PL)</span>
            </div>
            <span id="pres-bolso-badge" class="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
              -
            </span>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="pres-bolso-pct" class="text-3xl font-black text-blue-400 tracking-tight">0,00%</span>
            <span class="text-xs text-slate-400 font-mono" id="pres-bolso-votos">0 votos</span>
          </div>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800 pt-2.5">
            <span>Estados à frente:</span>
            <span id="pres-bolso-estados" class="font-bold text-white bg-slate-800 px-2 py-0.5 rounded font-mono">0 UFs</span>
          </div>
        </div>

        <!-- CARD 2: LULA -->
        <div class="bg-gradient-to-br from-rose-950/40 via-slate-900 to-slate-900 border border-rose-900/40 rounded-2xl p-4 shadow-lg">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-full bg-rose-500"></span>
              <span id="pres-lula-title" class="font-bold text-white text-base">Lula (PT)</span>
            </div>
            <span id="pres-lula-badge" class="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
              -
            </span>
          </div>
          <div class="flex items-baseline gap-2">
            <span id="pres-lula-pct" class="text-3xl font-black text-rose-400 tracking-tight">0,00%</span>
            <span class="text-xs text-slate-400 font-mono" id="pres-lula-votos">0 votos</span>
          </div>
          <div class="mt-3 flex items-center justify-between text-xs text-slate-400 border-t border-slate-800 pt-2.5">
            <span>Estados à frente:</span>
            <span id="pres-lula-estados" class="font-bold text-white bg-slate-800 px-2 py-0.5 rounded font-mono">0 UFs</span>
          </div>
        </div>

        <!-- CARD 3: DIFERENÇA DIRETA -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col justify-between">
          <div>
            <div class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Diferença Nacional
            </div>
            <div class="flex items-baseline gap-2">
              <span id="pres-diff-pct" class="text-2xl font-black text-emerald-400">0,00%</span>
              <span id="pres-diff-votos" class="text-xs text-slate-400 font-mono">0 votos</span>
            </div>
          </div>
          <div class="space-y-1.5 mt-3">
            <div class="flex justify-between text-xs text-slate-400">
              <span>Votos Válidos:</span>
              <span id="pres-valid-votos" class="font-mono text-slate-200">0</span>
            </div>
            <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden flex">
              <div id="pres-bar-bolso" class="bg-blue-500 h-full transition-all duration-500" style="width: 50%"></div>
              <div id="pres-bar-lula" class="bg-rose-500 h-full transition-all duration-500" style="width: 50%"></div>
            </div>
          </div>
        </div>

        <!-- CARD 4: TOTALIZAÇÃO GERAL -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col justify-between text-xs">
          <div>
            <div class="font-semibold text-slate-300 uppercase tracking-wider text-[11px] mb-2 flex items-center justify-between">
              <span id="pres-card4-title">Totalização Geral</span>
              <span class="text-amber-400 font-mono text-[10px]" id="pres-card4-badge">TSE 2026</span>
            </div>
            <div id="pres-card4-content" class="space-y-1 text-slate-300 font-mono text-[11px]">
              <div class="flex justify-between">
                <span class="text-slate-400">Brancos:</span>
                <span id="pres-stat-brancos" class="text-slate-200">0 (0,00%)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Nulos:</span>
                <span id="pres-stat-nulos" class="text-slate-200">0 (0,00%)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Abstenção:</span>
                <span id="pres-stat-abstencao" class="text-amber-400">0,00%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Eleitorado:</span>
                <span id="pres-stat-eleitorado" class="text-slate-200">158.745.502</span>
              </div>
            </div>
          </div>
          <div class="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
            <span id="pres-status-msg">Somente 2 Candidatos</span>
            <span class="text-emerald-400 font-medium font-mono">Oficial TSE</span>
          </div>
        </div>

      </section>

      <!-- REGIONAL OVERVIEW SECTION -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
              🗺️ Apuração e Desempenho por Macrorregiões
              <span class="text-xs px-2.5 py-0.5 rounded-full font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">5 Regiões</span>
            </h3>
            <p class="text-xs text-slate-400">Progresso da apuração e divisão de votos nominais em cada macrorregião brasileira</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="filterPresRegion('ALL')" id="btn-reg-all" class="text-xs px-3.5 py-1.5 rounded-xl font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5">
              <span>Mostrar Todas</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3.5" id="pres-regions-grid"></div>
      </section>

      <!-- Presidential Map and Details -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div class="lg:col-span-8 bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl flex flex-col">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-800">
            <div class="flex flex-wrap items-center gap-4 text-xs">
              <div class="flex items-center gap-1.5">
                <div class="w-3.5 h-3.5 rounded bg-blue-600 border border-blue-400/50"></div>
                <span class="font-medium text-slate-300">Bolsonaro à frente</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-3.5 h-3.5 rounded bg-rose-600 border border-rose-400/50"></div>
                <span class="font-medium text-slate-300">Lula à frente</span>
              </div>
              <div class="flex items-center gap-1.5">
                <div class="w-3.5 h-3.5 rounded bg-slate-700 border border-slate-600"></div>
                <span class="font-medium text-slate-400">Aguardando apuração</span>
              </div>
            </div>

            <div class="flex items-center gap-2">
              <select id="pres-region-filter" onchange="filterPresRegion(this.value)" class="bg-slate-800 text-slate-200 text-xs rounded-xl px-3 py-1.5 border border-slate-700">
                <option value="ALL">Todas as Regiões</option>
                <option value="Norte">Norte</option>
                <option value="Nordeste">Nordeste</option>
                <option value="Centro-Oeste">Centro-Oeste</option>
                <option value="Sudeste">Sudeste</option>
                <option value="Sul">Sul</option>
              </select>
            </div>
          </div>

          <div class="relative flex-1 flex items-center justify-center p-2 min-h-[460px]">
            <svg id="pres-map-svg" viewBox="0 0 800 800" class="w-full h-full max-h-[640px] drop-shadow-2xl">
              <g id="pres-states-group"></g>
              <g id="pres-labels-group"></g>
            </svg>

            <div id="pres-tooltip" class="absolute pointer-events-none hidden bg-slate-900/95 backdrop-blur-md text-white border border-slate-700 p-3.5 rounded-2xl shadow-2xl z-50 text-xs w-64 transition-all duration-150">
              <div id="pres-tooltip-content"></div>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex justify-between">
            <span>Passe o mouse ou clique no estado para fixar detalhes</span>
            <span class="text-slate-500 font-mono">IBGE / TSE 2026</span>
          </div>
        </div>

        <div class="lg:col-span-4 space-y-4 flex flex-col">
          <div id="pres-state-card" class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <div class="flex items-center gap-2">
                    <span id="pres-detail-uf" class="text-2xl font-black text-white font-mono">BR</span>
                    <span id="pres-detail-badge" class="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                      Total Nacional
                    </span>
                  </div>
                  <h3 id="pres-detail-nome" class="text-sm font-semibold text-slate-300">Brasil (Total Nacional)</h3>
                  <span id="pres-detail-regiao" class="text-xs text-slate-400">Totalização apurada</span>
                </div>
                <button onclick="resetPresSelection()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700 transition">
                  Reset BR
                </button>
              </div>

              <div class="space-y-4 mb-4">
                <div class="space-y-1">
                  <div class="flex justify-between text-xs">
                    <span class="font-bold text-blue-400">Flávio Bolsonaro (PL)</span>
                    <span id="pres-detail-bolso-pct" class="font-bold font-mono text-sm">0,00%</span>
                  </div>
                  <div class="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
                    <div id="pres-detail-bar-bolso" class="bg-blue-500 h-full rounded-full transition-all duration-300" style="width: 50%"></div>
                  </div>
                  <span id="pres-detail-bolso-votos" class="text-[11px] text-slate-400 font-mono block">0 votos</span>
                </div>

                <div class="space-y-1">
                  <div class="flex justify-between text-xs">
                    <span class="font-bold text-rose-400">Lula (PT)</span>
                    <span id="pres-detail-lula-pct" class="font-bold font-mono text-sm">0,00%</span>
                  </div>
                  <div class="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
                    <div id="pres-detail-bar-lula" class="bg-rose-500 h-full rounded-full transition-all duration-300" style="width: 50%"></div>
                  </div>
                  <span id="pres-detail-lula-votos" class="text-[11px] text-slate-400 font-mono block">0 votos</span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2.5 text-xs mb-3">
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                  <span class="text-slate-400 block text-[11px]">Vantagem Líder:</span>
                  <span id="pres-detail-margem" class="font-bold text-emerald-400 font-mono text-sm">-</span>
                </div>
                <div class="bg-slate-800/60 p-2.5 rounded-xl border border-slate-800">
                  <span class="text-slate-400 block text-[11px]">Seções Apuradas:</span>
                  <span id="pres-detail-apurado" class="font-bold font-mono text-sm">0,00%</span>
                </div>
              </div>

              <div id="pres-detail-extra" class="bg-slate-800/30 p-2.5 rounded-xl border border-slate-800/60 text-[11px] space-y-1 text-slate-300 font-mono">
                <div class="flex justify-between">
                  <span class="text-slate-400">Votos Válidos:</span>
                  <span id="pres-detail-vv">-</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Brancos / Nulos:</span>
                  <span id="pres-detail-bn">-</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-400">Abstenção:</span>
                  <span id="pres-detail-abs">-</span>
                </div>
              </div>
            </div>

            <div class="mt-4 pt-3 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
              <span>TSE 2026 — 2º Turno</span>
              <span id="pres-detail-ibge" class="font-mono text-[11px]">BR</span>
            </div>
          </div>
        </div>

      </div>

      <!-- PRESIDENTIAL 27-STATES TABLE -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 class="text-base font-bold text-white tracking-tight">Quadro dos 27 Estados — Apuração Presidencial</h3>
            <p class="text-xs text-slate-400">Contagem de votos nominais, percentuais e liderança por Unidade Federativa</p>
          </div>
          <div class="flex items-center gap-3">
            <input type="text" id="pres-table-search" placeholder="Buscar estado ou UF..." oninput="renderPresTable(this.value)" class="bg-slate-800 text-slate-200 text-xs rounded-xl pl-3 pr-3 py-1.5 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-rose-500 w-56">
          </div>
        </div>

        <div class="overflow-x-auto custom-scrollbar">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                <th class="py-3 px-3">UF</th>
                <th class="py-3 px-3">Estado</th>
                <th class="py-3 px-3">Região</th>
                <th class="py-3 px-3">Apuração</th>
                <th class="py-3 px-3">Líder</th>
                <th class="py-3 px-3 text-blue-400">Bolsonaro (PL)</th>
                <th class="py-3 px-3 text-right text-blue-400">%</th>
                <th class="py-3 px-3 text-rose-400">Lula (PT)</th>
                <th class="py-3 px-3 text-right text-rose-400">%</th>
                <th class="py-3 px-3 text-right text-emerald-400">Vantagem</th>
                <th class="py-3 px-3 text-right">Abstenção</th>
              </tr>
            </thead>
            <tbody id="pres-table-body" class="divide-y divide-slate-800/60 font-mono"></tbody>
          </table>
        </div>
      </section>

    </div>

    <!-- ======================================================== -->
    <!-- VIEW 2: PANORAMA DO SENADO FEDERAL 2026 -->
    <!-- ======================================================== -->
    <div id="view-senado" class="hidden space-y-6">
      
      <!-- Top Senate Stats / Scoreboard -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div class="bg-gradient-to-br from-blue-950/40 via-slate-900 to-slate-900 border border-blue-900/40 rounded-2xl p-4 shadow-lg">
          <div class="text-xs uppercase font-bold text-slate-400 mb-1 flex items-center justify-between">
            <span>Vagas Renovadas</span>
            <span class="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-mono text-[10px]">2/3 do Senado</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-black text-white tracking-tight">54</span>
            <span class="text-xs text-slate-400">senadores eleitos (2 por UF)</span>
          </div>
          <p class="text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
            Cada um dos 26 estados + DF elegeu exatamente 2 senadores no 1º turno.
          </p>
        </div>

        <div class="bg-gradient-to-br from-blue-950/40 via-slate-900 to-slate-900 border border-blue-800/40 rounded-2xl p-4 shadow-lg">
          <div class="text-xs uppercase font-bold text-blue-400 mb-1 flex items-center justify-between">
            <span>Maior Partido Eleito</span>
            <span class="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-mono text-[10px]" id="sen-top1-pct">-</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-black text-blue-400 tracking-tight" id="sen-top1-cadeiras">-</span>
            <span class="text-xs text-slate-300 font-semibold" id="sen-top1-nome">senadores (PL)</span>
          </div>
          <p class="text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
            Partido Liberal conquistou a maior bancada eleita.
          </p>
        </div>

        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg">
          <div class="text-xs uppercase font-bold text-slate-400 mb-1 flex items-center justify-between">
            <span>2ª & 3ª Bancadas</span>
            <span class="text-[10px] text-slate-500 font-mono">Cadeiras</span>
          </div>
          <div class="flex items-center gap-4 mt-1">
            <div>
              <span class="text-2xl font-black text-amber-400" id="sen-top2-cadeiras">7</span>
              <span class="text-xs text-slate-300 ml-1">MDB</span>
            </div>
            <div class="w-px h-8 bg-slate-800"></div>
            <div>
              <span class="text-2xl font-black text-sky-400" id="sen-top3-cadeiras">7</span>
              <span class="text-xs text-slate-300 ml-1">PSD</span>
            </div>
          </div>
          <p class="text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
            Forças de centro e apoio no Congresso Nacional.
          </p>
        </div>

        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col justify-between">
          <div class="text-xs uppercase font-bold text-slate-400 mb-1 flex items-center justify-between">
            <span>Total da Casa</span>
            <span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono text-[10px]">Consolidado</span>
          </div>
          <div class="flex items-baseline gap-2">
            <span class="text-3xl font-black text-white tracking-tight">81</span>
            <span class="text-xs text-slate-400">senadores na composição 2027</span>
          </div>
          <p class="text-xs text-slate-400 mt-2 pt-2 border-t border-slate-800">
            54 eleitos hoje somam-se aos 27 eleitos em 2022.
          </p>
        </div>

      </section>

      <!-- SENATE PARTY COMPOSITION BARS -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl space-y-4">
        <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
              Distribuição das 54 Cadeiras Eleitas por Partido
            </h3>
            <p class="text-xs text-slate-400">Número de senadores eleitos no 1º turno (mandato 2027 a 2035)</p>
          </div>
          <div class="flex items-center gap-2 text-xs">
            <span class="text-slate-400">Total:</span>
            <span class="font-bold text-emerald-400 font-mono bg-slate-800 px-2 py-0.5 rounded">54 de 54 Senadores Totalizados</span>
          </div>
        </div>

        <div class="w-full bg-slate-800 h-6 rounded-xl overflow-hidden flex shadow-inner" id="senate-proportional-bar"></div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5 pt-2" id="senate-parties-grid"></div>
      </section>

      <!-- SENATE MAP & STATE DETAILS -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <div class="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl flex flex-col justify-between">
          <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <h4 class="text-sm font-bold text-white">Mapa das Eleições para o Senado</h4>
              <p class="text-xs text-slate-400">Colorido pelo partido do 1º senador mais votado na UF</p>
            </div>
            
            <select id="senate-region-filter" onchange="filterSenateRegion(this.value)" class="bg-slate-800 text-slate-200 text-xs rounded-xl px-3 py-1.5 border border-slate-700 focus:outline-none">
              <option value="ALL">Todas as Regiões</option>
              <option value="Norte">Norte</option>
              <option value="Nordeste">Nordeste</option>
              <option value="Centro-Oeste">Centro-Oeste</option>
              <option value="Sudeste">Sudeste</option>
              <option value="Sul">Sul</option>
            </select>
          </div>

          <div class="relative py-2 flex items-center justify-center min-h-[460px]">
            <svg id="senate-map-svg" viewBox="0 0 800 800" class="w-full h-full max-h-[560px] drop-shadow-2xl">
              <g id="senate-states-group"></g>
              <g id="senate-labels-group"></g>
            </svg>

            <div id="senate-tooltip" class="absolute pointer-events-none hidden bg-slate-900/95 backdrop-blur-md text-white border border-slate-700 p-3.5 rounded-2xl shadow-2xl z-50 text-xs w-72 transition-all duration-150">
              <div id="senate-tooltip-content"></div>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-800/80 text-xs text-slate-400 flex justify-between items-center">
            <span>Passe o mouse ou clique no estado para ver os 2 senadores eleitos</span>
            <span class="text-slate-500 font-mono">TSE 2026</span>
          </div>
        </div>

        <div class="lg:col-span-5 space-y-4 flex flex-col">
          <div id="senate-state-inspector" class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-xl flex-1 flex flex-col justify-between">
            <div>
              <div class="flex items-start justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <div class="flex items-center gap-2">
                    <span id="sen-insp-uf" class="text-2xl font-black text-white font-mono">SP</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                      2 Vagas Eleitas
                    </span>
                  </div>
                  <h3 id="sen-insp-nome" class="text-sm font-semibold text-slate-300">São Paulo</h3>
                  <span id="sen-insp-regiao" class="text-xs text-slate-400">Região Sudeste</span>
                </div>
                <span class="text-xs font-mono text-emerald-400 bg-slate-800 px-2 py-1 rounded">Consolidado</span>
              </div>

              <div class="space-y-3 mb-4">
                <div class="text-xs font-bold uppercase tracking-wider text-slate-400">Senadores Eleitos:</div>
                <div id="sen-card-1" class="bg-slate-800/70 border border-slate-700/80 rounded-2xl p-3.5 space-y-1.5"></div>
                <div id="sen-card-2" class="bg-slate-800/70 border border-slate-700/80 rounded-2xl p-3.5 space-y-1.5"></div>
              </div>

              <div class="bg-slate-800/40 border border-slate-800 rounded-2xl p-3 text-xs space-y-1 mb-3">
                <div class="text-[11px] text-slate-400 uppercase font-semibold flex items-center justify-between">
                  <span>3º Senador da UF (Mandato até 2030):</span>
                  <span class="text-slate-500 font-mono">Eleito em 2022</span>
                </div>
                <div class="flex justify-between items-center text-slate-200">
                  <span id="sen-remanescente-nome" class="font-bold text-sm">Marcos Pontes</span>
                  <span id="sen-remanescente-partido" class="font-mono font-bold text-blue-400 px-2 py-0.5 rounded bg-blue-500/10">PL</span>
                </div>
              </div>

              <div class="pt-3 border-t border-slate-800 text-xs">
                <div class="text-slate-400 font-semibold mb-1 text-[11px] uppercase">Demais Candidatos:</div>
                <div id="sen-demais-cands" class="space-y-1 text-slate-300 font-mono text-xs"></div>
              </div>
            </div>

            <div class="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex justify-between">
              <span>Fonte: TSE - Divulgação Oficial</span>
              <span id="sen-insp-footer-uf" class="font-mono">SP</span>
            </div>
          </div>
        </div>

      </div>

      <!-- FULL SENATE TABLE -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-xl">
        <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div>
            <h3 class="text-base font-bold text-white tracking-tight">Quadro Completo dos 54 Senadores Eleitos em 2026</h3>
            <p class="text-xs text-slate-400">Relação dos dois primeiros colocados em cada uma das 27 Unidades da Federação</p>
          </div>
          
          <div class="flex items-center gap-3">
            <input type="text" id="senate-table-search" placeholder="Buscar por estado, senador ou partido..." oninput="renderSenateTable(this.value)" class="bg-slate-800 text-slate-200 text-xs rounded-xl pl-3 pr-3 py-1.5 border border-slate-700 focus:outline-none focus:ring-1 focus:ring-blue-500 w-64">
          </div>
        </div>

        <div class="overflow-x-auto custom-scrollbar">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400 text-[11px] uppercase tracking-wider font-semibold">
                <th class="py-3 px-3">UF</th>
                <th class="py-3 px-3">Estado</th>
                <th class="py-3 px-3">Região</th>
                <th class="py-3 px-3 text-blue-400">1º Senador Eleito</th>
                <th class="py-3 px-3">Partido 1</th>
                <th class="py-3 px-3 text-right">Votos 1</th>
                <th class="py-3 px-3 text-right">% 1</th>
                <th class="py-3 px-3 text-emerald-400">2º Senador Eleito</th>
                <th class="py-3 px-3">Partido 2</th>
                <th class="py-3 px-3 text-right">Votos 2</th>
                <th class="py-3 px-3 text-right">% 2</th>
                <th class="py-3 px-3 text-slate-400">Senador 2022-2030</th>
              </tr>
            </thead>
            <tbody id="senate-table-body" class="divide-y divide-slate-800/60 font-mono"></tbody>
          </table>
        </div>
      </section>

    </div>

  </main>

  <script>
    let DATA = {json_str};
    let currentMode = 'presidente'; // Padrão: 2º Turno Presidencial Hoje
    let currentPresTurno = 'hoje_2026';
    let currentSenateRegion = 'ALL';
    let currentPresRegion = 'ALL';
    let selectedSenateUF = 'SP';
    let selectedPresUF = null;
    let autoRefreshTimer = null;

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
      if (window.location.protocol === 'file:') {{
        document.getElementById('file-protocol-alert').classList.remove('hidden');
      }}

      setCargoMode('presidente');
      renderPresView();
      renderSenateView();

      if (DATA.hoje_2026_nacional) {{
        document.getElementById('last-updated-text').textContent = 'Boletim TSE: ' + (DATA.hoje_2026_nacional.timestamp || '25/10/2026');
      }}

      // Se servido por HTTP/HTTPS (GitHub Pages ou servidor local), ativa auto-atualização por padrão
      if (window.location.protocol.startsWith('http')) {{
        const chk = document.getElementById('chk-auto-refresh');
        if (chk) chk.checked = true;
        toggleAutoRefresh(true);
        // Busca imediata ao vivo do TSE no primeiro carregamento
        setTimeout(atualizarDadosAoVivo, 500);
      }}
    }}

    function setCargoMode(mode) {{
      currentMode = mode;
      const bSen = document.getElementById('nav-btn-senado');
      const bPres = document.getElementById('nav-btn-presidente');
      const viewSen = document.getElementById('view-senado');
      const viewPres = document.getElementById('view-presidente');

      if (mode === 'presidente') {{
        bPres.className = 'px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 bg-rose-600 text-white shadow-md flex items-center gap-1.5';
        bSen.className = 'px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 text-slate-400 hover:text-white flex items-center gap-1.5';
        viewPres.classList.remove('hidden');
        viewSen.classList.add('hidden');
        renderPresView();
      }} else {{
        bSen.className = 'px-4 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 bg-blue-600 text-white shadow-md flex items-center gap-1.5';
        bPres.className = 'px-4 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 text-slate-400 hover:text-white flex items-center gap-1.5';
        viewSen.classList.remove('hidden');
        viewPres.classList.add('hidden');
        renderSenateView();
      }}
    }}

    function setPresTurno(tKey) {{
      currentPresTurno = tKey;
      ['btn-turno-hoje', 'btn-turno-2026-1', 'btn-turno-2022-2', 'btn-turno-2022-1'].forEach(id => {{
        const btn = document.getElementById(id);
        if (btn) {{
          btn.className = 'px-3 py-1 rounded-xl text-xs font-semibold transition-all text-slate-400 hover:text-white bg-slate-800 hover:bg-slate-700';
        }}
      }});

      let activeId = 'btn-turno-hoje';
      let desc = 'Totalização Oficial TSE • Somente 2 Candidatos';
      if (tKey === 'hoje_2026') {{
        activeId = 'btn-turno-hoje';
        desc = 'Disputa direta: Flávio Bolsonaro (PL) x Lula (PT)';
      }} else if (tKey === 'turno1_2026') {{
        activeId = 'btn-turno-2026-1';
        desc = '1º Turno (04/10/2026) — Bolsonaro, Lula, Cury, Caiado, Renan e outros';
      }} else if (tKey === 'turno2') {{
        activeId = 'btn-turno-2022-2';
        desc = 'Resultado Final do 2º Turno de 2022: Lula (50,90%) x Bolsonaro (49,10%)';
      }} else if (tKey === 'turno1') {{
        activeId = 'btn-turno-2022-1';
        desc = 'Resultado do 1º Turno de 2022: Lula (48,43%) x Bolsonaro (43,20%)';
      }}

      const aBtn = document.getElementById(activeId);
      if (aBtn) {{
        aBtn.className = 'px-3 py-1 rounded-xl text-xs font-bold transition-all bg-rose-600 text-white shadow-md flex items-center gap-1.5';
      }}
      document.getElementById('pres-current-turno-desc').textContent = desc;

      renderPresView();
    }}

    function getPresDataNac() {{
      if (currentPresTurno === 'hoje_2026') return DATA.hoje_2026_nacional || {{}};
      if (currentPresTurno === 'turno1_2026') return DATA.turno1_2026_nacional || {{}};
      if (currentPresTurno === 'turno2') return DATA.nacional_turno2 || {{}};
      if (currentPresTurno === 'turno1') return DATA.nacional_turno1 || {{}};
      return DATA.hoje_2026_nacional || {{}};
    }}

    function getPresDataUF(st) {{
      if (currentPresTurno === 'hoje_2026') return st.hoje_2026 || {{}};
      if (currentPresTurno === 'turno1_2026') return st.turno1_2026 || {{}};
      if (currentPresTurno === 'turno2') return st.turno2 || {{}};
      if (currentPresTurno === 'turno1') return st.turno1 || {{}};
      return st.hoje_2026 || {{}};
    }}

    // ==========================================
    // PRESIDENTIAL LOGIC (2º TURNO AO VIVO)
    // ==========================================
    function renderPresView() {{
      const nac = getPresDataNac();
      const apurado = nac.apurado_pct !== undefined ? nac.apurado_pct : 0;
      const isLive = currentPresTurno === 'hoje_2026';

      // Banner
      const statusBadge = document.getElementById('pres-banner-status-badge');
      const progressText = document.getElementById('pres-banner-progress-text');
      const progressBar = document.getElementById('pres-banner-progress-bar');
      const bannerSubtitle = document.getElementById('pres-banner-subtitle');

      progressText.textContent = apurado.toFixed(2).replace('.', ',') + '%';
      progressBar.style.width = apurado + '%';

      if (isLive) {{
        if (apurado === 0) {{
          statusBadge.textContent = 'AGUARDANDO URNAS';
          statusBadge.className = 'px-2 py-0.5 bg-amber-500/20 text-amber-400 rounded-full font-mono text-[11px] font-bold';
          bannerSubtitle.textContent = 'Urnas fecham às 17h00 • Acompanhe a totalização em tempo real conforme as urnas são transmitidas';
        }} else {{
          statusBadge.textContent = `${{apurado.toFixed(2).replace('.', ',')}}% APURADO`;
          statusBadge.className = 'px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full font-mono text-[11px] font-bold';
          bannerSubtitle.textContent = `Apuração em andamento • Boletim TSE: ${{nac.timestamp || 'Hoje'}}`;
        }}
      }} else {{
        statusBadge.textContent = 'CONSOLIDADO';
        statusBadge.className = 'px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full font-mono text-[11px] font-bold';
        bannerSubtitle.textContent = `Dados históricos oficiais da Justiça Eleitoral (${{currentPresTurno === 'turno1_2026' ? '04/10/2026' : 'Pleito 2022'}})`;
      }}

      // Bolsonaro Card
      const bPct = nac.bolsonaro_pct !== undefined ? nac.bolsonaro_pct : 0;
      const bVotos = nac.bolsonaro_votos !== undefined ? nac.bolsonaro_votos : 0;
      const bUFs = nac.estados_bolsonaro !== undefined ? nac.estados_bolsonaro : 0;
      document.getElementById('pres-bolso-pct').textContent = bPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-bolso-votos').textContent = bVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-bolso-estados').textContent = bUFs + ' UFs';

      // Lula Card
      const lPct = nac.lula_pct !== undefined ? nac.lula_pct : 0;
      const lVotos = nac.lula_votos !== undefined ? nac.lula_votos : 0;
      const lUFs = nac.estados_lula !== undefined ? nac.estados_lula : 0;
      document.getElementById('pres-lula-pct').textContent = lPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-lula-votos').textContent = lVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-lula-estados').textContent = lUFs + ' UFs';

      // Liderança Badges
      const bBadge = document.getElementById('pres-bolso-badge');
      const lBadge = document.getElementById('pres-lula-badge');
      if (bVotos > lVotos) {{
        bBadge.textContent = 'LÍDER';
        bBadge.className = 'text-xs font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30';
        lBadge.textContent = '2º Colocado';
        lBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
      }} else if (lVotos > bVotos) {{
        lBadge.textContent = 'LÍDER';
        lBadge.className = 'text-xs font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30';
        bBadge.textContent = '2º Colocado';
        bBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
      }} else {{
        bBadge.textContent = isLive && apurado === 0 ? 'Aguardando' : 'Empate';
        bBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
        lBadge.textContent = isLive && apurado === 0 ? 'Aguardando' : 'Empate';
        lBadge.className = 'text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
      }}

      // Card 3: Diferença
      const diffPct = Math.abs(bPct - lPct);
      const diffVotos = Math.abs(bVotos - lVotos);
      document.getElementById('pres-diff-pct').textContent = (diffPct > 0 ? '+' : '') + diffPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-diff-votos').textContent = (diffVotos > 0 ? '+' : '') + diffVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-valid-votos').textContent = (nac.votos_validos || 0).toLocaleString('pt-BR');
      
      const totalCandPct = (bPct + lPct) || 1;
      const bBar = (bPct / totalCandPct) * 100;
      const lBar = (lPct / totalCandPct) * 100;
      document.getElementById('pres-bar-bolso').style.width = (bPct === 0 && lPct === 0 ? 50 : bBar) + '%';
      document.getElementById('pres-bar-lula').style.width = (bPct === 0 && lPct === 0 ? 50 : lBar) + '%';

      // Card 4: Totalização do Pleito
      const vb = nac.brancos_votos !== undefined ? nac.brancos_votos : 0;
      const vn = nac.nulos_votos !== undefined ? nac.nulos_votos : 0;
      const absPct = nac.abstencao_pct !== undefined ? nac.abstencao_pct : 0;
      const totEleit = nac.eleitorado_total || 158745502;
      
      const vbPct = nac.brancos_pct !== undefined ? nac.brancos_pct.toFixed(2).replace('.', ',') + '%' : '';
      const vnPct = nac.nulos_pct !== undefined ? nac.nulos_pct.toFixed(2).replace('.', ',') + '%' : '';

// Totais atualizados via c4Content

      // Se 1º turno com outros candidatos, mostrar na caixinha
      const c4Content = document.getElementById('pres-card4-content');
      if (currentPresTurno === 'turno1_2026' && nac.outros_candidatos && nac.outros_candidatos.length > 0) {{
        document.getElementById('pres-card4-title').textContent = 'Terceiras Vias (1º T)';
        document.getElementById('pres-card4-badge').textContent = '04/10/2026';
        let h = '';
        nac.outros_candidatos.slice(0, 4).forEach(c => {{
          h += `<div class="flex justify-between"><span>${{c.nome.split(' ')[0]}} (${{c.partido}}):</span><span class="text-amber-400 font-bold">${{c.pct.toFixed(2).replace('.', ',')}}%</span></div>`;
        }});
        c4Content.innerHTML = h;
      }} else {{
        document.getElementById('pres-card4-title').textContent = 'Totalização Geral';
        document.getElementById('pres-card4-badge').textContent = isLive ? '2º Turno TSE' : 'Histórico';
        c4Content.innerHTML = `
          <div class="flex justify-between"><span class="text-slate-400">Brancos:</span><span class="text-slate-200">${{vb.toLocaleString('pt-BR')}} ${{vbPct ? '(' + vbPct + ')' : ''}}</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Nulos:</span><span class="text-slate-200">${{vn.toLocaleString('pt-BR')}} ${{vnPct ? '(' + vnPct + ')' : ''}}</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Abstenção:</span><span class="text-amber-400 font-bold">${{absPct.toFixed(2).replace('.', ',')}}%</span></div>
          <div class="flex justify-between"><span class="text-slate-400">Eleitorado:</span><span class="text-slate-200">${{totEleit.toLocaleString('pt-BR')}}</span></div>
        `;
      }}

      renderRegionCards();
      renderPresMap();
      resetPresSelection();
      renderPresTable('');
    }}

    function computeRegionStats() {{
      const regioesList = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
      const stats = {{}};
      regioesList.forEach(r => {{
        stats[r] = {{
          nome: r,
          ufs: [],
          secoes_total: 0,
          secoes_apuradas: 0,
          bolsonaro_votos: 0,
          lula_votos: 0,
          votos_validos: 0,
          brancos_votos: 0,
          nulos_votos: 0,
          abstencao: 0,
          eleitorado: 0,
          estados_bolsonaro: 0,
          estados_lula: 0
        }};
      }});

      Object.values(DATA.estados).forEach(st => {{
        const r = st.regiao;
        if (!stats[r]) return;
        const td = getPresDataUF(st);
        stats[r].ufs.push(st.uf);
        stats[r].secoes_total += (td.secoes_total || 0);
        stats[r].secoes_apuradas += (td.secoes_apuradas || 0);
        stats[r].bolsonaro_votos += (td.bolsonaro_votos || 0);
        stats[r].lula_votos += (td.lula_votos || 0);
        stats[r].votos_validos += (td.votos_validos || (td.bolsonaro_votos || 0) + (td.lula_votos || 0));
        stats[r].brancos_votos += (td.brancos_votos || 0);
        stats[r].nulos_votos += (td.nulos_votos || 0);
        stats[r].abstencao += (td.abstencao || 0);
        stats[r].eleitorado += (td.eleitorado || 0);

        const bV = td.bolsonaro_votos || 0;
        const lV = td.lula_votos || 0;
        if (bV > lV || td.vencedor === 'Bolsonaro') stats[r].estados_bolsonaro++;
        else if (lV > bV || td.vencedor === 'Lula') stats[r].estados_lula++;
      }});

      regioesList.forEach(r => {{
        const s = stats[r];
        s.apurado_pct = s.secoes_total > 0 ? (s.secoes_apuradas / s.secoes_total) * 100 : 0;
        const totCand = s.bolsonaro_votos + s.lula_votos;
        s.bolsonaro_pct = totCand > 0 ? (s.bolsonaro_votos / totCand) * 100 : 0;
        s.lula_pct = totCand > 0 ? (s.lula_votos / totCand) * 100 : 0;
        s.margem_pct = Math.abs(s.bolsonaro_pct - s.lula_pct);
        s.margem_votos = Math.abs(s.bolsonaro_votos - s.lula_votos);
        if (s.bolsonaro_votos > s.lula_votos) s.vencedor = 'Bolsonaro';
        else if (s.lula_votos > s.bolsonaro_votos) s.vencedor = 'Lula';
        else s.vencedor = s.apurado_pct === 0 ? 'Aguardando' : 'Empate';
      }});

      return stats;
    }}

    function renderRegionCards() {{
      const grid = document.getElementById('pres-regions-grid');
      if (!grid) return;
      grid.innerHTML = '';
      const stats = computeRegionStats();
      const regioesList = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];

      // Atualizar options do dropdown
      const sel = document.getElementById('pres-region-filter');
      if (sel) {{
        const nac = getPresDataNac();
        const nacApur = (nac.apurado_pct || 0).toFixed(1).replace('.', ',');
        sel.innerHTML = `<option value="ALL">Todas as Regiões (${{nacApur}}% apurado)</option>` +
          regioesList.map(r => {{
            const s = stats[r];
            const ap = s.apurado_pct.toFixed(1).replace('.', ',');
            const selAttr = currentPresRegion === r ? 'selected' : '';
            return `<option value="${{r}}" ${{selAttr}}>${{r}} (${{ap}}% apurado)</option>`;
          }}).join('');
      }}

      const btnAll = document.getElementById('btn-reg-all');
      if (btnAll) {{
        if (currentPresRegion === 'ALL') {{
          btnAll.className = 'text-xs px-3.5 py-1.5 rounded-xl font-bold bg-blue-600 text-white shadow transition flex items-center gap-1.5';
        }} else {{
          btnAll.className = 'text-xs px-3.5 py-1.5 rounded-xl font-bold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition flex items-center gap-1.5';
        }}
      }}

      regioesList.forEach(rName => {{
        const s = stats[rName];
        const isSelected = currentPresRegion === rName;
        const isBolso = s.vencedor === 'Bolsonaro';
        const isLula = s.vencedor === 'Lula';
        const apurText = s.apurado_pct.toFixed(2).replace('.', ',') + '%';

        let badgeLider = '<span class="text-[10px] text-slate-500 font-mono">Aguardando</span>';
        if (s.bolsonaro_votos > 0 || s.lula_votos > 0) {{
          if (isBolso) {{
            badgeLider = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400">Bolsonaro +${{s.margem_pct.toFixed(1).replace('.', ',')}}%</span>`;
          }} else if (isLula) {{
            badgeLider = `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400">Lula +${{s.margem_pct.toFixed(1).replace('.', ',')}}%</span>`;
          }}
        }}

        const card = document.createElement('div');
        card.className = `bg-slate-800/60 hover:bg-slate-800/95 border ${{isSelected ? 'border-amber-400 ring-2 ring-amber-400/30 bg-slate-800' : 'border-slate-700/60'}} rounded-2xl p-3.5 transition-all cursor-pointer flex flex-col justify-between space-y-3`;
        card.onclick = () => filterPresRegion(isSelected ? 'ALL' : rName);

        const totVotos = s.bolsonaro_votos + s.lula_votos;
        const barB = totVotos > 0 ? s.bolsonaro_pct : 50;
        const barL = totVotos > 0 ? s.lula_pct : 50;

        card.innerHTML = `
          <div>
            <div class="flex items-center justify-between gap-1 mb-2">
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-sm text-white">${{s.nome}}</span>
                <span class="text-[10px] text-slate-400 font-mono bg-slate-900/80 px-1.5 py-0.2 rounded border border-slate-700">${{s.ufs.length}} UFs</span>
              </div>
              ${{badgeLider}}
            </div>

            <!-- Apuração Progress -->
            <div class="space-y-1 mb-3 bg-slate-900/60 p-2 rounded-xl border border-slate-800">
              <div class="flex justify-between text-[11px] font-mono">
                <span class="text-slate-400">Apuração:</span>
                <span class="font-bold text-emerald-400">${{apurText}}</span>
              </div>
              <div class="w-full bg-slate-700/50 h-2 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full rounded-full transition-all duration-500" style="width: ${{s.apurado_pct}}%"></div>
              </div>
              <div class="text-[10px] text-slate-500 font-mono text-right">
                ${{s.secoes_apuradas.toLocaleString('pt-BR')}} de ${{s.secoes_total.toLocaleString('pt-BR')}} seções
              </div>
            </div>

            <!-- Placar Bolsonaro x Lula -->
            <div class="space-y-1.5 text-xs">
              <div class="flex justify-between items-center text-blue-300">
                <span class="font-bold">Bolsonaro:</span>
                <span class="font-mono font-bold">${{s.bolsonaro_pct.toFixed(2).replace('.', ',')}}% <span class="text-slate-400 font-normal text-[10px]">(${{s.bolsonaro_votos.toLocaleString('pt-BR')}})</span></span>
              </div>
              <div class="flex justify-between items-center text-rose-300">
                <span class="font-bold">Lula:</span>
                <span class="font-mono font-bold">${{s.lula_pct.toFixed(2).replace('.', ',')}}% <span class="text-slate-400 font-normal text-[10px]">(${{s.lula_votos.toLocaleString('pt-BR')}})</span></span>
              </div>

              <!-- Direct split bar -->
              <div class="w-full bg-slate-900 h-2 rounded-full overflow-hidden flex">
                <div class="bg-blue-500 h-full transition-all duration-300" style="width: ${{barB}}%"></div>
                <div class="bg-rose-500 h-full transition-all duration-300" style="width: ${{barL}}%"></div>
              </div>
            </div>
          </div>

          <div class="pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex items-center justify-between font-mono">
            <span>UFs: <strong class="text-blue-400">${{s.estados_bolsonaro}}</strong> x <strong class="text-rose-400">${{s.estados_lula}}</strong></span>
            <span class="${{isSelected ? 'text-amber-400 font-bold' : 'text-slate-500'}}">${{isSelected ? '✓ Filtrado' : 'Clique p/ filtrar'}}</span>
          </div>
        `;

        grid.appendChild(card);
      }});
    }}

    function renderPresMap() {{
      const stGroup = document.getElementById('pres-states-group');
      const lblGroup = document.getElementById('pres-labels-group');
      stGroup.innerHTML = '';
      lblGroup.innerHTML = '';

      Object.values(DATA.estados).forEach(st => {{
        const td = getPresDataUF(st);
        const apurado = td.apurado_pct !== undefined ? td.apurado_pct : 0;
        const bVotos = td.bolsonaro_votos || 0;
        const lVotos = td.lula_votos || 0;

        let color = '#334155'; // Slate-700 neutro para aguardando
        if (apurado > 0 || bVotos > 0 || lVotos > 0) {{
          if (td.vencedor === 'Bolsonaro' || bVotos > lVotos) {{
            color = '#2563eb';
          }} else if (td.vencedor === 'Lula' || lVotos > bVotos) {{
            color = '#dc2626';
          }}
        }}

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('id', 'pres-path-' + st.uf);
        path.setAttribute('d', st.svg_path);
        path.setAttribute('class', 'state-path');
        path.setAttribute('stroke', '#0f172a');
        path.setAttribute('fill', color);

        path.addEventListener('mouseenter', (e) => onPresHover(st, e));
        path.addEventListener('mousemove', (e) => updatePresTooltipPos(e));
        path.addEventListener('mouseleave', () => onPresLeave());
        path.addEventListener('click', () => inspectPresState(st.uf));

        stGroup.appendChild(path);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', st.label_pos[0]);
        text.setAttribute('y', st.label_pos[1]);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'central');
        text.setAttribute('fill', '#ffffff');
        text.setAttribute('font-size', '10.5');
        text.setAttribute('font-weight', '700');
        text.setAttribute('class', 'pointer-events-none select-none drop-shadow');
        text.textContent = st.uf;

        lblGroup.appendChild(text);
      }});
    }}

    function onPresHover(st, e) {{
      const td = getPresDataUF(st);
      const apurado = td.apurado_pct !== undefined ? td.apurado_pct : 0;
      const bVotos = td.bolsonaro_votos || 0;
      const lVotos = td.lula_votos || 0;
      const bPct = td.bolsonaro_pct || 0;
      const lPct = td.lula_pct || 0;

      const tt = document.getElementById('pres-tooltip');
      const content = document.getElementById('pres-tooltip-content');

      if (apurado === 0 && bVotos === 0 && lVotos === 0) {{
        content.innerHTML = `
          <div class="flex items-center justify-between pb-2 border-b border-slate-700/80 mb-2">
            <span class="font-bold text-sm text-white">${{st.nome}} (${{st.uf}})</span>
            <span class="text-[10px] uppercase font-mono text-amber-400">0,00% Apurado</span>
          </div>
          <div class="space-y-1 text-slate-300 text-xs">
            <p class="text-amber-300 font-semibold">⏳ Aguardando Apuração</p>
            <p class="text-[11px] text-slate-400">As seções estão sendo totalizadas pelo TSE.</p>
            <div class="pt-1.5 border-t border-slate-800 text-[11px] flex justify-between">
              <span>Eleitorado:</span>
              <span class="font-mono">${{(td.eleitorado || 0).toLocaleString('pt-BR')}}</span>
            </div>
          </div>
        `;
      }} else {{
        const isBolso = td.vencedor === 'Bolsonaro' || bVotos > lVotos;
        content.innerHTML = `
          <div class="flex items-center justify-between pb-2 border-b border-slate-700/80 mb-2">
            <span class="font-bold text-sm text-white">${{st.nome}} (${{st.uf}})</span>
            <span class="text-[10px] uppercase font-mono text-emerald-400">${{apurado.toFixed(2).replace('.', ',')}}% Apurado</span>
          </div>
          <div class="space-y-1.5">
            <div class="flex justify-between items-center text-blue-300">
              <span>Bolsonaro:</span>
              <span class="font-mono font-bold">${{bPct.toFixed(2).replace('.', ',')}}% (${{bVotos.toLocaleString('pt-BR')}})</span>
            </div>
            <div class="flex justify-between items-center text-rose-300">
              <span>Lula:</span>
              <span class="font-mono font-bold">${{lPct.toFixed(2).replace('.', ',')}}% (${{lVotos.toLocaleString('pt-BR')}})</span>
            </div>
            <div class="pt-1.5 border-t border-slate-800 flex justify-between text-slate-300 text-[11px]">
              <span>Líder: <strong class="${{isBolso ? 'text-blue-400' : 'text-rose-400'}}">${{td.vencedor || (isBolso ? 'Bolsonaro' : 'Lula')}}</strong></span>
              <span class="font-mono text-emerald-400">+${{(td.margem_pct || Math.abs(bPct - lPct)).toFixed(2).replace('.', ',')}}%</span>
            </div>
          </div>
        `;
      }}

      tt.classList.remove('hidden');
      updatePresTooltipPos(e);
    }}

    function updatePresTooltipPos(e) {{
      const tt = document.getElementById('pres-tooltip');
      const mapCont = document.getElementById('pres-map-svg').parentElement;
      const rect = mapCont.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      tt.style.left = `${{Math.min(Math.max(x - 128, 10), rect.width - 270)}}px`;
      tt.style.top = `${{Math.max(y - 145, 10)}}px`;
    }}

    function onPresLeave() {{
      document.getElementById('pres-tooltip').classList.add('hidden');
    }}

    function inspectPresState(uf) {{
      selectedPresUF = uf;
      const st = DATA.estados[uf];
      if (!st) return;
      const td = getPresDataUF(st);

      document.querySelectorAll('#pres-states-group .state-path').forEach(p => p.classList.remove('selected'));
      const p = document.getElementById('pres-path-' + uf);
      if (p) p.classList.add('selected');

      const apurado = td.apurado_pct !== undefined ? td.apurado_pct : 0;
      const bPct = td.bolsonaro_pct || 0;
      const bVotos = td.bolsonaro_votos || 0;
      const lPct = td.lula_pct || 0;
      const lVotos = td.lula_votos || 0;

      document.getElementById('pres-detail-uf').textContent = uf;
      document.getElementById('pres-detail-nome').textContent = st.nome;
      document.getElementById('pres-detail-regiao').textContent = `Região ${{st.regiao}} • IBGE: ${{st.codigo_ibge}}`;

      const badge = document.getElementById('pres-detail-badge');
      if (apurado === 0 && bVotos === 0 && lVotos === 0) {{
        badge.textContent = 'Aguardando início';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
      }} else if (bVotos > lVotos || td.vencedor === 'Bolsonaro') {{
        badge.textContent = 'Bolsonaro lidera';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30';
      }} else if (lVotos > bVotos || td.vencedor === 'Lula') {{
        badge.textContent = 'Lula lidera';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30';
      }} else {{
        badge.textContent = 'Empate';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30';
      }}

      document.getElementById('pres-detail-bolso-pct').textContent = bPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-bolso-votos').textContent = bVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-detail-bar-bolso').style.width = (bPct === 0 && lPct === 0 ? 50 : (bPct / (bPct + lPct || 1) * 100)) + '%';

      document.getElementById('pres-detail-lula-pct').textContent = lPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-lula-votos').textContent = lVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-detail-bar-lula').style.width = (bPct === 0 && lPct === 0 ? 50 : (lPct / (bPct + lPct || 1) * 100)) + '%';

      const margem = td.margem_pct !== undefined ? td.margem_pct : Math.abs(bPct - lPct);
      document.getElementById('pres-detail-margem').textContent = `+${{margem.toFixed(2).replace('.', ',')}}%`;
      document.getElementById('pres-detail-apurado').textContent = apurado.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-ibge').textContent = `IBGE: ${{st.codigo_ibge}}`;

      document.getElementById('pres-detail-vv').textContent = (td.votos_validos || (bVotos + lVotos)).toLocaleString('pt-BR');
      document.getElementById('pres-detail-bn').textContent = `${{(td.brancos_votos || 0).toLocaleString('pt-BR')}} / ${{(td.nulos_votos || 0).toLocaleString('pt-BR')}}`;
      document.getElementById('pres-detail-abs').textContent = `${{(td.abstencao_pct || 0).toFixed(2).replace('.', ',')}}% (${{(td.abstencao || 0).toLocaleString('pt-BR')}})`;
    }}

    function resetPresSelection() {{
      selectedPresUF = null;
      document.querySelectorAll('#pres-states-group .state-path').forEach(p => p.classList.remove('selected'));
      const nac = getPresDataNac();

      const apurado = nac.apurado_pct !== undefined ? nac.apurado_pct : 0;
      const bPct = nac.bolsonaro_pct || 0;
      const bVotos = nac.bolsonaro_votos || 0;
      const lPct = nac.lula_pct || 0;
      const lVotos = nac.lula_votos || 0;

      document.getElementById('pres-detail-uf').textContent = 'BR';
      document.getElementById('pres-detail-nome').textContent = 'Brasil (Total Nacional)';
      document.getElementById('pres-detail-regiao').textContent = 'Totalização Nacional Apurada';

      const badge = document.getElementById('pres-detail-badge');
      if (bVotos > lVotos) {{
        badge.textContent = 'Bolsonaro lidera';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30';
      }} else if (lVotos > bVotos) {{
        badge.textContent = 'Lula lidera';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30';
      }} else {{
        badge.textContent = apurado === 0 ? 'Aguardando início' : 'Empate';
        badge.className = 'text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700';
      }}

      document.getElementById('pres-detail-bolso-pct').textContent = bPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-bolso-votos').textContent = bVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-detail-bar-bolso').style.width = (bPct === 0 && lPct === 0 ? 50 : (bPct / (bPct + lPct || 1) * 100)) + '%';

      document.getElementById('pres-detail-lula-pct').textContent = lPct.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-lula-votos').textContent = lVotos.toLocaleString('pt-BR') + ' votos';
      document.getElementById('pres-detail-bar-lula').style.width = (bPct === 0 && lPct === 0 ? 50 : (lPct / (bPct + lPct || 1) * 100)) + '%';

      document.getElementById('pres-detail-margem').textContent = `+${{Math.abs(bPct - lPct).toFixed(2).replace('.', ',')}}%`;
      document.getElementById('pres-detail-apurado').textContent = apurado.toFixed(2).replace('.', ',') + '%';
      document.getElementById('pres-detail-ibge').textContent = 'BR';

      document.getElementById('pres-detail-vv').textContent = (nac.votos_validos || (bVotos + lVotos)).toLocaleString('pt-BR');
      document.getElementById('pres-detail-bn').textContent = `${{(nac.brancos_votos || 0).toLocaleString('pt-BR')}} / ${{(nac.nulos_votos || 0).toLocaleString('pt-BR')}}`;
      document.getElementById('pres-detail-abs').textContent = `${{(nac.abstencao_pct || 0).toFixed(2).replace('.', ',')}}% (${{(nac.abstencao_votos || 0).toLocaleString('pt-BR')}})`;
    }}

    function filterPresRegion(reg) {{
      currentPresRegion = reg;
      const sel = document.getElementById('pres-region-filter');
      if (sel) sel.value = reg;

      Object.values(DATA.estados).forEach(st => {{
        const p = document.getElementById('pres-path-' + st.uf);
        if (!p) return;
        const isDim = reg !== 'ALL' && st.regiao !== reg;
        p.setAttribute('opacity', isDim ? '0.2' : '1');
      }});

      renderRegionCards();
      const search = document.getElementById('pres-table-search');
      renderPresTable(search ? search.value : '');
    }}

    function renderPresTable(query) {{
      const tbody = document.getElementById('pres-table-body');
      if (!tbody) return;
      tbody.innerHTML = '';
      const q = (query || '').toLowerCase().trim();

      Object.values(DATA.estados).forEach(st => {{
        const td = getPresDataUF(st);
        if (currentPresRegion !== 'ALL' && st.regiao !== currentPresRegion) return;

        if (q) {{
          const full = (st.uf + ' ' + st.nome + ' ' + st.regiao).toLowerCase();
          if (!full.includes(q)) return;
        }}

        const apurado = td.apurado_pct !== undefined ? td.apurado_pct : 0;
        const bPct = td.bolsonaro_pct || 0;
        const bVotos = td.bolsonaro_votos || 0;
        const lPct = td.lula_pct || 0;
        const lVotos = td.lula_votos || 0;
        const isBolso = bVotos > lVotos || td.vencedor === 'Bolsonaro';
        const isLula = lVotos > bVotos || td.vencedor === 'Lula';
        
        let liderBadge = '<span class="text-slate-500">-</span>';
        if (bVotos > 0 || lVotos > 0) {{
          if (isBolso) {{
            liderBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-400">Bolsonaro</span>';
          }} else if (isLula) {{
            liderBadge = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400">Lula</span>';
          }}
        }}

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/50 transition cursor-pointer';
        tr.onclick = () => inspectPresState(st.uf);

        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-white">${{st.uf}}</td>
          <td class="py-2.5 px-3 font-sans text-slate-200 font-medium">${{st.nome}}</td>
          <td class="py-2.5 px-3 text-slate-400 font-sans">${{st.regiao}}</td>
          <td class="py-2.5 px-3 font-mono text-emerald-400">${{apurado.toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3">${{liderBadge}}</td>
          <td class="py-2.5 px-3 text-slate-300">${{bVotos.toLocaleString('pt-BR')}}</td>
          <td class="py-2.5 px-3 text-right text-blue-400 font-bold">${{bPct.toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3 text-slate-300">${{lVotos.toLocaleString('pt-BR')}}</td>
          <td class="py-2.5 px-3 text-right text-rose-400 font-bold">${{lPct.toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3 text-right text-emerald-400 font-bold">+${{Math.abs(bPct - lPct).toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3 text-right text-slate-400">${{(td.abstencao_pct || 0).toFixed(2).replace('.', ',')}}%</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // ==========================================
    // SENATE LOGIC
    // ==========================================
    function renderSenateView() {{
      if (!DATA.senado_2026) return;
      renderSenateBars();
      renderSenateMap();
      inspectSenateState(selectedSenateUF || 'SP');
      renderSenateTable('');
    }}

    function renderSenateBars() {{
      const barCont = document.getElementById('senate-proportional-bar');
      const gridCont = document.getElementById('senate-parties-grid');
      barCont.innerHTML = '';
      gridCont.innerHTML = '';

      const parties = DATA.senado_2026.partidos_eleitos_hoje || [];
      const total = DATA.senado_2026.total_eleitos_hoje || 54;

      if (parties.length > 0) {{
        document.getElementById('sen-top1-nome').textContent = `senadores (${{parties[0].partido}})`;
        document.getElementById('sen-top1-cadeiras').textContent = parties[0].cadeiras;
        document.getElementById('sen-top1-pct').textContent = ((parties[0].cadeiras / total) * 100).toFixed(1).replace('.', ',') + '%';
        if (parties.length > 1) document.getElementById('sen-top2-cadeiras').textContent = parties[1].cadeiras;
        if (parties.length > 2) document.getElementById('sen-top3-cadeiras').textContent = parties[2].cadeiras;
      }}

      parties.forEach(p => {{
        const widthPct = (p.cadeiras / total) * 100;
        const seg = document.createElement('div');
        seg.style.width = widthPct + '%';
        seg.style.backgroundColor = p.cor;
        seg.className = 'h-full transition-all duration-300 relative group cursor-pointer';
        seg.title = `${{p.partido}}: ${{p.cadeiras}} cadeiras (${{widthPct.toFixed(1)}}%)`;
        barCont.appendChild(seg);

        const card = document.createElement('div');
        card.className = 'bg-slate-800/60 border border-slate-700/60 rounded-xl p-2.5 text-center flex flex-col justify-between';
        card.innerHTML = `
          <div class="flex items-center justify-center gap-1.5 mb-1">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${{p.cor}}"></span>
            <span class="font-bold text-xs text-white">${{p.partido}}</span>
          </div>
          <div class="text-lg font-black text-white font-mono">${{p.cadeiras}}</div>
          <div class="text-[10px] text-slate-400 font-mono">${{widthPct.toFixed(1)}}%</div>
        `;
        gridCont.appendChild(card);
      }});
    }}

    function renderSenateMap() {{
      const stGroup = document.getElementById('senate-states-group');
      const lblGroup = document.getElementById('senate-labels-group');
      stGroup.innerHTML = '';
      lblGroup.innerHTML = '';

      Object.values(DATA.estados).forEach(st => {{
        const sen = DATA.senado_2026.por_uf[st.uf];
        const p1 = sen ? sen.partido_1 : 'OUTROS';
        const color = PARTY_COLORS[p1] || '#64748b';

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('id', 'sen-path-' + st.uf);
        path.setAttribute('d', st.svg_path);
        path.setAttribute('class', 'state-path');
        path.setAttribute('stroke', '#0f172a');
        path.setAttribute('fill', color);

        path.addEventListener('mouseenter', (e) => onSenateHover(st, e));
        path.addEventListener('mousemove', (e) => updateSenateTooltipPos(e));
        path.addEventListener('mouseleave', () => onSenateLeave());
        path.addEventListener('click', () => inspectSenateState(st.uf));

        stGroup.appendChild(path);

        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', st.label_pos[0]);
        text.setAttribute('y', st.label_pos[1]);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'central');
        text.setAttribute('fill', '#ffffff');
        text.setAttribute('font-size', '10.5');
        text.setAttribute('font-weight', '700');
        text.setAttribute('class', 'pointer-events-none select-none drop-shadow');
        text.textContent = st.uf;

        lblGroup.appendChild(text);
      }});
    }}

    function onSenateHover(st, e) {{
      const sen = DATA.senado_2026.por_uf[st.uf];
      if (!sen) return;
      const tt = document.getElementById('senate-tooltip');
      const content = document.getElementById('senate-tooltip-content');

      const e1 = sen.eleitos[0];
      const e2 = sen.eleitos[1];

      content.innerHTML = `
        <div class="flex items-center justify-between pb-2 border-b border-slate-700/80 mb-2">
          <span class="font-bold text-sm text-white">${{st.nome}} (${{st.uf}})</span>
          <span class="text-[10px] uppercase font-mono text-blue-400">2 Senadores Eleitos</span>
        </div>
        <div class="space-y-2">
          <div class="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-white">1º ${{e1.nome.split(' ')[0]}}</span>
              <span class="font-mono font-bold text-blue-400 px-1.5 py-0.2 rounded bg-blue-500/10">${{e1.partido}}</span>
            </div>
            <div class="text-[11px] text-slate-400 font-mono mt-0.5">${{e1.pct.toFixed(2).replace('.', ',')}}% (${{e1.votos.toLocaleString('pt-BR')}} votos)</div>
          </div>
          <div class="bg-slate-800/80 p-2 rounded-lg border border-slate-700">
            <div class="flex justify-between items-center text-xs">
              <span class="font-bold text-white">2º ${{e2.nome.split(' ')[0]}}</span>
              <span class="font-mono font-bold text-emerald-400 px-1.5 py-0.2 rounded bg-emerald-500/10">${{e2.partido}}</span>
            </div>
            <div class="text-[11px] text-slate-400 font-mono mt-0.5">${{e2.pct.toFixed(2).replace('.', ',')}}% (${{e2.votos.toLocaleString('pt-BR')}} votos)</div>
          </div>
        </div>
      `;

      tt.classList.remove('hidden');
      updateSenateTooltipPos(e);
    }}

    function updateSenateTooltipPos(e) {{
      const tt = document.getElementById('senate-tooltip');
      const mapCont = document.getElementById('senate-map-svg').parentElement;
      const rect = mapCont.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      tt.style.left = `${{Math.min(Math.max(x - 140, 10), rect.width - 300)}}px`;
      tt.style.top = `${{Math.max(y - 180, 10)}}px`;
    }}

    function onSenateLeave() {{
      document.getElementById('senate-tooltip').classList.add('hidden');
    }}

    function inspectSenateState(uf) {{
      selectedSenateUF = uf;
      const st = DATA.estados[uf];
      const sen = DATA.senado_2026.por_uf[uf];
      if (!st || !sen) return;

      document.querySelectorAll('#senate-states-group .state-path').forEach(p => p.classList.remove('selected'));
      const p = document.getElementById('sen-path-' + uf);
      if (p) p.classList.add('selected');

      document.getElementById('sen-insp-uf').textContent = uf;
      document.getElementById('sen-insp-nome').textContent = st.nome;
      document.getElementById('sen-insp-regiao').textContent = `Região ${{st.regiao}} • IBGE: ${{st.codigo_ibge}}`;
      document.getElementById('sen-insp-footer-uf').textContent = uf;

      const e1 = sen.eleitos[0];
      const e2 = sen.eleitos[1];

      document.getElementById('sen-card-1').innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-white flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${{PARTY_COLORS[e1.partido] || '#3b82f6'}}"></span>
            1º Eleito: ${{e1.nome}}
          </span>
          <span class="font-mono text-xs font-black text-white px-2 py-0.5 rounded" style="background-color: ${{PARTY_COLORS[e1.partido] || '#3b82f6'}}">${{e1.partido}}</span>
        </div>
        <div class="flex justify-between items-center text-xs font-mono text-slate-300 pt-1">
          <span>${{e1.pct.toFixed(2).replace('.', ',')}}% dos votos válidos</span>
          <span class="text-slate-400 font-semibold">${{e1.votos.toLocaleString('pt-BR')}} votos</span>
        </div>
      `;

      document.getElementById('sen-card-2').innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-white flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${{PARTY_COLORS[e2.partido] || '#10b981'}}"></span>
            2º Eleito: ${{e2.nome}}
          </span>
          <span class="font-mono text-xs font-black text-white px-2 py-0.5 rounded" style="background-color: ${{PARTY_COLORS[e2.partido] || '#10b981'}}">${{e2.partido}}</span>
        </div>
        <div class="flex justify-between items-center text-xs font-mono text-slate-300 pt-1">
          <span>${{e2.pct.toFixed(2).replace('.', ',')}}% dos votos válidos</span>
          <span class="text-slate-400 font-semibold">${{e2.votos.toLocaleString('pt-BR')}} votos</span>
        </div>
      `;

      const rem = sen.remanescente_2022 || {{}};
      document.getElementById('sen-remanescente-nome').textContent = rem.nome || 'Senador em exercício';
      document.getElementById('sen-remanescente-partido').textContent = rem.partido || '-';

      const demaisCont = document.getElementById('sen-demais-cands');
      demaisCont.innerHTML = '';
      if (sen.demais_candidatos) {{
        sen.demais_candidatos.slice(0, 3).forEach((c, idx) => {{
          demaisCont.innerHTML += `
            <div class="flex justify-between items-center py-0.5">
              <span>${{idx + 3}}º ${{c.nome}} (${{c.partido}}):</span>
              <span class="text-slate-400 font-mono">${{c.pct.toFixed(2).replace('.', ',')}}% (${{c.votos.toLocaleString('pt-BR')}})</span>
            </div>
          `;
        }});
      }}
    }}

    function filterSenateRegion(reg) {{
      currentSenateRegion = reg;
      Object.values(DATA.estados).forEach(st => {{
        const p = document.getElementById('sen-path-' + st.uf);
        if (!p) return;
        const isDim = reg !== 'ALL' && st.regiao !== reg;
        p.setAttribute('opacity', isDim ? '0.25' : '1');
      }});
    }}

    function renderSenateTable(query) {{
      const tbody = document.getElementById('senate-table-body');
      tbody.innerHTML = '';
      const q = (query || '').toLowerCase().trim();

      Object.values(DATA.estados).forEach(st => {{
        const sen = DATA.senado_2026.por_uf[st.uf];
        if (!sen) return;
        const e1 = sen.eleitos[0];
        const e2 = sen.eleitos[1];
        const rem = sen.remanescente_2022 || {{}};

        if (q) {{
          const full = (st.uf + ' ' + st.nome + ' ' + e1.nome + ' ' + e1.partido + ' ' + e2.nome + ' ' + e2.partido).toLowerCase();
          if (!full.includes(q)) return;
        }}

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/50 transition cursor-pointer';
        tr.onclick = () => inspectSenateState(st.uf);

        tr.innerHTML = `
          <td class="py-2.5 px-3 font-bold text-white">${{st.uf}}</td>
          <td class="py-2.5 px-3 font-sans text-slate-200 font-medium">${{st.nome}}</td>
          <td class="py-2.5 px-3 text-slate-400 font-sans">${{st.regiao}}</td>
          <td class="py-2.5 px-3 font-bold text-slate-100">${{e1.nome}}</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold" style="background-color: ${{PARTY_COLORS[e1.partido] || '#3b82f6'}}22; color: ${{PARTY_COLORS[e1.partido] || '#3b82f6'}}">${{e1.partido}}</span></td>
          <td class="py-2.5 px-3 text-right text-slate-300">${{e1.votos.toLocaleString('pt-BR')}}</td>
          <td class="py-2.5 px-3 text-right text-blue-400 font-bold">${{e1.pct.toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3 font-bold text-slate-100">${{e2.nome}}</td>
          <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold" style="background-color: ${{PARTY_COLORS[e2.partido] || '#10b981'}}22; color: ${{PARTY_COLORS[e2.partido] || '#10b981'}}">${{e2.partido}}</span></td>
          <td class="py-2.5 px-3 text-right text-slate-300">${{e2.votos.toLocaleString('pt-BR')}}</td>
          <td class="py-2.5 px-3 text-right text-emerald-400 font-bold">${{e2.pct.toFixed(2).replace('.', ',')}}%</td>
          <td class="py-2.5 px-3 text-slate-400 font-sans">${{rem.nome || '-'}} (${{rem.partido || '-'}})</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // ==========================================
    // REFRESH & LIVE UPDATES (DIRETO DO TSE NO NAVEGADOR & GITHUB PAGES)
    // ==========================================
    function parseNum(val, def = 0) {{
      if (val === undefined || val === null) return def;
      const s = String(val).split('.').join('').replace(',', '.').trim();
      const n = parseInt(s, 10);
      return isNaN(n) ? def : n;
    }}

    function parseFloatBR(val, def = 0.0) {{
      if (val === undefined || val === null) return def;
      const s = String(val).split('.').join('').replace(',', '.').trim();
      const f = parseFloat(s);
      return isNaN(f) ? def : f;
    }}

    // Coleta diretamente da API oficial do TSE pelo navegador (com suporte total a CORS em GitHub Pages)
    async function coletarTSEClientSide() {{
      const ts = Date.now();
      const ufs = ['ac', 'al', 'am', 'ap', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mg', 'ms', 'mt', 'pa', 'pb', 'pe', 'pi', 'pr', 'rj', 'rn', 'ro', 'rr', 'rs', 'sc', 'se', 'sp', 'to'];
      const baseTse = 'https://resultados.tse.jus.br/oficial/ele2026/6258/dados';

      // 1. Totalização Nacional (BR)
      const rBr = await fetch(`${{baseTse}}/br/br-c0001-e006258-u.json?_t=${{ts}}`, {{ cache: 'no-store' }});
      if (!rBr.ok) throw new Error('Falha ao consultar TSE BR: ' + rBr.status);
      const brJson = await rBr.json();

      const secoesBr = brJson.s || {{}};
      const apuradoPctBr = parseFloatBR(secoesBr.pst, 0);
      const cargBr = (brJson.carg && brJson.carg[0]) || {{}};

      let bolsoBr = {{ votos: 0, pct: 0, nome: 'FLAVIO NANTES BOLSONARO' }};
      let lulaBr = {{ votos: 0, pct: 0, nome: 'LUIZ INÁCIO LULA DA SILVA' }};

      (cargBr.agr || []).forEach(a => {{
        (a.par || []).forEach(p => {{
          (p.cand || []).forEach(c => {{
            const num = c.n;
            const item = {{
              numero: num,
              nome: c.nm,
              partido: p.sg,
              votos: parseNum(c.vap),
              pct: parseFloatBR(c.pvap)
            }};
            if (num === '22') bolsoBr = item;
            if (num === '13') lulaBr = item;
          }});
        }});
      }});

      const vInfo = brJson.v || {{}};
      const eInfo = brJson.e || {{}};

      let vencedorNac = 'Aguardando';
      if (bolsoBr.votos > lulaBr.votos) vencedorNac = 'Bolsonaro';
      else if (lulaBr.votos > bolsoBr.votos) vencedorNac = 'Lula';
      else vencedorNac = apuradoPctBr === 0 ? 'Aguardando' : 'Empate';

      const nacHoje = {{
        timestamp: `${{brJson.dg || ''}} ${{brJson.hg || ''}}`.trim(),
        turno: 2,
        pleito_data: '25/10/2026',
        descricao: '2º Turno Presidencial (25/10/2026)',
        apurado_pct: apuradoPctBr,
        secoes_total: parseNum(secoesBr.ts),
        secoes_apuradas: parseNum(secoesBr.st),
        lula_votos: lulaBr.votos,
        lula_pct: lulaBr.pct,
        lula_nome: lulaBr.nome,
        bolsonaro_votos: bolsoBr.votos,
        bolsonaro_pct: bolsoBr.pct,
        bolsonaro_nome: bolsoBr.nome,
        outros_candidatos: [],
        votos_validos: parseNum(vInfo.vv),
        brancos_votos: parseNum(vInfo.vb),
        brancos_pct: parseFloatBR(vInfo.pvb),
        nulos_votos: parseNum(vInfo.tvn),
        nulos_pct: parseFloatBR(vInfo.ptvn),
        abstencao_votos: parseNum(eInfo.a),
        abstencao_pct: parseFloatBR(eInfo.pa),
        eleitorado_total: parseNum(eInfo.te),
        vencedor: vencedorNac,
        estados_lula: 0,
        estados_bolsonaro: 0
      }};

      // 2. Consulta concorrente dos 27 estados
      const ufReqs = ufs.map(async u => {{
        try {{
          const r = await fetch(`${{baseTse}}/${{u}}/${{u}}-c0001-e006258-u.json?_t=${{ts}}`, {{ cache: 'no-store' }});
          if (!r.ok) return null;
          const j = await r.json();
          return {{ uf: u.toUpperCase(), json: j }};
        }} catch (e) {{
          return null;
        }}
      }});

      const ufResults = await Promise.all(ufReqs);

      ufResults.forEach(res => {{
        if (!res || !res.json) return;
        const uf = res.uf;
        const uJson = res.json;
        const cargUf = (uJson.carg && uJson.carg[0]) || {{}};

        let bUf = {{ votos: 0, pct: 0, nome: 'FLAVIO NANTES BOLSONARO' }};
        let lUf = {{ votos: 0, pct: 0, nome: 'LUIZ INÁCIO LULA DA SILVA' }};

        (cargUf.agr || []).forEach(a => {{
          (a.par || []).forEach(p => {{
            (p.cand || []).forEach(c => {{
              const num = c.n;
              const item = {{
                nome: c.nm,
                partido: p.sg,
                votos: parseNum(c.vap),
                pct: parseFloatBR(c.pvap)
              }};
              if (num === '22') bUf = item;
              if (num === '13') lUf = item;
            }});
          }});
        }});

        const vUf = uJson.v || {{}};
        const eUf = uJson.e || {{}};
        const sUf = uJson.s || {{}};
        const apurUf = parseFloatBR(sUf.pst);

        let vencedorUf = 'Aguardando';
        if (bUf.votos > lUf.votos) {{
          vencedorUf = 'Bolsonaro';
          nacHoje.estados_bolsonaro++;
        }} else if (lUf.votos > bUf.votos) {{
          vencedorUf = 'Lula';
          nacHoje.estados_lula++;
        }}

        const margemPct = Math.round(Math.abs(lUf.pct - bUf.pct) * 100) / 100;
        const margemVotos = Math.abs(lUf.votos - bUf.votos);

        if (DATA.estados && DATA.estados[uf]) {{
          DATA.estados[uf].hoje_2026 = {{
            timestamp: `${{uJson.dg || ''}} ${{uJson.hg || ''}}`.trim(),
            secoes_total: parseNum(sUf.ts),
            secoes_apuradas: parseNum(sUf.st),
            apurado_pct: apurUf,
            eleitorado: parseNum(eUf.te),
            abstencao: parseNum(eUf.a),
            abstencao_pct: parseFloatBR(eUf.pa),
            lula_votos: lUf.votos,
            lula_pct: lUf.pct,
            lula_nome: lUf.nome,
            bolsonaro_votos: bUf.votos,
            bolsonaro_pct: bUf.pct,
            bolsonaro_nome: bUf.nome,
            vencedor: vencedorUf,
            margem_pct: margemPct,
            margem_votos: margemVotos,
            brancos_votos: parseNum(vUf.vb),
            brancos_pct: parseFloatBR(vUf.pvb),
            nulos_votos: parseNum(vUf.tvn),
            nulos_pct: parseFloatBR(vUf.ptvn),
            votos_validos: parseNum(vUf.vv),
            outros: []
          }};
        }}
      }});

      DATA.hoje_2026_nacional = nacHoje;
      return DATA;
    }}

    async function atualizarDadosAoVivo() {{
      const btn = document.getElementById('btn-refresh');
      const label = document.getElementById('refresh-label');
      const icon = document.getElementById('refresh-icon');
      label.textContent = 'Buscando TSE...';
      icon.classList.add('animate-spin');

      try {{
        // 1. Tentar coletar direto da API oficial do TSE no navegador (suporta GitHub Pages via CORS!)
        try {{
          await coletarTSEClientSide();
          document.getElementById('last-updated-text').textContent = 'Boletim TSE: ' + (DATA.hoje_2026_nacional.timestamp || 'Hoje');
          renderPresView();
          label.textContent = 'Atualizado!';
          return;
        }} catch (errDirect) {{
          console.warn('Consulta direta ao TSE falhou ou bloqueada no protocolo file://, tentando fallback local...', errDirect);
        }}

        // 2. Se falhar (ex: file:// sem permissão de rede), tenta servidor local Python
        const resp = await fetch('/api/atualizar?_t=' + Date.now(), {{ cache: 'no-store' }});
        if (resp.ok) {{
          DATA = await resp.json();
          document.getElementById('last-updated-text').textContent = 'Boletim TSE: ' + (DATA.hoje_2026_nacional.timestamp || 'Hoje');
          renderPresView();
          label.textContent = 'Atualizado!';
        }} else {{
          // 3. Fallback para arquivo JSON estático se disponível
          const rJson = await fetch('election_data.json?_t=' + Date.now(), {{ cache: 'no-store' }});
          if (rJson.ok) {{
            DATA = await rJson.json();
            document.getElementById('last-updated-text').textContent = 'Boletim TSE: ' + (DATA.hoje_2026_nacional.timestamp || 'Hoje');
            renderPresView();
            label.textContent = 'Atualizado!';
          }}
        }}
      }} catch (e) {{
        console.warn('Erro ao atualizar dados:', e);
      }} finally {{
        setTimeout(() => {{
          label.textContent = 'Atualizar Agora';
          icon.classList.remove('animate-spin');
        }}, 1500);
      }}
    }}

    function toggleAutoRefresh(enable) {{
      if (autoRefreshTimer) {{
        clearInterval(autoRefreshTimer);
        autoRefreshTimer = null;
      }}
      if (enable) {{
        autoRefreshTimer = setInterval(atualizarDadosAoVivo, 60000);
      }}
    }}

    function downloadCSV() {{
      const lines = [];
      if (currentMode === 'presidente') {{
        lines.push('UF;Estado;Regiao;Apurado_Pct;Lider;Bolsonaro_Votos;Bolsonaro_Pct;Lula_Votos;Lula_Pct;Margem_Pct;Abstencao_Pct');
        Object.values(DATA.estados).forEach(st => {{
          const td = getPresDataUF(st);
          lines.push([
            st.uf,
            st.nome,
            st.regiao,
            td.apurado_pct || 0,
            td.vencedor || '-',
            td.bolsonaro_votos || 0,
            td.bolsonaro_pct || 0,
            td.lula_votos || 0,
            td.lula_pct || 0,
            td.margem_pct || 0,
            td.abstencao_pct || 0
          ].join(';'));
        }});
      }} else {{
        lines.push('UF;Estado;Regiao;Senador_1_Nome;Senador_1_Partido;Senador_1_Votos;Senador_2_Nome;Senador_2_Partido;Senador_2_Votos');
        Object.values(DATA.estados).forEach(st => {{
          const sen = (DATA.senado_2026 && DATA.senado_2026.por_uf) ? DATA.senado_2026.por_uf[st.uf] : null;
          if (sen) {{
            const e1 = sen.eleitos[0];
            const e2 = sen.eleitos[1];
            lines.push([
              st.uf,
              st.nome,
              st.regiao,
              e1.nome,
              e1.partido,
              e1.votos,
              e2.nome,
              e2.partido,
              e2.votos
            ].join(';'));
          }}
        }});
      }}
      const csv = lines.join(String.fromCharCode(10));
      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'tse_eleicoes_2026_' + currentMode + '.csv';
      a.click();
      URL.revokeObjectURL(url);
    }}

    window.addEventListener('DOMContentLoaded', init);
  </script>
</body>
</html>
'''

    out_file = os.path.join(base_dir, 'index.html')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print('index.html rebuilt successfully! Size:', len(html_content))
    return html_content

if __name__ == '__main__':
    rebuild_html()
