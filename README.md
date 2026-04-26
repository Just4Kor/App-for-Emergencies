# App-for-Emergencies

## Įvadas

Šio kursinio darbo tikslas – sukurti objektinio programavimo principais paremtą programą, kuri leidžia vartotojams rasti skubios pagalbos paslaugų darbuotojus ir pateikti jiems užklausas.

Programa leidžia:
- registruotis kaip klientui arba darbuotojui;
- ieškoti darbuotojų pagal miestą ir specialybę;
- peržiūrėti darbuotojo informaciją, valandinį įkainį ir įvertinimą;
- klientui pateikti užklausą;
- darbuotojui priimti arba atmesti užklausą;
- saugoti duomenis tekstiniuose failuose.

---

## Kaip paleisti programą

Įdiegti reikalingas bibliotekas:

```bash
pip install flask flask-login
```

Jeigu `pip` neveikia:

```bash
py -m pip install flask flask-login
```

Paleisti programą:

```bash
py app.py
```

Naršyklėje atidaryti:

```text
http://127.0.0.1:5000
```

---

## Kaip naudotis programa

### Klientas

Klientas gali:
1. Užsiregistruoti kaip `Customer`.
2. Prisijungti prie sistemos.
3. Ieškoti darbuotojų pagal miestą ir specialybę.
4. Pasirinkti darbuotoją.
5. Pateikti užklausą su problemos pavadinimu, adresu ir aprašymu.
6. Matyti savo užklausas puslapyje `My Requests`.

### Darbuotojas

Darbuotojas gali:
1. Užsiregistruoti kaip `Worker`.
2. Prisijungti prie sistemos.
3. Matyti gautas užklausas `Worker Dashboard` puslapyje.
4. Priimti arba atmesti užklausas.

---

## Objektinio programavimo principai

## 6. Objektinio programavimo principai

Objektinis programavimas leidžia programą suskirstyti į atskirus objektus, kurie turi savo duomenis ir veiksmus. Mano projekte objektai naudojami klientams, darbuotojams, užklausoms, įvertinimams ir sistemos logikai aprašyti.

Projekte įgyvendinti visi 4 pagrindiniai OOP principai:

- paveldėjimas;
- abstrakcija;
- inkapsuliacija;
- polimorfizmas.

---

## 6.1 Paveldėjimas

Paveldėjimas leidžia vienai klasei perimti kitos klasės savybes ir metodus. Tai padeda sumažinti pasikartojantį kodą ir sukurti aiškią klasių hierarchiją.

Mano projekte bazinė klasė yra `Person`:

```python
class Person(ABC):
    def __init__(self, person_id, username, location=""):
        self.id = str(person_id)
        self.username = username
        self.location = location
```

Ši klasė saugo bendrus duomenis, kuriuos turi tiek klientas, tiek darbuotojas:
- `id`;
- `username`;
- `location`.

Iš `Person` klasės paveldi `User` klasė:

```python
class User(Person, UserMixin):
```

Ir `Worker` klasė:

```python
class Worker(Person, UserMixin):
```

Tai reiškia, kad `User` ir `Worker` automatiškai gauna bendras `Person` savybes. Klientui papildomai pridedamas `city`, o darbuotojui – `specialty`, `hourly_rate` ir `rating`.

Šis principas mano projekte svarbus todėl, kad klientas ir darbuotojas yra panašūs objektai: abu turi identifikatorių, vartotojo vardą ir vietą, tačiau jų paskirtis sistemoje skiriasi.

---

## 6.2 Abstrakcija

Abstrakcija leidžia aprašyti bendrą idėją, nesigilinant į visas detales. Ji padeda sukurti bendrą klasės šabloną, kurį kitos klasės turi įgyvendinti.

Mano projekte abstrakcija naudojama `Person` klasėje:

```python
from abc import ABC, abstractmethod
```

```python
class Person(ABC):
```

Ši klasė yra abstrakti, nes ji nėra skirta naudoti kaip konkretus žmogus sistemoje. Ji tik aprašo bendras savybes, kurias turi kiti objektai.

`Person` klasėje yra abstraktus metodas:

```python
@abstractmethod
def get_profile_summary(self):
    pass
```

Tai reiškia, kad kiekviena klasė, kuri paveldi `Person`, privalo turėti savo `get_profile_summary()` metodą.

Pavyzdžiui, `User` klasėje šis metodas grąžina kliento informaciją:

```python
def get_profile_summary(self):
    return f"Customer: {self.username}, City: {self.city}"
```

O `Worker` klasėje jis grąžina darbuotojo informaciją:

```python
def get_profile_summary(self):
    return (
        f"{self.username} - {self.specialty}, "
        f"{self.location}, {self.hourly_rate}€/h, "
        f"rating {self.rating}/5"
    )
```

Abstrakcija šiame projekte naudinga todėl, kad `Person` aprašo tik bendrą žmogaus struktūrą, o konkrečios klasės (`User` ir `Worker`) pačios nusprendžia, kaip pateikti savo informaciją.

---

## 6.3 Inkapsuliacija

Inkapsuliacija reiškia, kad objektas saugo savo duomenis ir pats kontroliuoja, kaip tie duomenys keičiami. Tai padeda išvengti neteisingų duomenų ir palaiko tvarkingą programos struktūrą.

Mano projekte inkapsuliacija matoma keliose vietose.

Pirmas pavyzdys yra `ServiceRequest` klasė. Užklausos statusas nekeičiamas bet kaip, o tam naudojami metodai:

```python
def accept(self):
    self.status = RequestStatus.ACCEPTED

def deny(self):
    self.status = RequestStatus.DENIED
```

Tai reiškia, kad užklausa pati turi elgseną, kuri leidžia ją priimti arba atmesti. Vietoje to, kad visoje programoje rankiniu būdu rašyčiau:

```python
request.status = "Accepted"
```

naudoju metodą:

```python
request.accept()
```

Tai yra aiškiau ir saugiau.

Antras pavyzdys yra `Rating` klasė:

```python
class Rating:
    def __init__(self):
        self.scores = []
```

Ji turi metodą `add_score()`, kuris patikrina, ar įvertinimas yra tinkamas:

```python
def add_score(self, score):
    score = float(score)

    if score < 0 or score > 5:
        raise ValueError("Rating must be between 0 and 5.")

    self.scores.append(score)
```

Tai apsaugo sistemą nuo neteisingų įvertinimų, pavyzdžiui `-1` arba `10`.

Inkapsuliacija mano projekte padeda užtikrinti, kad objektų duomenys būtų keičiami per metodus, o ne atsitiktinai bet kurioje programos vietoje.

---

## 6.4 Polimorfizmas

Polimorfizmas reiškia, kad tas pats metodas gali turėti skirtingą elgseną skirtingose klasėse.

Mano projekte polimorfizmas matomas per metodą:

```python
get_profile_summary()
```

Šis metodas yra aprašytas abstrakčioje `Person` klasėje, bet skirtingai įgyvendintas `User` ir `Worker` klasėse.

`User` klasėje:

```python
def get_profile_summary(self):
    return f"Customer: {self.username}, City: {self.city}"
```

Šis metodas pateikia kliento informaciją.

`Worker` klasėje:

```python
def get_profile_summary(self):
    return (
        f"{self.username} - {self.specialty}, "
        f"{self.location}, {self.hourly_rate}€/h, "
        f"rating {self.rating}/5"
    )
```

Šis metodas pateikia darbuotojo informaciją.

Tai reiškia, kad galima naudoti tą patį metodą abiem objektams, bet rezultatas bus skirtingas pagal objekto tipą.

Pavyzdžiui:

```python
people = [customer, worker]

for person in people:
    print(person.get_profile_summary())
```

Vienas objektas grąžins kliento aprašymą, o kitas – darbuotojo aprašymą. Tai yra polimorfizmo pavyzdys.

Polimorfizmas mano projekte naudingas todėl, kad leidžia dirbti su skirtingais objektais per bendrą metodą, bet išlaikyti skirtingą jų elgseną.

---

## Kompozicija ir agregacija

---

## Kompozicija

Kompozicija reiškia stiprų ryšį tarp objektų, kai vienas objektas „turi“ kitą objektą kaip savo dalį.

Svarbiausia savybė:
jei pagrindinis objektas sunaikinamas, jo viduje esantys objektai taip pat praranda prasmę.

---

### Pavyzdys

Kompozicija naudojama `Worker` klasėje kartu su `Rating` klase:

```python
from models.rating import Rating

class Worker(Person, UserMixin):
    def __init__(...):
        ...
        self.rating_object = Rating()
```

Čia:
- `Worker` turi `Rating` objektą;
- `Rating` egzistuoja tik tam, kad aptarnautų konkretų darbuotoją.

Toliau naudojamas metodas:

```python
self.rating_object.add_score(rating)
self.rating = str(round(self.rating_object.get_average(), 2))
```

Tai reiškia:
- darbuotojo įvertinimas nėra tiesiog skaičius;
- jis apskaičiuojamas naudojant atskirą objektą (`Rating`);
- `Rating` objektas sukuriamas **viduje** `Worker` klasės;
- jis nėra naudojamas savarankiškai;
- jis priklauso tik vienam darbuotojui.

---

## Agregacija

Agregacija yra silpnesnis ryšys nei kompozicija.

Svarbiausia savybė - objektai gali egzistuoti nepriklausomai vienas nuo kito.

---

### Pavyzdys nr.1

Agregacija naudojama `Platform` klasėje:

```python
class Platform:
    def __init__(self):
        self.search_engine = SearchEngine()
```

Ir:

```python
def get_workers(self, location="", specialty=""):
    workers = read_workers()
    filtered_workers = self.search_engine.filter_workers(
        workers,
        location,
        specialty,
    )
    return self.search_engine.sort_workers(filtered_workers)
```

---

`Platform` gauna darbuotojus iš failų (`read_workers()`), perduoda juos `SearchEngine`, grąžina rezultatą.
`Platform` **nesukuria darbuotojų rankiniu būdu**, ji tik dirba su jau egzistuojančiais objektais.

---

### Pavyzdys nr. 2

```python
def get_customer_requests(self, customer_id):
    return [
        request for request in self.get_requests()
        if request.customer_id == str(customer_id)
    ]
```

`Platform` dirba su `ServiceRequest` objektais,cbet jų „neturi“ kaip savo dalies,cjie egzistuoja nepriklausomai (saugomi failuose).
`Platform` tik **naudoja** kitus objektus,cji jų „nevaldo“ pilnai, objektai egzistuoja ir be `Platform`.

---

## Failų skaitymas ir rašymas

Failų skaitymas ir rašymas įgyvendintas faile:

```text
services/worker_file_service.py
```

Naudojamos funkcijos:

```python
read_workers()
save_workers()
read_customers()
save_customers()
read_requests()
save_requests()
```

Programa:
- skaito darbuotojus iš `workers.txt`;
- skaito klientus iš `customers.txt`;
- skaito užklausas iš `requests.txt`;
- įrašo naujus darbuotojus;
- įrašo naujus klientus;
- įrašo naujas ir atnaujintas užklausas.

---

## Paieška ir filtravimas
Mano programoje galima filtruoti darbuotojus pagal miestą ir specialybę. Pati programa automatiškai pirmiausia rodo darbuotojus su geriuaisais įvertinimais.

Darbuotojų paieška įgyvendinta faile:

```text
services/search.py
```

Klasė:

```python
class SearchEngine:
```

Ji turi metodus:

```python
filter_workers()
sort_workers()
```

`filter_workers()` filtruoja darbuotojus pagal miestą ir specialybę.

`sort_workers()` rūšiuoja darbuotojus pagal įvertinimą.


---

## Web modeliai

Aplanke:

```text
web_models/
```

yra klasės:
- `AccountView`;
- `CustomerView`;
- `WorkerView`.

Jos naudojamos tam, kad į HTML šablonus būtų perduodami tik reikalingi duomenys.

Pavyzdys:

```python
worker_views = [
    WorkerView(worker) for worker in workers
]
```

## Flask dalis

Failas:

```text
app.py
```

yra pagrindinis programos paleidimo failas.

Jis atsakingas už:
- pagrindinį puslapį;
- registraciją;
- prisijungimą;
- atsijungimą;
- darbuotojo peržiūrą;
- užklausos sukūrimą;
- kliento užklausų puslapį;
- darbuotojo valdymo puslapį;
- profilio redagavimą.

Svarbiausi maršrutai:

```python
@app.route("/")
```

```python
@app.route("/register", methods=["GET", "POST"])
```

```python
@app.route("/login", methods=["GET", "POST"])
```

```python
@app.route("/worker/<worker_id>", methods=["GET", "POST"])
```

```python
@app.route("/my_requests")
```

```python
@app.route("/worker_dashboard")
```

```python
@app.route("/update_request/<request_id>", methods=["POST"])
```

```python
@app.route("/profile", methods=["GET", "POST"])
```

---

## 14. Rezultatai

- Sukurta veikianti skubios pagalbos paslaugų paieškos sistema.
- Įgyvendinti visi 4 objektinio programavimo principai.
- Pritaikytas Factory Method dizaino šablonas.
- Duomenys saugomi tekstiniuose failuose.
- Sukurta klientų ir darbuotojų registracija.
- Darbuotojai gali priimti arba atmesti užklausas.
- Sukurtas vienetinių testų failas.

---

## 15. Išvados

Šio kursinio darbo metu buvo sukurta objektinio programavimo principais paremta sistema, leidžianti klientams ieškoti darbuotojų ir siųsti jiems užklausas.

Darbo metu buvo pritaikyti:
- paveldėjimas;
- abstrakcija;
- inkapsuliacija;
- polimorfizmas;
- Factory Method dizaino šablonas;
- failų skaitymas ir rašymas;
- vienetiniai testai.

Programa gali būti toliau plečiama. Ateityje būtų galima:
- pridėti tikrą darbuotojų vertinimo sistemą;
- naudoti duomenų bazę vietoje TXT failų;
- pridėti administratoriaus rolę;
- pridėti užklausų ištrynimą;
- pridėti daugiau miestų ir specialybių;
- pridėti slaptažodžių hashinimą saugumui;
- pridėti žemėlapį su real-time tracking.

---
