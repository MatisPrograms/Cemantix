# API SWAGGER

This API works for:
- https://cemantix.certitudes.org/ - French
- https://cemantle.certitudes.org/ - English

## GET /stats
This endpoint returns the number of the word day and the number of people who have already found it.

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "https://cemantix.certitudes.org/stats" `
∙ -Method "GET" `
∙ -Headers @{
∙   "Referer"="https://cemantix.certitudes.org/"
∙ }).Content
```

- @returns {json} - {"n":number,"v":number}
- @return-params {n} - number of the word day
- @return-params {v} - number of people who have already found it

```json
{"n":1071,"v":9929}
```

## POST /nearby

This endpoint returns a list of words that are close to the word given in the body. (The word of the previous day)

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "https://cemantix.certitudes.org/nearby" `
∙ -Method "POST" `
∙ -Headers @{
∙   "Referer"="https://cemantix.certitudes.org/"
∙ } `
∙ -Body "word=montée").Content
```

- @param {word} - word of the previous day
- @returns {json} - [["word",percent,degree],...]
- @return-params {word} - word
- @return-params {percent} - percentage of similarity out of ‰
- @return-params {degree} - fun value to show hot or coldness

```json
[["mont\u00e9e",1000,100.0],["descente",999,49.82],["remont\u00e9e",998,46.36],["puissance",997,42.46],["acc\u00e9l\u00e9ration",996,41.65],["grandissant",995,40.36],["affaiblissement",994,40.3],["croissant",993,40.13],["monter",992,39.68],["effritement",991,39.58],["ascension",990,39.32],["d\u00e9sescalade",989,38.64],["essoufflement",988,37.86],["chute",987,37.77],["d\u00e9clin",986,37.64],["pentu",985,37.37],["accroissement",984,36.87],["redescendre",983,36.76],["marche",982,36.53],["acc\u00e9l\u00e9rer",981,36.5],["raidillon",980,36.37],["redescente",979,36.19],["multiplication",978,35.97],["d\u00e9crue",977,35.86],["radicalisation",976,35.78],["fl\u00e9chissement",975,35.75],["d\u00e9nivel\u00e9",974,35.58],["progressif",973,35.57],["raide",972,35.5],["pouss\u00e9e",971,35.25],["stagnation",970,34.99],["grimpette",969,34.83],["pente",968,34.82],["effondrement",967,34.79],["\u00e9clatement",966,34.43],["d\u00e9c\u00e9l\u00e9ration",965,34.3],["aggravation",964,34.17],["accentuer",963,34.08],["augmentation",962,34.05],["\u00e9mergence",961,33.97],["progression",960,33.93]]
```

## POST /score

This endpoint returns the score of the word given in the body.

```powershell
(Invoke-WebRequest -UseBasicParsing -Uri "https://cemantix.certitudes.org/score" `
∙ -Method "POST" `
∙ -Headers @{
∙   "Referer"="https://cemantix.certitudes.org/"
∙ } `
∙ -Body "word=humain").Content
```

- @param {word} - word
- @returns {json} - {"n":number,"p":number,"s":number,"v":number}
- @return-params {n} - number of the word day
- @return-params {v} - number of people who have already found it
- @return-params {p} - percentage of similarity out of ‰
- @return-params {s} - score

```json
{"n":1071,"p":1000,"s":1,"v":10531}
```