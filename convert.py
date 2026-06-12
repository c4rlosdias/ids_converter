"""
Simpel conversie script: Excel naar IDS
Gebruik: python convert.py mijn_bestand.xlsx
"""

import sys
import pandas as pd
import numpy as np
from modules.ifctester import ids


def pattern(value):
    """Converteer waarde naar IDS pattern/restriction"""
    result = None if value == '' else value
    try:
        if '|' in value:
            enums = [j.strip() for j in value.split('|')]
            if isinstance(enums[0], str):
                base = "string"
            elif isinstance(enums[0], int):
                base = "integer"
            elif isinstance(enums[0], bool):
                base = "boolean"
            else:
                base = "decimal"
            
            result = ids.Restriction(base=base, options={'enumeration': enums})
        if value[:1] == '/' and value[-1:] == '/':
            value = value[1:-1]
            if 'clusive=' in value:
                l = value.split(',')                
                options = {}
                for it in l:
                    key = it.split('=')[0].strip()
                    val = int(it.split('=')[1].strip())
                    options[key] = val
                result = ids.Restriction(base="integer", options=options)
            elif 'ength=' in value:
                l = value.split(',')
                options = {}
                for it in l:
                    key = it.split('=')[0].strip().strip()
                    val = int(it.split('=')[1].strip())
                    options[key] = val
                result = ids.Restriction(base="string", options=options)
            else:
                result = ids.Restriction(base="string", options={'pattern': value})  
        return result
    except:
        return None


def convert_excel_to_ids(excel_path):
    """Converteer Excel bestand naar IDS XML"""
    
    print(f"📥 Lezen van: {excel_path}")
    
    # Lees Excel sheets
    df_ids_information = pd.read_excel(excel_path, dtype=str, skiprows=1, sheet_name="IDS_INFORMATION")
    df_ids_information = df_ids_information.replace({np.nan: None})
    df_specifications = pd.read_excel(excel_path, dtype=str, skiprows=2, sheet_name="SPECIFICATIONS")
    df_applicability = pd.read_excel(excel_path, dtype=str, skiprows=2, sheet_name="APPLICABILITY")
    df_requirements = pd.read_excel(excel_path, dtype=str, skiprows=2, sheet_name="REQUIREMENTS")
    
    df_specifications = df_specifications.fillna('')
    df_applicability = df_applicability.fillna('')
    df_requirements = df_requirements.fillna('')
    
    # Haal IDS informatie op
    ids_info = {}
    for index, info in df_ids_information.iterrows():
        ids_info[info.iloc[0]] = info.iloc[1]
    
    print(f"📋 IDS Titel: {ids_info.get('Title', 'Geen titel')}")
    print(f"📝 Aantal specificaties: {len(df_specifications)}")
    
    # Maak IDS object
    my_ids = ids.Ids(
        title=ids_info.get('Title'),
        copyright=ids_info.get('Copyright'),
        version=ids_info.get('IDS Version'),
        author=ids_info.get('Author (email)'),
        description=ids_info.get('Description'),
        date=ids_info.get('Date'),
        purpose=ids_info.get('Purpose'),
        milestone=ids_info.get('Milestone')
    )
    
    # Verwerk elke specificatie
    for index, spec in df_specifications.iterrows():
        print(f"   ✓ Specificatie: {spec.iloc[0]}")
        
        my_spec = ids.Specification(
            name=spec.iloc[0],
            description=spec.iloc[1],
            minOccurs=0 if spec.iloc[2].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
            maxOccurs='unbounded' if spec.iloc[2].upper() in ['REQUIRED', 'OPTIONAL'] else 0,
            ifcVersion=ids_info.get('IFC Version')
        )
        
        # Filter applicability voor deze specificatie
        df_app_spec = df_applicability[df_applicability["specification"] == spec.iloc[0]]
        df_req_spec = df_requirements[df_requirements["specification"] == spec.iloc[0]]
        
        # Voeg applicability toe
        for index, row in df_app_spec.iterrows():
            entity = ids.Entity(
                name=pattern(row['entity name'].upper()),
                predefinedType=pattern(row['predefined type'].upper())
            ) if row['entity name'] != '' else None
            
            attribute = ids.Attribute(
                name=pattern(row['attribute name']),
                value=pattern(row['attribute value'])
            ) if row['attribute name'] != '' else None
            
            property = ids.Property(
                baseName=pattern(row['property name']),
                value=pattern(row['property value']),
                propertySet=pattern(row['property set']),
                dataType=row['data type'] if row['data type'] != '' else None
            ) if row['property name'] != '' else None
            
            classification = ids.Classification(
                value=pattern(row['classification reference']),
                system=pattern(row['classification system'])
            ) if row['classification reference'] != '' and row['classification system'] != '' else None
            
            material = ids.Material(
                value=pattern(row['material name'])
            ) if row['material name'] != '' else None
            
            parts = ids.PartOf(
                name=row['part of entity'].upper(),
                relation=None if row['relation'] == '' else row['relation']
            ) if row['part of entity'] != '' else None
            
            if entity:
                my_spec.applicability.append(entity)
            if attribute:
                my_spec.applicability.append(attribute)
            if property:
                my_spec.applicability.append(property)
            if classification:
                my_spec.applicability.append(classification)
            if material:
                my_spec.applicability.append(material)
            if parts:
                my_spec.applicability.append(parts)
        
        # Voeg requirements toe
        for index, row in df_req_spec.iterrows():
            row['cardinality'] = 'required' if row['cardinality'] == '' else row['cardinality']
            
            entity = ids.Entity(
                name=pattern(row['entity name'].upper()),
                predefinedType=pattern(row['predefined type'].upper()),
                instructions=row['instructions'] if row['instructions'] != '' else None
            ) if row['entity name'] != '' else None
            
            attribute = ids.Attribute(
                name=pattern(row['attribute name']),
                value=pattern(row['attribute value']),
                cardinality=row['cardinality'],
                instructions=row['instructions'] if row['instructions'] != '' else None
            ) if row['attribute name'] != '' else None
            
            property = ids.Property(
                uri=row['URI'] if row['URI'] != '' else None,
                baseName=pattern(row['property name']),
                value=pattern(row['property value']) if row['property value'] != '' else None,
                propertySet=pattern(row['property set']),
                dataType=row['data type'] if row['data type'] != '' else None,
                instructions=row['instructions'] if row['instructions'] != '' else None,
                cardinality=row['cardinality']
            ) if row['property name'] != '' else None
            
            property2 = ids.Property(
                uri=row['URI'] if row['URI'] != '' else None,
                baseName=pattern(row['property name(bSDD)'].split('[')[0].rstrip()),
                value=pattern(row['property value(bSDD)'].split('[')[0].rstrip()) if row['property value(bSDD)'] != '' else None,
                propertySet=pattern(row['property set(bSDD)'].split('[')[0].rstrip()),
                dataType=row['data type(bSDD)'].split('[')[0].rstrip() if row['data type(bSDD)'] != '' else None,
                instructions=row['instructions'] if row['instructions'] != '' else None,
                cardinality=row['cardinality']
            ) if row['property name(bSDD)'] != '' else None
            
            classification = ids.Classification(
                uri=row['URI'] if row['URI'] != '' else None,
                value=pattern(row['classification reference']),
                system=pattern(row['classification system']),
                cardinality=row['cardinality']
            ) if row['classification reference'] != '' and row['classification system'] != '' else None
            
            material = ids.Material(
                uri=row['URI'] if row['URI'] != '' else None,
                value=pattern(row['material name']),
                instructions=row['instructions'] if row['instructions'] != '' else None,
                cardinality=row['cardinality']
            ) if row['material name'] != '' else None
            
            parts = ids.PartOf(
                name=row['part of entity'].upper(),
                relation=None if row['relation'] == '' else row['relation'],
                instructions=row['instructions'] if row['instructions'] != '' else None,
                cardinality=row['cardinality']
            ) if row['part of entity'] != '' else None
            
            if entity:
                my_spec.requirements.append(entity)
            if attribute:
                my_spec.requirements.append(attribute)
            if property:
                my_spec.requirements.append(property)
            if property2:
                my_spec.requirements.append(property2)
            if classification:
                my_spec.requirements.append(classification)
            if material:
                my_spec.requirements.append(material)
            if parts:
                my_spec.requirements.append(parts)
        
        my_ids.specifications.append(my_spec)
    
    # Converteer naar XML
    ids_xml = my_ids.to_string()
    
    # Bepaal output bestandsnaam
    output_file = excel_path.replace('.xlsx', '.ids').replace('.xls', '.ids')
    
    # Schrijf naar bestand
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(ids_xml)
    
    print(f"✅ IDS bestand aangemaakt: {output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python convert.py <excel_bestand.xlsx>")
        print("Voorbeeld: python convert.py mijn_requirements.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    try:
        convert_excel_to_ids(excel_file)
    except FileNotFoundError:
        print(f"❌ Fout: Bestand niet gevonden: {excel_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fout tijdens conversie: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
