# PS20-LoRa-code

Dieses Repository enthält sämtlichen Code für das LoRa-Projektseminar im WS 2020/21.

## Bestandteile

* `gps-shield`: Enthält den Sketch für die Arduino-basierte Node mit dem GPS Shield.
* `hacked-gps-shield`: Enthält den Sketch für eine "zusammengewürfelte" Node, bestehend aus dem LoRa GPS Hat für den Raspberry Pi und den Arduino Uno. Identisch zu `gps-shield` bis auf die verwendeten TTN-Credentials.
* `lora-gateway`: Enthält den Code für die genutzte Raspberry Pi Gateway Software, inklusive unserer eigenen Modifizierungen.
* `python-scripts`: Enthält alle Python-Scripts, die im Laufe des Projektseminars entstanden sind:
  * Web-App zur Betrachtung der Daten der Reichweitenmessung
  * Grabber-Script, welches ankommende Pakete von TTN abholt und in eine CSV-Datei schreibt
