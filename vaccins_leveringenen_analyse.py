import numpy as np
import mariadb
from sys import exit

try:
    conn = mariadb.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        #port=,
        database='vaccins'
    )
except mariadb.Error as e:
    print(f'Kon geen verbinding maken met Database: {e}')
    exit()

cur = conn.cursor()

cur.execute('SELECT * FROM geleverd')
geleverd = cur.fetchall()
conn.close()

geleverd_np = np.array(geleverd)

dtypes_Arr = [('date','M8[D]'), ('amount',int), ('manufacturer','U50')]

geleverdArr = np.array(geleverd, dtype=dtypes_Arr)

# Splitsen van kolommen

# rot90() sneller dan de (geleverd_split = np.array_split(geleverd_np, 3, axis=1)) en dan 1 voor 1 flattenen()

# Met de klok mee
# geleverd_rot = np.rot90(geleverd_np,-1)
# print(geleverd_rot)

# Tegen de klok mee
geleverd_rot = np.rot90(geleverd_np)

datums = geleverd_rot[2].astype('M8[D]')
dosis = geleverd_rot[1].astype('i')
leveranciers = geleverd_rot[0]

# Som van alle geleverde vaccins
print(f'\n\nAantal totaal geleverde vaccins: {np.sum(dosis)}')

# Filteren van leverancier namen
print(f'\n\nUnieke leveranciers: {np.unique(leveranciers)}')

# Aantal keer dat een leverancier heeft geleverd
print(f'\n\nTotaal aantal keer geleverd door leveranciers: {np.unique(leveranciers, return_counts=True)}')

# Totaal aantal keer geleverd
print(f'\n\nTotaal aantal keer geleverd door leveranciers: {np.ma.count(leveranciers)}')

# Datum : aantal keer geleverd per dag
dt = np.unique(datums, return_counts=True)[0].astype('U50')
dtc = np.unique(datums, return_counts=True)[1]
print(f'\n\nAantal keer geleverd per dag: {np.stack((dt,dtc), axis=1)}')

# Waardes met meer als 100 000 leveringen
print(f'\n\nAlle aantallen vaccins dat geleverd werden met meer dan 100 000: {dosis[np.where(dosis>100000)]}')

# Leveranciers die meer dan 100 000 vaccins hebben geleverd op 1 dag
print(f'\n\nLeveranciers die meer dan 100 000 vaccins hebben geleverd op 1 dag: {leveranciers[np.where(dosis>100000)]}')

# Samenvoegen van leveranciers en geleverde dosisen boven de 100 000
print(f'\n\nDosis : leverancier die meer dan 100 000 vaccins hebben geleverd (2D array)\n{np.dstack((dosis[np.where(dosis>100000)], leveranciers[np.where(dosis>100000)]))}')

# Aantal leveringen boven de 100 000
print(f'\n\nAantal leveringen boven de 100 000: {np.ma.count(np.where(dosis>100000))}')

# Aantal vaccins geleverd op 22 februari 2021
print(f'\n\nAantal dosisen geleverd op 22-02-2021: {dosis[np.where(datums == np.datetime64("2021-02-22"))]}')

# Aantal geleverde vaccins in de maand februari 2021
print(f'\n\nTotaal aantal geleverde vaccins in de maand feb 2021: {np.sum(dosis[np.where(np.logical_and(datums> np.datetime64("2021-01-31"), datums < np.datetime64("2021-03-01")))])}')

# Sorteren op geleverd ipv datum
print(f'\n\nAantal geleverd van klein naar groot:\n{np.sort(geleverdArr, order="amount")}')
print(f'\n\nAantal geleverd van groot naar klein:\n{np.sort(geleverdArr, order="amount")[::-1]}')