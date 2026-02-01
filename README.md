# 🛰️ NetScanner CLI
> **The Ralph Experiment**: Test di generazione autonoma di codice tramite loop IA su Windows.

**NetScanner** è un tool a riga di comando (CLI) in Python sviluppato per la scansione di reti locali. Il progetto è stato creato come "Proof of Concept" per dimostrare come un agente IA autonomo possa gestire l'intero ciclo di sviluppo in ambiente Windows.

---

## 🤖 Il Progetto Ralph
NetScanner non è stato scritto manualmente. È il risultato di un **Autonomous Coding Loop**:
- **AI Engine**: Claude Code (Anthropic).
- **Orchestratore**: `ralph.sh` (Script Bash ottimizzato per Windows).
- **Metodo**: L'IA ha interpretato un file `prd.json`, pianificato i task e iterato autonomamente fino al completamento delle User Stories.

Questa repository documenta le soluzioni tecniche adottate per far girare Claude Code su Windows, superando i limiti di path, encoding e shell.

---

## ✨ Funzionalità
- **Rilevamento Interfacce**: Identifica schede di rete attive e subnet (psutil).
- **Discovery Host**: Ping sweep parallelo per trovare dispositivi connessi.
- **Port Scanner**: Scansione TCP multi-threaded rapida.
- **UI Moderna**: Tabelle e progress bar grazie alla libreria `Rich`.
- **Gestione Progetto**: Basato su `uv` per performance e isolamento.

---

## 📁 Struttura del Codice
- `cli.py`: Entry point e gestione comandi (Typer).
- `network.py`: Logica di analisi della rete.
- `discovery.py`: Motore di ricerca host.
- `scanner.py`: Scanner di porte TCP.
- `output.py`: Formattazione visuale dei risultati.
- `services.py`: Mapping porte/servizi

---

## 🛠️ Installazione e Uso

### Prerequisiti
- Python 3.10+
- [uv](https://astral.sh/uv/)

### Setup
```bash
git clone [https://github.com/tuo-username/netscanner.git](https://github.com/tuo-username/netscanner.git)
cd netscanner
uv sync 


``
# Info rete
uv run netscanner info

# Scansione completa
uv run netscanner scan --ports 1-1024 --threads 100
`` 
