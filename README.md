# Mapa Eleitoral do Brasil — 2º Turno Presidencial ao Vivo (Dados Oficiais TSE)

Aplicação interativa para visualização geográfica e estatística da apuração presidencial em tempo real direta dos servidores do **Tribunal Superior Eleitoral (TSE)**. Focada no **2º Turno da Eleição Presidencial de Hoje (25/10/2026)** entre os dois candidatos, com alternância para o **1º Turno (04/10/2026)**, **Bancada do Senado 2026** e histórico de **2022**.

---

## 🔴 Como Funciona com o 2º Turno de Hoje (25/10/2026)

O TSE disponibiliza os arquivos unificados de totalização em tempo real da Eleição Ordinária Federal de 2º Turno (Código `6258`).
A disputa é direta e exclusiva entre dois candidatos:
- **Flávio Bolsonaro** (PL — nº 22)
- **Luiz Inácio Lula da Silva** (PT — nº 13)

### 1. Atualização com 1 Clique (Interface Web)
Se o servidor estiver em execução (`python server.py`), basta clicar no botão **"🔄 Atualizar Agora"** no topo da página (ou deixar ativada a opção **Auto 60s**). A aplicação consulta o TSE em segundo plano e renova o mapa, a contagem de votos e o placar instantaneamente.

### 2. Atualização via Linha de Comando
Execute a qualquer momento no terminal:
```bash
python atualizar_dados.py
```
O script fará o download simultâneo e seguro das 27 Unidades da Federação + total Brasil (código `6258`), consolidará os votos nominais, percentuais, abstenções e seções apuradas, atualizando `election_data.json` e reconstruindo `index.html`.

---

## 🚀 Como Iniciar a Aplicação

### Opção 1: Servidor Local Interativo (Recomendado)
Execute no terminal:
```bash
python server.py
```
- Inicia o servidor HTTP local na porta `8000`.
- Abre automaticamente o navegador em `http://localhost:8000/index.html`.
- Sincronização em segundo plano automática a cada 60 segundos.
- Habilita a rota `/api/atualizar` para buscar novos boletins de urna do TSE sob demanda.

### Opção 2: Abertura Direta
Dê duplo clique no arquivo [`index.html`](index.html) para abrir em qualquer navegador.

---

## 🗺️ Funcionalidades Disponíveis

- **2º Turno Presidencial (Hoje — 25/10/2026 Ao Vivo)**:
  - Disputa direta entre Flávio Bolsonaro (PL) e Lula (PT).
  - Indicador de apuração em tempo real com barra de progresso oficial.
  - Votos válidos, brancos, nulos e taxa de abstenção nacional.
  - Quadro completo dos 27 estados com contagem e margens.
- **Alternador de Pleitos Presidenciais**:
  - **1º Turno (04/10/2026)**: Detalhamento com todas as candidaturas da primeira rodada.
  - **2022 (2º Turno)**: Histórico da eleição passada.
  - **2022 (1º Turno)**: Histórico completo de 2022.
- **Painel da Bancada do Senado 2026**:
  - Composição completa das 54 vagas de senadores eleitas no 1º turno (2 por estado).
  - Distribuição partidária e mapa interativo por senador mais votado.
- **Mapa Vetorial do Brasil (IBGE)**:
  - Cores dinâmicas: Azul (Bolsonaro lidera), Vermelho (Lula lidera) e Cinza Slate (Aguardando apuração).
  - Destaque ao passar o mouse com tooltip detalhado e clique para fixar o estado no painel lateral.
- **Exportação CSV**:
  - Download imediato da planilha com os dados apurados de todos os estados.

---

## 🛠️ Especificação Técnica da API do TSE (2º Turno 2026)

- **Configuração Canônica**: `https://resultados.tse.jus.br/oficial/comum/config/ele-c.json`
- **Código do Pleito de Hoje**: `3221` (25/10/2026)
- **Código da Eleição Presidencial (2º Turno)**: `6258`
- **Código do Cargo**: `c0001` (Presidente da República)
- **Candidatos Registrados**:
  - `22`: Flávio Nantes Bolsonaro (PL)
  - `13`: Luiz Inácio Lula da Silva (PT)
- **Estrutura dos Arquivos de Dados (JSON)**:
  - Total Brasil:
    ```text
    https://resultados.tse.jus.br/oficial/ele2026/6258/dados/br/br-c0001-e006258-u.json
    ```
  - Cada Unidade da Federação:
    ```text
    https://resultados.tse.jus.br/oficial/ele2026/6258/dados/{uf}/{uf}-c0001-e006258-u.json
    ```
- **Campos Principais**:
  - `s.pst`: Percentual de seções totalizadas.
  - `carg[0].agr[].par[].cand[]`: Lista de candidatos com votos nominais (`vap`) e percentual (`pvap`).
  - `e.pa`: Percentual de abstenção.
  - `dg` e `hg`: Data e hora de geração do boletim.

---

## 📁 Estrutura do Projeto

```
e:\_Git\Resultados/
├── index.html            # Dashboard web interativo com mapa SVG e alternador de eleições
├── election_data.json    # Base com dados ao vivo de hoje (2026) e histórico de 2022
├── atualizar_dados.py    # Script que consome a API oficial do TSE em tempo real
├── server.py             # Servidor Python local com rota de atualização ao vivo
├── tse_api_client.py     # Biblioteca cliente para consulta genérica aos serviços do TSE
├── brazil_states.geojson # Coordenadas cartográficas oficiais do IBGE
└── README.md             # Documentação completa
```
