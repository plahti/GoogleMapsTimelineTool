# Visit Locator - Python Script

Tämä Python-skripti analysoi paikkatietoja (semanttisia segmenttejä) ja palauttaa niistä tietoa paikkakäynneistä, jotka sijaitsevat tietyllä etäisyydellä määritellyistä koordinaateista. Skripti käyttää `geopy`-kirjastoa paikkatietojen käsittelyyn ja Nominatim-geokooderia osoitteiden hakemiseen.

Alle viiden minuutin käyntejä ei huomioida, ne katsotaan paikan ohi ajamiseksi. 

Jos samassa paikassa ollaan 24 h sisällä uudestaan, se katsotaan samaksi käynniksi.

Sijainneista lasketaan keskiarvo ja osoite määritellään sen perusteella.

Ohjelman toimintalogiikka on varsin yksinkertainen ja se saattaa joissain tilanteissa aiheuttaa virheitä.

## Ominaisuudet

- Analysoi paikkatiedot (JSON-formaatissa).
- Palauttaa vierailut, jotka sijaitsevat annetun koordinaatin säteellä.
- Käyttää paikallista kieltä (tai englantia) osoitteiden palauttamiseen.
- Välimuistittaa geokoodauskutsut parantamaan suorituskykyä.
- Tulostaa vierailut, niiden keston ja osoitteet.

## Asennus

Asenna tarvittavat riippuvuudet:

```bash
pip install geopy
```

## Käyttö

```
python3 find_visits_at_locations.py <data.json> <latitude> <longitude> <distance>
```

Esimerkkinä käynnit Helsingissä. Kaikki alle 3000 m sisällä olevat pisteet lasketaan samaksi paikaksi.

```
python3 find_visits_at_locations.py <data.json> 60.169269 24.942484 3000
```

## Apuohjelmat

### Etsi aikavälejä, joissa on aukkoja.

```
 find_gaps <data.json> <min_gap_hours>
```

### Aikajanatiedostojen yhdistäminen

Jos sinulla on jostain syystä useita aikajanatiedostoja, niiden yhdistäminen onnistuu tällä komennolla. Tulos tulee tiedostoon nykyiseen hakemistoon merged.json

```
merge_timeline_files.py [-h] files [files ...]
```

Esimerkki:

```
python3 merge_timeline_files.py /tmp/Aikajana*
```

Mallitiedosto testausta varten

```
do_example_tests
```

# Aikajanatiedosto hankkiminen

## How to Download Your Timeline Data

### On Android Devices:
1. Open Settings on your device.
2. Navigate to Device Settings.
3. Scroll down to Location and tap on Location Services.
4. Locate Timeline (this might be labeled differently, like "Location History" or similar).
5. Tap Export Timeline Data (or a similar option depending on your device).
6, Choose a location to save your exported timeline file.
7. Once exported, copy the file to your computer.

Note: The steps may vary slightly depending on your Android device and version.

###  On iOS Devices (not tested):
Unfortunately, the exact steps to export timeline data from iOS are not clear. As of now, exporting location history from iOS might require using the Google Maps Timeline (if you have location history enabled with Google). You can follow the steps below:

1. Open the Google Maps app.
2. Tap on your profile picture in the top-right corner.
3. Go to Your Timeline.
4. Select the gear icon (settings) in the bottom-right corner.
5. Tap on Export Your Data to download your timeline history.

If you're not using Google Maps for location tracking, you may need to refer to Apple’s documentation or third-party apps for further instructions.

## Finding coordinates Easily:

To get precise coordinates (latitude and longitude), in Scandinavia you can use the Eniro Map:

Visit Eniro Map https://kartor.eniro.se/ to find a location.

Enter the desired location on the map to get its coordinates using coordinate tool in right bottom corner.

Copy the coordinates for use in your timeline processing.

Example: Coordinates for Turku, Finland are: 60.451581 22.275494.