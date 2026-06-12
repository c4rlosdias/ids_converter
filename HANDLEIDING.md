# IDS Converter - Handleiding voor beginners

## Wat heb je nodig?

1. **Python** - Download en installeer van [python.org](https://www.python.org/downloads/)
   - Tijdens installatie: vink "Add Python to PATH" aan!

## Eenvoudigste manier (zonder UI)

### 1. Download de bestanden
- Download deze map naar je computer

### 2. Open PowerShell in deze map
- Ga naar de map in Windows Verkenner
- Klik in de adresbalk bovenin
- Typ `powershell` en druk op Enter

### 3. Installeer de benodigde software (eenmalig)

**Voor alleen convert.py (minimaal, aangeraden):**
```powershell
pip install -r requirements-minimal.txt
```

**Voor de volledige app met UI:**
```powershell
pip install -r requirements.txt
```
Druk op Enter en wacht tot het klaar is (kan even duren).

### 4. Converteer je Excel bestand
Zet je Excel bestand in deze map en run:
```powershell
python convert.py jouw_bestand.xlsx
```
Klaar! Het .ids bestand wordt aangemaakt in dezelfde map.

## Met grafische interface

Als je liever een interface wilt:

### Stap 1-3: Zie hierboven

### Stap 4: Start de applicatie
```powershell
streamlit run Instructions.py
```

### Stap 5: Gebruik de applicatie
- Je browser opent automatisch
- Zo niet? Ga naar: http://localhost:8501
- Klik in het menu links op "💾 xlsx to IDS xml"
- Upload je Excel bestand en converteer!

## Problemen?

- **Python niet gevonden**: Installeer Python opnieuw en vink "Add to PATH" aan
- **pip werkt niet**: Probeer `python -m pip install -r requirements.txt`
- **Bestand niet gevonden**: Zorg dat je in de juiste map bent

## Online versie

Gebruik de online versie: [idsconverter.streamlit.app](https://idsconverter.streamlit.app/)
