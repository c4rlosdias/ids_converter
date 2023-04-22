# ids_converter
## **🔄 Convert xlsx file to ids**

IDS converter is a converter of information requirements in xlsx (excel) files to the IDS standard (information delivery standard) developed by [buildingSMART](https://buildingsmart.org/).

Many information requirements files are prepared in excel spreadsheet format (xlsx) and are based only on property requirements that the IFC file must have.

Of course, the IDS standard goes much further than that, providing an incredible amount of checks that can be done on the information in the model. However, based on the most common requirements used in the market, I created this small app to create an IDS file just for checking the properties that a model must have, being able to add a check of values that these properties must have, but only based on constraints of 'xs:pattern' (see IDs documentation on [buildingsmart page](https://technical.buildingsmart.org/projects/information-delivery-specification-ids/))

Still in Beta version, for testing purposes, this app is open for use by anyone who wants to collaborate with the project.

(IDS Converter uses [Ifcopenshell](http://ifcopenshell.org/))

## Try on:
https://idsconverter.herokuapp.com/

## TODO:
- [ ] Include other types of restrictions accepted by the IDS;
- [X] Connection with bSDD;
- [ ] Add a IDS validator
- [ ] Add a BCF creator

For IDS documentation visit: https://github.com/buildingSMART/IDS

## Contact me:
Carlos Dias <c.dias@carlosdiasopenbim.com>
