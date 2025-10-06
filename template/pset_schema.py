import ifcopenshell.util.pset
import pandas as pd


template = ifcopenshell.util.pset.get_template('IFC4X3_ADD2')
psets = template.templates[0].by_type('IfcPropertySetTemplate')

measure_type = {
    'Q_LENGTH' : 'IFCLENGTHMEASURE',
    'Q_AREA'   : 'IFCLENGTHMEASURE',
    'Q_VOLUME' : 'IFCLENGTHMEASURE',
    'Q_WEIGHT' : 'IFCWEIGHTMEASURE',
    'Q_COUNT'  : 'IFCCOUNTMEASURE',
    'Q_LENGTH' : 'IFCLENGTHMEASURE',
    'Q_LENGTH' : 'IFCLENGTHMEASURE',
    'Q_LENGTH' : 'IFCLENGTHMEASURE',
    'Q_LENGTH' : 'IFCLENGTHMEASURE',

}

table = {
    'property'     : [],
    'pset'         : [],    
    'templatetype' : [],
    'measuretype'  : [],
    'ifcobject'    : []
}

for pset in psets:    
    for prop in pset.HasPropertyTemplates:
        table['pset'].append(pset.Name)
        table['ifcobject'].append(pset.ApplicableEntity)
        table['property'].append(prop.Name)
        table['templatetype'].append(prop.TemplateType)

        if prop.PrimaryMeasureType is not None:
            primary_type = prop.PrimaryMeasureType.upper()
        else:
            primary_type = 'IFC' + prop.TemplateType.split('_')[1].upper() + 'MEASURE'

        table['measuretype'].append(primary_type)

df = pd.DataFrame(table)
print(df)
df.to_csv('./template/teste.csv')



