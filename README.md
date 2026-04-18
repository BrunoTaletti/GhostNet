# GhostNet 👻
**Monitor de Rotação de IP & Infraestrutura**

O GhostNet é um utilitário desktop desenvolvido em Python focado no monitoramento e validação de rotação de endereços IP. Projetado com uma interface enxuta e estética *Demoscene/Terminal*, o aplicativo garante que a infraestrutura operacional permaneça segura e sem rastros reutilizados.

## Funcionalidades
- **Detecção de IP Público:** Consulta em tempo real via API `ipify`.
- **Histórico Persistente:** Valida instantaneamente se um IP já foi utilizado anteriormente pela máquina.
- **HUD Retrátil:** Interface flexível. Ative o HUD para visualizar o log de rede ou oculte-o para ocupar o mínimo de espaço na tela.
- **Auto-Update Nativo:** Validação contínua da versão atual contra as *Releases* oficiais do repositório no GitHub.

## Instalação e Execução (Desenvolvimento)
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt