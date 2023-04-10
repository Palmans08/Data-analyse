import mariadb
import numpy as np
import matplotlib.pyplot as plt
import datetime
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

cur.execute('SELECT * FROM gezet')
gezet = cur.fetchall()
conn.close()

geleverd_np = np.array(geleverd)
gezet_np = np.array(gezet)

geleverd_rot = np.rot90(geleverd_np,1)

leverancier_geleverd = geleverd_rot[0].astype('U50')
dosis_geleverd = geleverd_rot[1].astype(int)
datum_geleverd = geleverd_rot[2].astype('M8[D]')

#rot90 gezet tbl
gezet_rot = np.rot90(gezet_np,1)

hoeveelheid_dosis_gezet = gezet_rot[0].astype(int)
typedosis_gezet = gezet_rot[1].astype('U50')
leverancier_gezet = gezet_rot[2].astype('U50')
geslacht_gezet = gezet_rot[3].astype('U50')
leeftijdsgroep_gezet = gezet_rot[4].astype('U50')
regio_gezet = gezet_rot[5].astype('U50')
datum_gezet = gezet_rot[6].astype('M8[D]')

periode = np.arange('2020-12-28', '2021-05-19', dtype="datetime64[D]")

unique_leverancier_geleverd = np.unique(leverancier_geleverd)

unique_leverancier_gezet = np.unique(leverancier_gezet)

#1 Geleverd vs toegediend
geleverde_vaccins_arr, toegediende_vaccins_arr= [], []
geleverde_dosis, gezet_dosis = 0, 0
for x in np.nditer(periode):
    dosis_gel = np.sum(dosis_geleverd[np.where(datum_geleverd == x)])
    geleverde_dosis += dosis_gel
    geleverde_vaccins_arr.append(geleverde_dosis)
    
    dosis_gezet_per_dag = np.sum(hoeveelheid_dosis_gezet[np.where(datum_gezet == x)])
    gezet_dosis += dosis_gezet_per_dag
    toegediende_vaccins_arr.append(gezet_dosis)
    
vaccins_in_voorraad = np.subtract(geleverde_vaccins_arr, toegediende_vaccins_arr)

plt.title('Geleverd vs toegediend')
plt.plot(periode, geleverde_vaccins_arr, c ='m', label = 'geleverde vaccins')
plt.plot(periode, toegediende_vaccins_arr, c ='b', label = 'toegediende vaccins')
plt.plot(periode, vaccins_in_voorraad, c ='r', label = 'vaccins in voorraad')
plt.legend()
plt.show()

#2 Dosissen toegediend(TOTAAL) (Absolute waarden/Procentuele waarden)
eerste_dosis_arr, finale_dosis_arr, eerste_dosis_procentueel_arr, finale_dosis_procentueel_arr, dagelijks_toeg_eerste_dosis_arr, dagelijks_toeg_finale_dosis_arr, gemiddelde_buffer_arr, gemiddelde_arr = [], [], [], [], [], [], [], []
eerste_dosis, finale_dosis, eerste_dosis_procentueel, finale_dosis_procentueel = 0, 0, 0, 0
totaal_dosis = np.sum(hoeveelheid_dosis_gezet)
buffer = 7
for x in np.nditer(periode):
    
    eerste_dosis_gez = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, typedosis_gezet == 'A'))])
    eerste_dosis += eerste_dosis_gez
    eerste_dosis_arr.append(eerste_dosis)
    eerste_dosis_procentueel = np.round(eerste_dosis / totaal_dosis * 100, 2)
    eerste_dosis_procentueel_arr.append(eerste_dosis_procentueel)
    dagelijks_toeg_eerste_dosis_arr.append(eerste_dosis_gez)
    
    finale_dosis_gez = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))])
    finale_dosis += finale_dosis_gez
    finale_dosis_arr.append(finale_dosis)
    finale_dosis_procentueel = np.round(finale_dosis / totaal_dosis * 100, 2)
    finale_dosis_procentueel_arr.append(finale_dosis_procentueel)
    dagelijks_toeg_finale_dosis_arr.append(finale_dosis_gez)
    
    gemiddelde_buffer_arr.append(eerste_dosis_gez + finale_dosis_gez)
    if (len(gemiddelde_buffer_arr) < 7):
        gemiddelde_arr.append(np.round(np.average(gemiddelde_buffer_arr),2))
    elif (len(gemiddelde_buffer_arr) >= 7 and (len(gemiddelde_buffer_arr) <= len(periode)-7)):
        gemiddelde_arr.append(np.round(np.average(gemiddelde_buffer_arr[-7:]),2))
    else:
        gemiddelde_arr.append(np.round(np.average(gemiddelde_buffer_arr[-buffer:]),2))
        buffer -= 1

plt.subplot(1, 2, 1)
plt.plot(periode, eerste_dosis_arr, c = 'y', label = '1ste van 2 dosissen')
plt.plot(periode, finale_dosis_arr, c = 'g', label = 'finale dosis')
plt.title('Absolute waarden')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(periode, eerste_dosis_procentueel_arr, c = 'y', label = '1ste van 2 dosissen')
plt.plot(periode, finale_dosis_procentueel_arr, c = 'g', label = 'finale dosis')
plt.title('Procentuele waarden')
plt.legend()

plt.suptitle('Dosissen toegediend(TOTAAL)')
plt.show()
#3 Dagelijks toegediend
plt.plot(periode, gemiddelde_arr, color = 'b', label = '7-daags gemiddelde')
plt.bar(periode, dagelijks_toeg_eerste_dosis_arr, color = 'y', label = '1ste van 2 dosissen', width=0.8)
plt.bar(periode, dagelijks_toeg_finale_dosis_arr, color = 'g', label = 'finale dosis', width=0.8)
plt.title('Dagelijks toegediend')
plt.legend()
plt.show()

#4 Wekelijks toegediend
dagelijks_gezet_eerste_dosis, dagelijks_gezet_finale_dosis = [], []
weeknumber = []
periode_string = np.array(periode, dtype='U50')

for x in periode_string:
    if (x[5:6] == '0'):
        weeknumber.append(datetime.date(int(x[0:4]),int(x[6:7]),int(x[-2:])).strftime('%V'))
    else:
        weeknumber.append(datetime.date(int(x[0:4]),int(x[5:7]),int(x[-2:])).strftime('%V'))

for x in np.nditer(periode):
    dagelijks_gezet_eerste_dosis.append(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, typedosis_gezet == 'A'))]))
    dagelijks_gezet_finale_dosis.append(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))]))

weeknr_indexes = np.unique(weeknumber, return_index=True)[1]
order_weeknr = np.array([weeknumber[index] for index in sorted(weeknr_indexes)], dtype=int)
weeknumber_arr = np.asarray(weeknumber, dtype=int)

dagelijks_gezet_eerste_dosis = np.asarray(dagelijks_gezet_eerste_dosis, dtype=int)
dagelijks_gezet_finale_dosis = np.asarray(dagelijks_gezet_finale_dosis, dtype=int)

week_gezet_eerste_dosis, week_gezet_finale_dosis = [], []
for x in np.nditer(order_weeknr):
    week_gezet_eerste_dosis.append(np.sum(dagelijks_gezet_eerste_dosis[np.where(weeknumber_arr == x)]))
    week_gezet_finale_dosis.append(np.sum(dagelijks_gezet_finale_dosis[np.where(weeknumber_arr == x)]))

x_weeknummers = []
for i in order_weeknr:
    x_weeknummers.append(f'w{i}')


a = np.asarray(week_gezet_eerste_dosis, dtype=int)
b = np.asarray(week_gezet_finale_dosis, dtype=int)
plt.bar(x_weeknummers, a, color = 'y', label = '1ste van 2 dosissen')
plt.bar(x_weeknummers, b, bottom = a, color = 'g', label = 'finale dosis')
plt.title('Wekelijks toegediend')
plt.legend()
plt.show()

#5 Leveringen producenten Totaal aantal leveringen per producent
naam_ontvangen_lev = np.unique(leverancier_geleverd)
naam_leveranciers = np.array([naam_ontvangen_lev[3], naam_ontvangen_lev[2], naam_ontvangen_lev[0], naam_ontvangen_lev[1]])

leverancier_Pfizer_BioNTech_arr, leverancier_Moderna_arr, leverancier_AstraZeneca_Oxford_arr, leverancier_Johnson_Johnson_arr = [], [], [], []
geleverde_dosis_Pfizer_BioNTech, geleverde_dosis_Moderna, geleverde_dosis_AstraZeneca_Oxford, geleverde_dosis_Johnson_Johnson = 0, 0, 0, 0
for x in np.nditer(periode):
    dosis_gel_pf = np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[0]))])
    geleverde_dosis_Pfizer_BioNTech += dosis_gel_pf
    leverancier_Pfizer_BioNTech_arr.append(geleverde_dosis_Pfizer_BioNTech)
    
    dosis_gel_mo = np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[1]))])
    geleverde_dosis_Moderna += dosis_gel_mo
    leverancier_Moderna_arr.append(geleverde_dosis_Moderna)
    
    dosis_gel_ast = np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[2]))])
    geleverde_dosis_AstraZeneca_Oxford += dosis_gel_ast
    leverancier_AstraZeneca_Oxford_arr.append(geleverde_dosis_AstraZeneca_Oxford)
    
    dosis_gel_jj = np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[3]))])
    geleverde_dosis_Johnson_Johnson += dosis_gel_jj
    leverancier_Johnson_Johnson_arr.append(geleverde_dosis_Johnson_Johnson)

plt.subplot(1, 2, 1)
plt.plot(periode, leverancier_Pfizer_BioNTech_arr, c = 'b', label = naam_leveranciers[0])
plt.plot(periode, leverancier_Moderna_arr, c = 'r', label = naam_leveranciers[1])
plt.plot(periode, leverancier_AstraZeneca_Oxford_arr, c = 'y', label = naam_leveranciers[2])
plt.plot(periode, leverancier_Johnson_Johnson_arr, c = 'g', label = naam_leveranciers[3])
plt.title('Totaal aantal leveringen per producent')
plt.legend()

#5/2 Verhouding van de totale leveringen per producent
totale_leveringen_per_producent_percentage_arr = []
totaal_aantal_levering = np.sum(dosis_geleverd)

for x in np.nditer(naam_leveranciers):
    totale_leveringen_per_producent_percentage_arr.append(np.round(np.sum(dosis_geleverd[np.where(leverancier_geleverd == x)]) / totaal_aantal_levering * 100))

kleuren = ['b', 'r', 'y', 'g']
total = np.sum(totale_leveringen_per_producent_percentage_arr)
plt.subplot(1, 2, 2)
plt.title('Verhouding van de totale leveringen per producent')
plt.pie(totale_leveringen_per_producent_percentage_arr, labels= naam_leveranciers, colors = kleuren, autopct=lambda p: '{:.0f}%'.format(p * total / 100))
plt.suptitle('Leveringen producenten')
plt.show()

#6 Wekelijks geleverde dosissen
naam_ontvangen_lev = np.unique(leverancier_geleverd)
naam_leveranciers = np.array([naam_ontvangen_lev[3], naam_ontvangen_lev[2], naam_ontvangen_lev[0], naam_ontvangen_lev[1]])
elke_dag_geleverde_dosissen_ph, elke_dag_geleverde_dosissen_mo, elke_dag_geleverde_dosissen_az, elke_dag_geleverde_dosissen_jj = [], [], [], []

for x in np.nditer(periode):
    elke_dag_geleverde_dosissen_ph.append(np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[0]))]))
    elke_dag_geleverde_dosissen_mo.append(np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[1]))]))
    elke_dag_geleverde_dosissen_az.append(np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[2]))]))
    elke_dag_geleverde_dosissen_jj.append(np.sum(dosis_geleverd[np.where(np.logical_and(datum_geleverd == x, leverancier_geleverd == naam_leveranciers[3]))]))

elke_dag_geleverde_dosissen_ph = np.asarray(elke_dag_geleverde_dosissen_ph, dtype=int)
elke_dag_geleverde_dosissen_mo = np.asarray(elke_dag_geleverde_dosissen_mo, dtype=int)
elke_dag_geleverde_dosissen_az = np.asarray(elke_dag_geleverde_dosissen_az, dtype=int)
elke_dag_geleverde_dosissen_jj = np.asarray(elke_dag_geleverde_dosissen_jj, dtype=int)

week_geleverde_dosissen_ph, week_geleverde_dosissen_mo, week_geleverde_dosissen_az, week_geleverde_dosissen_jj = [], [], [], []
for x in np.nditer(order_weeknr):
    week_geleverde_dosissen_ph.append(np.sum(elke_dag_geleverde_dosissen_ph[np.where(weeknumber_arr == x)]))
    week_geleverde_dosissen_mo.append(np.sum(elke_dag_geleverde_dosissen_mo[np.where(weeknumber_arr == x)]))
    week_geleverde_dosissen_az.append(np.sum(elke_dag_geleverde_dosissen_az[np.where(weeknumber_arr == x)]))
    week_geleverde_dosissen_jj.append(np.sum(elke_dag_geleverde_dosissen_jj[np.where(weeknumber_arr == x)]))

a = np.asarray(week_geleverde_dosissen_ph, dtype=int)
b = np.asarray(week_geleverde_dosissen_mo, dtype=int)
c = np.asarray(week_geleverde_dosissen_az, dtype=int)
d = np.asarray(week_geleverde_dosissen_jj, dtype=int)
plt.bar(x_weeknummers, a, color = 'b', label = 'Pfizer/BioNTech')
plt.bar(x_weeknummers, b, bottom = a, color = 'r', label = 'Moderna')
plt.bar(x_weeknummers, c, bottom = a + b, color = 'y', label = 'AstraZeneca/Oxford')
plt.bar(x_weeknummers, d, bottom = a + b + c, color = 'g', label = 'Johnson&Johnson')
plt.title('Wekelijks geleverde dosissen')
plt.legend()
plt.show()

#7 Vaccinaties per leeftijdscategorie
mensen_per_leeftijdscategorie = np.array([2318719, 2418119, 1503690, 1525508, 1548656, 1204262, 726147, 338907])
finale_dosis_pl, eerste_dosis_pl = 0, 0
finale_dosis_pl_perc, eerste_dosis_pl_perc = [], []
leeftijdscategorie = np.unique(leeftijdsgroep_gezet)

vaccins_per_leeftijd_percentueel =  np.array([])
vaccins_per_leeftijd_percentueel_label = np.array([])
index = 0
for x in np.nditer(leeftijdscategorie):
    finale_dosis_pl = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(leeftijdsgroep_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))])
    eerste_dosis_pl = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(leeftijdsgroep_gezet == x, typedosis_gezet == 'A'))])
    
    finale_dosis_pl_perc.append(np.round(100/mensen_per_leeftijdscategorie[np.where(leeftijdscategorie == x)] * finale_dosis_pl,2))
    eerste_dosis_pl_perc.append((np.round(100/mensen_per_leeftijdscategorie[np.where(leeftijdscategorie == x)] * (eerste_dosis_pl - finale_dosis_pl),2)))

    vaccins_per_leeftijd_percentueel = np.append(vaccins_per_leeftijd_percentueel, np.round((eerste_dosis_pl_perc[index] + finale_dosis_pl_perc[index]),2))
    vaccins_per_leeftijd_percentueel_label = np.append(vaccins_per_leeftijd_percentueel_label, (f'{vaccins_per_leeftijd_percentueel[index]}%'))
    index += 1

plt.subplot(1, 2, 1)
barplot = plt.barh(leeftijdscategorie, vaccins_per_leeftijd_percentueel, color = 'y')
plt.bar_label(barplot, vaccins_per_leeftijd_percentueel_label, color = 'y', padding=3)
plt.title('Vaccinaties per leeftijdscategorie')

#7/2 Vaccinaties per geslacht
aantal_per_geslacht = np.array([5708902, 5875106])
vaccins_per_geslacht_percentueel =  np.array([])
vaccins_per_geslacht_percentueel_label = np.array([])
finale_dosis_pl, eerste_dosis_pl = 0, 0
finale_dosis_pl_perc, eerste_dosis_pl_perc = [], []
geslacht_gezet_plot = np.array(['M', 'F'])
index = 0

for x in np.nditer(geslacht_gezet_plot):
    eerste_dosis_pl = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(geslacht_gezet == x, typedosis_gezet == 'A'))])
    finale_dosis_pl = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(geslacht_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))])
    
    finale_dosis_pl_perc.append(np.round(100/aantal_per_geslacht[np.where(geslacht_gezet_plot == x)] * finale_dosis_pl,2))
    eerste_dosis_pl_perc.append((np.round(100/aantal_per_geslacht[np.where(geslacht_gezet_plot == x)] * (eerste_dosis_pl - finale_dosis_pl),2)))

    vaccins_per_geslacht_percentueel = np.append(vaccins_per_geslacht_percentueel, np.round((eerste_dosis_pl_perc[index] + finale_dosis_pl_perc[index]),2))
    vaccins_per_geslacht_percentueel_label = np.append(vaccins_per_geslacht_percentueel_label, (f'{vaccins_per_geslacht_percentueel[index]}%'))
    index += 1

plt.subplot(1, 2, 2)
barplot = plt.barh(geslacht_gezet_plot, vaccins_per_geslacht_percentueel, color = 'y')
plt.bar_label(barplot, vaccins_per_geslacht_percentueel_label, color = 'y', padding=3)
plt.title('Vaccinaties per geslacht')
plt.show()

#8 Vaccinaties per regio (Volledig gevaccineerden per 100 inwoners)
voll_gev_brussel_arr, voll_gev_vlaanderen_arr, voll_gev_wallonie_arr, voll_gev_oostkantons_arr = [], [], [], []
voll_gev_brussel, voll_gev_vlaanderen, voll_gev_wallonie, voll_gev_oostkantons = 0, 0, 0, 0
niet_gesorteerd_regio = np.unique(regio_gezet)
bevolking_land_en_per_regio = np.array([1222637, 6698876, 3583891, 78604])
gesorteerde_regio = np.array([niet_gesorteerd_regio[0], niet_gesorteerd_regio[1], niet_gesorteerd_regio[4], niet_gesorteerd_regio[3]])

for x in np.nditer(periode):
    for index, i in np.ndenumerate(gesorteerde_regio):
        if (index == (0,)):
            dosis_a = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'A'))])
            dosis_b = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'B'))])
            dosis_c = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'C'))])
            dosis_gezet_br = (dosis_a - dosis_b) + dosis_c
            voll_gev_brussel +=  dosis_gezet_br / (bevolking_land_en_per_regio[index] / 100)
            voll_gev_brussel_arr.append(voll_gev_brussel)
        if (index == (1,)):
            dosis_a = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'A'))])
            dosis_b = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'B'))])
            dosis_c = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'C'))])
            dosis_gezet_vl = (dosis_a - dosis_b) + dosis_c
            voll_gev_vlaanderen += dosis_gezet_vl / (bevolking_land_en_per_regio[index] / 100)
            voll_gev_vlaanderen_arr.append(voll_gev_vlaanderen)
        if (index == (2,)):
            dosis_a = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'A'))])
            dosis_b = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'B'))])
            dosis_c = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'C'))])
            dosis_gezet_wa = (dosis_a - dosis_b) + dosis_c
            voll_gev_wallonie += dosis_gezet_wa  / (bevolking_land_en_per_regio[index] / 100)
            voll_gev_wallonie_arr.append(voll_gev_wallonie)
        if (index == (3,)):
            dosis_a = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'A'))])
            dosis_b = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'B'))])
            dosis_c = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i, typedosis_gezet == 'C'))])
            dosis_gezet_oo = (dosis_a - dosis_b) + dosis_c
            voll_gev_oostkantons += dosis_gezet_oo / (bevolking_land_en_per_regio[index] / 100)
            voll_gev_oostkantons_arr.append(voll_gev_oostkantons)
plt.subplot(1, 2, 1)
plt.plot(periode, voll_gev_brussel_arr, c = 'b', label = 'Brussel')
plt.plot(periode, voll_gev_vlaanderen_arr, c = 'y', label = 'Vlaanderen')       
plt.plot(periode, voll_gev_wallonie_arr, c = 'r', label = 'Wallonië')
plt.plot(periode, voll_gev_oostkantons_arr, c = 'm', label = 'Oostkantons')
plt.title('Volledig gevaccineerden per 100 inwoners')
plt.legend()
#8/2 Toegediende dosissen per 100 inwoners
toege_brussel_arr, toege_vlaanderen_arr, toege_wallonie_arr, toege_oostkantons_arr, toeg_belgie_arr = [], [], [], [], []
toege_brussel, toege_vlaanderen, toege_wallonie, toege_oostkantons, toege_belgie = 0, 0, 0, 0, 0
bevolking_land_en_per_regio_all = np.array([1222637, 6698876, 3583891, 78604, 11584008])
gesorteerde_regio_all = np.append(gesorteerde_regio, 'België')

for x in np.nditer(periode):
    for index, i in np.ndenumerate(gesorteerde_regio_all):
        if (index == (0,)):
            toeg_br = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i))])
            toege_brussel +=  toeg_br / (bevolking_land_en_per_regio_all[index] / 100)
            toege_brussel_arr.append(toege_brussel)
        if (index == (1,)):
            toeg_vl = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i))])
            toege_vlaanderen +=  toeg_vl / (bevolking_land_en_per_regio_all[index] / 100)
            toege_vlaanderen_arr.append(toege_vlaanderen)
        if (index == (2,)):
            toeg_wa = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i))])
            toege_wallonie +=  toeg_wa / (bevolking_land_en_per_regio_all[index] / 100)
            toege_wallonie_arr.append(toege_wallonie)
        if (index == (3,)):
            toeg_oo = np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(datum_gezet == x, regio_gezet == i))])
            toege_oostkantons +=  toeg_oo / (bevolking_land_en_per_regio_all[index] / 100)
            toege_oostkantons_arr.append(toege_oostkantons)
        if (index == (4,)):
            toeg_be = np.sum(hoeveelheid_dosis_gezet[np.where(datum_gezet == x)])
            toege_belgie +=  toeg_be / (bevolking_land_en_per_regio_all[index] / 100)
            toeg_belgie_arr.append(toege_belgie)

plt.subplot(1, 2, 2)
plt.plot(periode, voll_gev_brussel_arr, c = 'b', label = 'Brussel')
plt.plot(periode, voll_gev_vlaanderen_arr, c = 'y', label = 'Vlaanderen')       
plt.plot(periode, voll_gev_wallonie_arr, c = 'r', label = 'Wallonië')
plt.plot(periode, voll_gev_oostkantons_arr, c = 'm', label = 'Oostkantons')
plt.plot(periode, voll_gev_oostkantons_arr, c = 'g', label = 'België')
plt.title('Toegediende dosissen per 100 inwoners')
plt.suptitle('Vaccinaties per regio')
plt.legend()
plt.show()

#9 Vaccinatiecampagne per regio (België/Vlaanderen/Oostkantons/Brussel/Wallonië)
niet_gesorteerd_regio = np.unique(regio_gezet)
gesorteerde_regio = np.array(['België', niet_gesorteerd_regio[1], niet_gesorteerd_regio[3], niet_gesorteerd_regio[0], niet_gesorteerd_regio[4]])
vaccinatiecampagne_belgie_arr, vaccinatiecampagne_vlaanderen_arr, vaccinatiecampagne_oostkantons_arr, vaccinatiecampagne_brussel_arr, vaccinatiecampagne_wallonie_arr = [], [], [], [], []

bevolking_land_en_per_regio = np.array([11584008, 6698876, 78604, 1222637, 3583891])
for index, x in np.ndenumerate(gesorteerde_regio):
    eerste_dosis, volledig = 0, 0
    if (index == (0,)):
        eerste_dosis = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(typedosis_gezet == 'A')] / bevolking_land_en_per_regio[index] * 100))
        volledig = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C'))] / bevolking_land_en_per_regio[index] * 100))
        vaccinatiecampagne_belgie_arr = [eerste_dosis, volledig, (100 - (eerste_dosis + volledig))]
    if (index == (1,)):
        eerste_dosis = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, typedosis_gezet == 'A'))] / bevolking_land_en_per_regio[index] * 100))
        volledig = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))] / bevolking_land_en_per_regio[index] * 100))
        vaccinatiecampagne_vlaanderen_arr = [eerste_dosis, volledig, (100 - (eerste_dosis + volledig))]
    if (index == (2,)):
        eerste_dosis = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, typedosis_gezet == 'A'))] / bevolking_land_en_per_regio[index] * 100))
        volledig = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))] / bevolking_land_en_per_regio[index] * 100))
        vaccinatiecampagne_oostkantons_arr = [eerste_dosis, volledig, (100 - (eerste_dosis + volledig))]
    if (index == (3,)):
        eerste_dosis = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, typedosis_gezet == 'A'))] / bevolking_land_en_per_regio[index] * 100))
        volledig = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))] / bevolking_land_en_per_regio[index] * 100))
        vaccinatiecampagne_brussel_arr = [eerste_dosis, volledig, (100 - (eerste_dosis + volledig))]
    if (index == (4,)):
        eerste_dosis = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, typedosis_gezet == 'A'))] / bevolking_land_en_per_regio[index] * 100))
        volledig = np.round(np.sum(hoeveelheid_dosis_gezet[np.where(np.logical_and(regio_gezet == x, np.logical_or(typedosis_gezet == 'B', typedosis_gezet == 'C')))] / bevolking_land_en_per_regio[index] * 100))
        vaccinatiecampagne_wallonie_arr = [eerste_dosis, volledig, (100 - (eerste_dosis + volledig))]


label =  ['1ste dosis', 'volledig', 'ongevaccineerd']
kleur = ['y', 'g', 'b']
font_title = {'size': 10, 'weight' : 'bold'}
pie_text_props = {'fontsize' : 7}

total = np.sum(vaccinatiecampagne_belgie_arr)
plt.subplot(3, 2, 1)
plt.pie(vaccinatiecampagne_belgie_arr,labels = label, colors = kleur,autopct = lambda p: '{:.0f}%'.format(p * total / 100), textprops = pie_text_props)
plt.title('België', fontdict = font_title)

total = np.sum(vaccinatiecampagne_brussel_arr)
plt.subplot(3, 2, 2)
plt.pie(vaccinatiecampagne_brussel_arr,labels = label, colors = kleur,autopct = lambda p: '{:.0f}%'.format(p * total / 100), textprops = pie_text_props)
plt.title('Brussel', fontdict = font_title)

total = np.sum(vaccinatiecampagne_vlaanderen_arr)
plt.subplot(3, 2, 3)
plt.pie(vaccinatiecampagne_vlaanderen_arr,labels = label, colors = kleur,autopct = lambda p: '{:.0f}%'.format(p * total / 100), textprops = pie_text_props)
plt.title('Vlaanderen', fontdict = font_title)

total = np.sum(vaccinatiecampagne_wallonie_arr)
plt.subplot(3, 2, 4)
plt.pie(vaccinatiecampagne_wallonie_arr,labels = label, colors = kleur,autopct = lambda p: '{:.0f}%'.format(p * total / 100), textprops = pie_text_props)
plt.title('Wallonië', fontdict = font_title)

total = np.sum(vaccinatiecampagne_oostkantons_arr)
plt.subplot(3, 2, 5)
plt.pie(vaccinatiecampagne_oostkantons_arr,labels = label, colors = kleur,autopct = lambda p: '{:.0f}%'.format(p * total / 100), textprops = pie_text_props)
plt.title('Oostkantons', fontdict = font_title)

plt.suptitle('Vaccinatiecampagne per regio')
plt.show()

#10 Aandeel bestellingen per producent (Verhouding van bestellingen per producent/Aantal bestellingen per producent)
aantal_bestellingen_per_product_arr = np.array([12500000, 5800000, 7740000, 5160000, 2900000])
aantal_bestellingen_ontvangen_arr = []
aantal_bestellingen_ontvangen = 0

naam_ontvangen_lev = np.unique(leverancier_geleverd)
naam_leveranciers = np.array([naam_ontvangen_lev[3], naam_ontvangen_lev[2], naam_ontvangen_lev[0], naam_ontvangen_lev[1], 'CureVac'])

for x in (naam_leveranciers):
    aantal_bestellingen_ontvangen = np.sum(dosis_geleverd[np.where(leverancier_geleverd == x)])
    aantal_bestellingen_ontvangen_arr.append(aantal_bestellingen_ontvangen)

sum_totaal_bestellingen = np.sum(aantal_bestellingen_per_product_arr)
totaal_bestellingen_pie_perc, totaal_bestellingen_pie_perc_zonder_totaal = np.array([]), np.array([])
index = 0
for x in aantal_bestellingen_ontvangen_arr:
    verhouding_per_product = round(aantal_bestellingen_per_product_arr[index] / sum_totaal_bestellingen * 100)
    geleverd_per_product = round((aantal_bestellingen_per_product_arr[index] - aantal_bestellingen_ontvangen_arr[index]) / sum_totaal_bestellingen * 100)
    nog_te_leveren = verhouding_per_product - geleverd_per_product
    totaal_bestellingen_pie_perc = np.append(totaal_bestellingen_pie_perc,[verhouding_per_product, geleverd_per_product, nog_te_leveren])
    totaal_bestellingen_pie_perc_zonder_totaal = np.append(totaal_bestellingen_pie_perc_zonder_totaal, [nog_te_leveren, geleverd_per_product])
    index += 1

totaal_bestellingen_pie_perc = np.reshape(totaal_bestellingen_pie_perc, (len(naam_leveranciers), 3))
totaal_bestellingen_pie_perc_zonder_totaal = np.reshape(totaal_bestellingen_pie_perc_zonder_totaal, (len(naam_leveranciers), 2))

size = 0.3
vals = totaal_bestellingen_pie_perc_zonder_totaal
cmap = plt.colormaps["tab20c"]
outer_colors = cmap(np.arange(5)*4)
inner_colors = cmap([1, 2, 5, 6, 9, 10, 13, 14, 17, 18])
label = naam_leveranciers
plt.subplot(1,2,1)
plt.pie(vals.sum(axis=1), labels= label, radius=1, colors=outer_colors,
       wedgeprops=dict(width=size, edgecolor='w'))
label = np.array(['geleverd', 'nog te leveren']*5)
plt.pie(vals.flatten(), labels = label, radius=1-size, colors=inner_colors, autopct='%.0f%%', textprops=pie_text_props,
       wedgeprops=dict(width=size, edgecolor='w'))

plt.title('Verhouding van bestellingen per producent')

x = np.arange(len(naam_leveranciers))
width = 0.20
plt.subplot(1,2,2)
plt.bar(x - width/2, aantal_bestellingen_per_product_arr, color = 'y', width = 0.20, label='totaal besteld')
plt.bar(x + width/2, aantal_bestellingen_ontvangen_arr, color = 'g', width = 0.20, label='reeds geleverd')
plt.title('Aantal bestellingen per producent')
plt.xticks(x, naam_leveranciers, fontsize = 8)
plt.legend()
plt.suptitle('Aandeel bestellingen per producent')
plt.show()