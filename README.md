# Data-analyse
Aantal voorbeelden van data-analyse gebaseerd op data van Covid-19 (van 2020-12-28 t.e.m. 2021-05-18).

### Tools (Programma)
XAMPP (testserver, databanken lokaal beheren).

### Python modules
* MariaDB 
* NumPy
* Matplotlib

##### Voor Windows gebruikers
```
pip install mariadb
pip install numpy
pip install matplotlib
```
___
___
# Voorbereiding
1.	Start het programma XAMPP op.
	* Start Apache
	* Start MySQL
	* Klik op de knop Admin en dan phpMyAdmin.

2.	WAARSCHUWING als je standaard XAMPP gebruikt.
	* Controleer zeker na of er geen databank bestaat met als naam "vaccins".

3.	Run het bestand "create_db_and_insert_data.py".
	* Het tabel geleverd zou 49 records moeten bevatten.
	* Het tabel gezet zou 27795 records moeten bevatten.
		* Reden van het bestand "create_db_and_insert_data.py" is omdat het csv bestand van gezet te groot is om te importeren in phpMyAdmin.
		* De andere reden is omdat je 3 zaken moet anders uitvoeren, het manueel aanmaken van de databank en het importeren van de csv bestanden.
___
# Legende/uitleg DOSE
* A = eerste dosis
* B = tweede dosis
* C = vereist één dosis (m.a.w. finale dosis, je kan het bezien als A + B)
___
___

### Verwijderen van databank
1.	Ga naar phpMyAdmin
	* Server: 127.0.0.1
	* SQL
```
DROP DATABASE vaccins;
```
