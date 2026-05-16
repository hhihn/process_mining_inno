# Process Mining Exercise: Procure-to-Pay

Dieses Repository enthält einen kleinen Procure-to-Pay-Datensatz und ein exploratives Python-Skript für eine Übung im Vorlesungsteil **Process Innovation** der Veranstaltung **Innovation in the Digital Environment**.

Ziel der Übung ist es, mit Process-Mining-Daten typische Prozessprobleme sichtbar zu machen: lange Durchlaufzeiten, Bottlenecks, Prozessvarianten, Nacharbeit und Unterschiede zwischen Ländern.

## Projektstruktur

```text
.
├── data/
│   ├── Procure-to-Pay.csv
│   ├── Procure-to-Pay 2.csv
│   ├── Procure-to-Pay 3.csv
│   └── Phases_of_activities.csv
├── figures/
│   ├── 01_activity_frequency_by_phase.png
│   ├── 02_throughput_by_country.png
│   ├── 03_bottlenecks_waiting_time.png
│   ├── 04_invoice_amount_vs_throughput.png
│   ├── 05_top_variants.png
│   ├── 06_directly_follows_graph.png
│   ├── summary_metrics.csv
│   └── top_variants.csv
├── scripts/
│   └── explore_process_mining.py
├── requirements.txt
└── README.md
```

## Daten

Die drei `Procure-to-Pay*.csv`-Dateien enthalten Eventlogs mit diesen zentralen Spalten:

- `Case ID`: Prozessinstanz
- `Start Timestamp`: Startzeitpunkt eines Events
- `Complete Timestamp`: Endzeitpunkt eines Events
- `Activity`: Aktivität im Prozess
- `Resource`: ausführende Person
- `Role`: Rolle der ausführenden Person
- `Invoice amount`: Rechnungsbetrag
- `Discount`: Rabatt
- `Country`: Land

Die Datei `Phases_of_activities.csv` ordnet Aktivitäten groben Prozessphasen zu.

## Setup

Empfohlen ist eine lokale virtuelle Umgebung:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Analyse Ausführen

```bash
.venv/bin/python scripts/explore_process_mining.py
```

Das Skript schreibt alle Ergebnisse nach `figures/`.

## Erzeugte Analysen

### 1. Aktivitätshäufigkeiten Nach Phase

Datei: `figures/01_activity_frequency_by_phase.png`

Zeigt, welche Aktivitäten im Eventlog besonders häufig auftreten und zu welcher Prozessphase sie gehören.

Nutzen:

- Verständnis des Prozessaufbaus
- Identifikation dominanter Aktivitäten
- Einstieg in die Frage, wo der Prozess besonders viel Aufwand erzeugt

### 2. Durchlaufzeit Nach Land

Datei: `figures/02_throughput_by_country.png`

Vergleicht die Case-Durchlaufzeit zwischen Ländern.

Nutzen:

- Länderunterschiede erkennen
- Ausreißer sichtbar machen
- Best Practices zwischen Ländern diskutieren

### 3. Bottlenecks Über Wartezeiten

Datei: `figures/03_bottlenecks_waiting_time.png`

Zeigt Aktivitäten, nach denen besonders lange gewartet wird, bis der nächste Prozessschritt beginnt.

Nutzen:

- Engpässe erkennen
- Freigabestau, manuelle Prüfungen oder Übergabeprobleme diskutieren
- Ansatzpunkte für Automatisierung und Eskalation finden

### 4. Rechnungsbetrag, Rabatt Und Durchlaufzeit

Datei: `figures/04_invoice_amount_vs_throughput.png`

Setzt Rechnungsbetrag, Rabattquote, Land und Durchlaufzeit in Beziehung.

Nutzen:

- Prüfen, ob hohe Beträge länger dauern
- Prüfen, ob hohe Rabatte mit längeren Prozessen verbunden sind
- Diskussion über risikobasierte Freigaben

### 5. Prozessvarianten

Dateien:

- `figures/05_top_variants.png`
- `figures/top_variants.csv`

Zeigt die häufigsten Aktivitätssequenzen im Prozess.

Nutzen:

- Standardprozess vs. Varianten vergleichen
- Komplexität und Abweichungen erkennen
- Fälle mit Nacharbeit oder frühem Abbruch identifizieren

### 6. Directly-Follows Graph

Datei: `figures/06_directly_follows_graph.png`

Visualisiert die häufigsten direkten Übergänge zwischen Aktivitäten.

Nutzen:

- Hauptpfad des Prozesses erkennen
- Abzweigungen und Rücksprünge sichtbar machen
- Prozesslogik für Studierende greifbar machen

## Kennzahlen

Zusammenfassung: `figures/summary_metrics.csv`

Aktuelle Werte aus dem Datensatz:

- Events: 6.139
- Cases: 428
- Aktivitäten: 24
- Ressourcen: 27
- Länder: 4
- Median-Durchlaufzeit: ca. 11,7 Tage
- Durchschnittliche Durchlaufzeit: ca. 22,5 Tage

## Nutzung In Der Übung

Leitfragen:

1. Wo liegen die größten Bottlenecks im Prozess?
2. Welche Prozessvarianten wirken ineffizient?
3. Welche Aktivitäten deuten auf Nacharbeit, Konflikte oder Korrekturen hin?
4. Gibt es Länder mit deutlich längeren Durchlaufzeiten?
5. Hängen Rechnungsbetrag oder Rabatt mit längeren Durchlaufzeiten zusammen?
6. Welche Process-Innovation-Maßnahme würdet ihr aus den Daten ableiten?

Mögliche Innovationsideen:

- Automatisierte Vorprüfung von Purchase Requisitions
- Standardisierte Eingabeformulare zur Reduktion von Nacharbeit
- Automatische Eskalation bei langen Wartezeiten
- Regelbasierte Freigaben für niedrige Beträge
- Process-Monitoring-Dashboard für SLA-Verletzungen
- Supplier-Self-Service zur Reduktion von Rückfragen und Disputes
