# App-for-Emergencies

## 1. Įvadas

Šio kursinio darbo tikslas – sukurti objektinio programavimo principais paremtą programą, kuri leidžia vartotojams rasti skubios pagalbos paslaugų darbuotojus ir pateikti jiems užklausas.

Programa leidžia:
- registruotis kaip klientui arba darbuotojui;
- ieškoti darbuotojų pagal miestą ir specialybę;
- peržiūrėti darbuotojo informaciją, valandinį įkainį ir įvertinimą;
- klientui pateikti užklausą;
- darbuotojui priimti arba atmesti užklausą;
- saugoti duomenis tekstiniuose failuose.

---

## 2. Kaip paleisti programą

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

## 3. Kaip naudotis programa

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

## 5. Objektinio programavimo principai

Projekte įgyvendinti visi 4 OOP principai:
- paveldėjimas;
- abstrakcija;
- enkapsuliacija;
- polimorfizmas.

---

## 5.1 Paveldėjimas

Paveldėjimas leidžia vienai klasei perimti kitos klasės savybes ir metodus.

Projekte naudojama bazinė klasė:

```python
class Person(ABC):
```

Iš jos paveldi:

```python
class User(Person, UserMixin):
```

ir:

```python
class Worker(Person, UserMixin):
```

Tai reiškia, kad tiek klientas, tiek darbuotojas turi bendras savybes:
- `id`;
- `username`;
- `location`.

---

## 5.2 Abstrakcija

Abstrakcija naudojama `Person` klasėje.

Faile `models/person.py` naudojama abstrakti klasė:

```python
class Person(ABC):
```

Joje yra abstraktus metodas:

```python
@abstractmethod
def get_profile_summary(self):
    pass
```

Šis metodas privalo būti įgyvendintas klasėse, kurios paveldi `Person`.

---

## 5.3 Enkapsuliacija

Enkapsuliacija reiškia, kad duomenys ir metodai laikomi klasės viduje.

Pavyzdys iš `ServiceRequest` klasės:

```python
def accept(self):
    self.status = RequestStatus.ACCEPTED

def deny(self):
    self.status = RequestStatus.DENIED
```

Užklausos statusas keičiamas per klasės metodus.

Taip pat `Rating` klasėje tikrinama, kad įvertinimas būtų tinkamas:

```python
if score < 0 or score > 5:
    raise ValueError("Rating must be between 0 and 5.")
```

---

## 5.4 Polimorfizmas

Polimorfizmas reiškia, kad tas pats metodas skirtingose klasėse gali veikti skirtingai.

Projekte metodas:

```python
get_profile_summary()
```

naudojamas tiek `User`, tiek `Worker` klasėse.

`User` klasėje:

```python
def get_profile_summary(self):
    return f"Customer: {self.username}, City: {self.city}"
```

`Worker` klasėje:

```python
def get_profile_summary(self):
    return (
        f"{self.username} - {self.specialty}, "
        f"{self.location}, {self.hourly_rate}€/h, "
        f"rating {self.rating}/5"
    )
```

---

## 6. Dizaino šablonas

Projekte naudojamas **Factory Method** dizaino šablonas.

Jis įgyvendintas faile:

```text
factory/account_factory.py
```

Klasė:

```python
class AccountFactory:
```

Ji turi metodus:

```python
create_customer()
create_worker()
```

Registracijos metu gali būti sukuriami du skirtingi objektų tipai:
- klientas;
- darbuotojas.

Todėl objektų kūrimas perkeltas į `AccountFactory`, o `app.py` tik iškviečia reikiamą metodą.

Kliento kūrimo pavyzdys:

```python
customer = AccountFactory.create_customer(
    user_id=get_next_customer_id(),
    username=username,
    password=password,
    city=request.form["city"],
)
```

Darbuotojo kūrimo pavyzdys:

```python
worker = AccountFactory.create_worker(
    worker_id=get_next_worker_id(),
    username=username,
    password=password,
    specialty=request.form["specialty"],
    location=request.form["location"],
    hourly_rate=request.form["hourly_rate"],
)
```

---

## 7. Kompozicija ir agregacija

### Kompozicija

Kompozicija matoma `Worker` klasėje.

Darbuotojas turi savo `Rating` objektą:

```python
self.rating_object = Rating()
```

Tai reiškia, kad `Worker` objektas naudoja `Rating` objektą savo įvertinimui valdyti.

### Agregacija

Agregacija matoma `Platform` klasėje.

Faile:

```text
services/platform.py
```

`Platform` klasė gauna darbuotojus, klientus ir užklausas iš failų.

Pavyzdžiai:

```python
get_workers()
get_customers()
get_requests()
get_customer_requests()
get_worker_requests()
```

---

## 8. Failų skaitymas ir rašymas

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

## 9. Paieška ir filtravimas

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

## 10. Platformos logika

Pagrindinė sistemos logika yra faile:

```text
services/platform.py
```

`Platform` klasė sujungia:
- failų servisą;
- paiešką;
- darbuotojų gavimą;
- klientų užklausų gavimą;
- darbuotojų užklausų gavimą.

Metodas:

```python
def get_workers(self, location="", specialty=""):
```

Šis metodas:
1. nuskaito darbuotojus iš failo;
2. pritaiko filtravimą;
3. surūšiuoja darbuotojus;
4. grąžina rezultatą į `app.py`.

---

## 11. Web modeliai

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

## 12. Flask dalis

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
- pagerinti vartotojo sąsają;
- pridėti slaptažodžių hashinimą saugumui.
- pridėti žemėlapį, real-time tracking

---
