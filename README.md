🛰️ NetScanner CLI

    The Ralph Experiment: Un esperimento di generazione di codice autonoma tramite loop IA.

NetScanner è un tool a riga di comando (CLI) in Python progettato per la scoperta di host e la scansione di porte in reti locali. Questo progetto rappresenta il Proof of Concept (PoC) del sistema Ralph, un agente autonomo basato su Claude Code configurato per operare in ambiente Windows.
🤖 Genesi del Progetto: Il "Ralph Test"

A differenza dei software tradizionali, NetScanner è stato sviluppato attraverso un processo di Autonomous Coding Loop:

    Definizione: Gli obiettivi sono stati scritti in un file prd.json.

    Esecuzione: Lo script ralph.sh ha orchestrato Claude Code in un loop continuo su Git Bash.

    Sviluppo: L'IA ha analizzato i requisiti, creato la struttura delle cartelle, gestito le dipendenze con uv e implementato la logica correggendo i propri errori in tempo reale.

✨ Funzionalità

    Auto-Detection: Rilevamento automatico delle interfacce di rete attive e delle relative subnet.

    Host Discovery: Ping sweep multi-threaded per individuare dispositivi attivi nella rete.

    Port Scanner: Scansione TCP veloce (thread-pool) con identificazione dei nomi dei servizi (SSH, HTTP, ecc.).

    Rich UI: Output formattato in tabelle eleganti e barre di caricamento grazie alla libreria Rich.

    Cross-Platform: Progettato per funzionare fluidamente su Windows (via Git Bash/PowerShell) e Linux.

📁 Struttura della Repository

Il codice segue un'architettura modulare e pulita:

    network.py: Logica di rilevamento interfacce (psutil).

    discovery.py: Motore di ricerca host (ping sweep).

    scanner.py: Core del port scanning TCP.

    output.py: Gestione dell'interfaccia grafica nel terminale.

    cli.py: Entry point dell'applicazione gestito con Typer.

🚀 Installazione e Uso
Prerequisiti

    Python 3.10+

    uv (consigliato per la gestione delle dipendenze)

Setup
Bash

# Clona la repo
git clone https://github.com/tuo-username/netscanner.git
cd netscanner

# Sincronizza le dipendenze
uv sync

Comandi Disponibili

1. Vedere le info sulla propria rete:
Bash

uv run netscanner info

2. Eseguire una scansione completa:
Bash

uv run netscanner scan --ports 1-1024 --threads 100

🛠️ Come riprodurre il Test di Ralph (Windows)

Se vuoi usare la stessa architettura che ha creato questo codice:

    Assicurati che ralph.sh sia salvato con codifica LF.

    Configura il percorso del binario di Claude in ralph.sh: CLAUDE_BIN="C:/Users/TUO_UTENTE/.local/bin/claude.exe"

    Lancia il loop da Git Bash:
    Bash

    ./ralph.sh --tool claude 10

📝 Note Tecniche

Durante la generazione, Ralph ha dovuto superare sfide specifiche di Windows, come la gestione dei permessi per i comandi di ping e la corretta mappatura dei percorsi C:\ in ambiente Bash. Il risultato è un codice robusto che gestisce correttamente le eccezioni di rete e i segnali di interruzione (Ctrl+C).
