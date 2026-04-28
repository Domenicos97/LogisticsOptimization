# Logistics Optimization

Una pipeline logistica in Python che integra **Data Quality**, **Graph Theory** e **Ricerca Operativa** per risolvere un classico problema di ottimizzazione su rete (Shortest Path / Min-Cost Flow).

## 🛠️ Architettura e Stack Tecnologico
Il progetto è strutturato in tre fasi modulari:

1. 🛡️ **Fase 1: Data Validation (Pydantic)**
   Simulando la ricezione di dati da un'API esterna, il modello intercetta i payload JSON. `Pydantic` assicura la corretta tipizzazione (Type Hinting) e applica regole di business rigorose (es. *il costo di una rotta deve essere strettamente > 0*), evitando che dati anomali raggiungano il motore di calcolo.

2. 🕸️ **Fase 2: Graph Modeling (NetworkX)**
   I dati validati vengono trasformati in un grafo pesato e direzionato (*Weighted DiGraph*). Questo permette di mappare topologicamente la rete logistica, estrarre le matrici di adiacenza e visualizzare le connessioni tra i magazzini.

3. 🧮 **Fase 3: Mathematical Optimization (Pyomo)**
   Il problema viene convertito in un modello matematico *object-oriented*. Tramite `Pyomo`, vengono definiti la Funzione Obiettivo (minimizzazione dei costi di trasporto) e i Vincoli (conservazione del flusso ai nodi). Il modello viene poi elaborato da un solver lineare open-source (`GLPK`) per l'estrazione del percorso ottimale ordinato.

## 📊 Visualizzazione della Rete Topologica
*(Il codice salva automaticamente questa mappa come file PNG nella root del progetto)*

![Rete Logistica](logistic_network.png)

## 🚀 Come eseguire il progetto in locale

1. **Clona il repository e installa le dipendenze Python:**
   ```bash
   git clone https://github.com/Domenicos97/LogisticsOptimization.git
   cd LogisticsOptimization
   pip install -r requirements.txt
   ```

2. **Installa il Solver (GLPK):**
   Per permettere a Pyomo di eseguire l'ottimizzazione matematica, è necessario un solver esterno installato nel sistema operativo.
   * **Ubuntu/Debian:** `sudo apt-get install glpk-utils`
   * **macOS:** `brew install glpk`
   * **Windows:** Scarica i binari dal sito ufficiale o usa un package manager come Conda (assicurati di aggiungere l'eseguibile al `PATH` di sistema).

3. **Avvia la pipeline:**
   ```bash
   python main.py
   ```