from experta import * 
import schema

# 17.17

class Kompanija(Fact):
    idKompanija = Field(lambda x: isinstance(x, int) and x > 0)
    naziv = Field(str)
    oblast = Field(str)
    bilans = Field(float)
    rizikPoslovanja = Field(float, default = 1.0)
    
    provera_urednosti = Field(schema.Or("DA", "NE"), default = "DA")
    pozitivan_bilans = Field(schema.Or("DA", "NE"), default = "DA")
    bilans_rizik_uracunat = Field(schema.Or("DA", "NE"), default = "NE")
    smanjen_rizik_zbog_urednosti = Field(schema.Or("DA", "NE"), default = "NE")
    smanjen_it_rizik = Field(schema.Or("DA", "NE"), default = "NE")
    provera_bilansa = Field(schema.Or("DA", "NE"), default = "NE")

    provera_da_li_je_najsigurnija = Field(schema.Or("DA", "NE"), default = "DA")
    provera_sigurnosti = Field(schema.Or("DA", "NE"), default = "NE")

class Transakcija(Fact):
    idTransakcija = Field(lambda x: isinstance(x, int) and x > 0)
    idKompanija = Field(lambda x: isinstance(x, int) and x > 0)
    iznos = Field(float)
    status = Field(schema.Or("PLACENA", "NEPLACENA"))
    brojDanaKasnjenja = Field(lambda x: isinstance(x, int) and x >= 0, default = 0)

    provera_transakcija_neplacena_kasni = Field(schema.Or("DA", "NE"), default = "NE")
    provera_transakcija_placena_kasni = Field(schema.Or("DA", "NE"), default = "NE")
    provera_uredno_placanje = Field(schema.Or("DA", "NE"), default = "NE")

class sistem(KnowledgeEngine):
    @DefFacts()
    def inicijalizacija(self):
        yield Fact("pocetna-procena")
        # za prvo pravilo
        yield Kompanija(idKompanija = 1, naziv = "KOMTREJD", oblast = "IT", bilans = 40000000.0)
        yield Transakcija(idTransakcija = 1, idKompanija = 1, iznos = 300.0, status = "NEPLACENA", brojDanaKasnjenja = 5)
        # za drugo pravilo
        yield Kompanija(idKompanija = 2, naziv = "Henkel", oblast = "IT", bilans = 800.0)
        yield Transakcija(idTransakcija = 2, idKompanija = 2, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 0)
        yield Transakcija(idTransakcija = 2, idKompanija = 2, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 0)
        #za trece pravilo
        yield Kompanija(idKompanija = 3, naziv = "Yuhor", oblast = "IT", bilans = 500.0)
        yield Transakcija(idTransakcija = 3, idKompanija = 3, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 0)
        yield Transakcija(idTransakcija = 4, idKompanija = 3, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 6)
        yield Transakcija(idTransakcija = 5, idKompanija = 3, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 0)
        yield Transakcija(idTransakcija = 6, idKompanija = 3, iznos = 140.0, status = "PLACENA", brojDanaKasnjenja = 0)

    # За сваку трансакцију која је неплаћена и постоји кашњење ризик пословања компаније
    # увећава се за 0.2;
    @Rule(
        Fact("pocetna-procena"),
        AS.t << Transakcija(idKompanija = MATCH.kompanija, status = L("NEPLACENA"), brojDanaKasnjenja = MATCH.kasnjenje, provera_transakcija_neplacena_kasni = "NE"),
        TEST(lambda kasnjenje: kasnjenje > 0),
        AS.k << Kompanija(idKompanija = MATCH.kompanija, rizikPoslovanja = MATCH.rizik)
    )
    def neplacena_transakcija(self, k, t, rizik):
        self.modify(t, provera_transakcija_neplacena_kasni = "DA" )
        self.modify(k, rizikPoslovanja = rizik + 0.2)
    
    # За сваку трансакцију која је плаћена и постоји кашњење веће од 5 дана, ризик пословања 
    # компаније увећава се за 0.1;
    @Rule(
        Fact("pocetna-procena"),
        AS.t << Transakcija(idKompanija = MATCH.kompanija, status = L("PLACENA"), brojDanaKasnjenja = MATCH.kasnjenje, provera_transakcija_placena_kasni = "NE"),
        TEST(lambda kasnjenje: kasnjenje > 5),
        AS.k << Kompanija(idKompanija = MATCH.kompanija, rizikPoslovanja = MATCH.rizik)       
    )
    def placena_kasni(self, k, t, rizik):
        self.modify(t, provera_transakcija_placena_kasni = "DA" )
        self.modify(k, rizikPoslovanja = rizik + 0.1)

    # Компанија чије су све трансакције плаћене без кашњења има умањење ризика за 0.75;
    # uredno_placanje -> proverava da li je transakcija placena i da li nema kasnjenja (setuje provera_uredno_placanje na DA)
    # uredno_placanje2 -> proverava da li kompanija ima transakcije koje nisu uredno placene (setuje provera_urednosti u NE ako naidje na provera_uredno_placanje == NE)
    # uredno_placanje3 -> proverava da li su sve transakcije uredne (smanjuje rizik i setuje smanjen_rizik_zbog_urednosti na DA)
    @Rule(
    Fact("pocetna-procena"),
    #AS.k << Kompanija(idKompanija = MATCH.kompanija, rizikPoslovanja = MATCH.rizik), 
    AS.t << Transakcija(idKompanija = MATCH.kompanija, status = L("PLACENA"), brojDanaKasnjenja = MATCH.kasnjenje, provera_uredno_placanje = "NE"),
    TEST(lambda kasnjenje: kasnjenje == 0) 
    )
    def uredno_placanje(self, t):
        self.modify(t, provera_uredno_placanje = "DA" )

    @Rule(
    Fact("pocetna-procena"),
    AS.k << Kompanija(idKompanija = MATCH.kompanija, rizikPoslovanja = MATCH.rizik, provera_urednosti = "DA"), 
    Transakcija(idKompanija = MATCH.kompanija, provera_uredno_placanje = L("NE")), 
    salience = -1 
    )
    def uredno_placanje2(self, k, rizik):
        self.modify(k, provera_urednosti = "NE")

    @Rule(
        Fact("pocetna-procena"),
        AS.k << Kompanija(rizikPoslovanja = MATCH.rizik, provera_urednosti = "DA", smanjen_rizik_zbog_urednosti = "NE"),
        salience = -2
    )
    def uredno_placanje3(self, k, rizik):
        self.modify(k, rizikPoslovanja = rizik - 0.75, smanjen_rizik_zbog_urednosti = "DA")

    # Компаније које послују у ИТ сектору имају умањење ризика за 0.25.
    @Rule(
        Fact("pocetna-procena"),
        AS.k << Kompanija(rizikPoslovanja = MATCH.rizik, oblast = "IT", smanjen_it_rizik = "NE")
    )
    def smanji_rizik_na_it(self, k, rizik):
        self.modify(k, rizikPoslovanja = rizik - 0.25, smanjen_it_rizik = "DA")

    #pocetna-procena faza gotova

    # 18.52

    @Rule(
        AS.f1 << Fact("pocetna-procena"),
        salience = -10
    )
    def promena_sa_pocetne_na_bilans_fazu(self, f1):
        self.retract(f1)
        self.declare(Fact("bilans-faza"))
    
    # Након ове почетне процене гледа се биланс пословања фирме. Ако компанија има биланс већи од
    # милион ризик се смањује за 10%, а уколико је биланс негативан ризик се повећава за 20%.
    @Rule(
        Fact("bilans-faza"), 
        AS.k << Kompanija(bilans = MATCH.bilans, rizikPoslovanja = MATCH.rizik, provera_bilansa = "NE"),
        TEST(lambda bilans: bilans < 1000000)
    )
    def odredjivanje_bilansa(self, k):
        self.modify(k, pozitivan_bilans = "NE", provera_bilansa = "DA")

    @Rule(
        Fact("bilans-faza"), 
        AS.k << Kompanija(rizikPoslovanja = MATCH.rizik, pozitivan_bilans = "DA", bilans_rizik_uracunat = "NE"),
        salience = -1
    )
    def rizik_sa_pozitivnim_bilansom(self, k, rizik):
        self.modify(k, rizikPoslovanja = rizik - 0.1, bilans_rizik_uracunat = "DA")

    @Rule(
        Fact("bilans-faza"), 
        AS.k << Kompanija(rizikPoslovanja = MATCH.rizik, pozitivan_bilans = "NE", bilans_rizik_uracunat= "NE"),
        salience = -1
    )
    def rizik_sa_negativnim_bilansom(self, k, rizik):
        self.modify(k, rizikPoslovanja = rizik + 0.2, bilans_rizik_uracunat = "DA")


    # Тек пошто су све вредности ризика одређене, корисник уноси област пословања како би пронашао
    # најпогоднију компанију за робу коју продаје. Исписати идентификациони број, назив и ризик
    # пословања компаније са најмањим ризиком пословања за изабрану област. 
    @Rule(
        AS.f1 << Fact("bilans-faza"),
        salience = -10
    )
    def promena_sa_bilans_na_izbornu_fazu(self, f1):
        self.retract(f1)
        self.declare(Fact("izborna-faza"))
    
    @Rule(
        Fact("izborna-faza"),
        salience = 1
    )
    def unos_oblasti(self):
        oblast = input("unesi oblast poslovanja: ")
        self.declare(Fact(naziv_oblasti = oblast))

    @Rule(
        Fact("izborna-faza"), 
        Fact(naziv_oblasti = MATCH.naziv),
        AS.k1 << Kompanija(idKompanija = MATCH.id, oblast = MATCH.naziv, rizikPoslovanja = MATCH.rizik1, provera_da_li_je_najsigurnija = "DA"),
        AS.k2 << Kompanija(idKompanija = ~MATCH.id, oblast = MATCH.naziv, rizikPoslovanja = MATCH.rizik2, provera_da_li_je_najsigurnija = "DA" ),
        TEST( lambda rizik1, rizik2: rizik1 > rizik2)
    )
    def najsigurnija_kompanija(self, k1):
        self.modify(k1, provera_da_li_je_najsigurnija = "NE")

    @Rule(
        Fact("izborna-faza"), 
        Fact(naziv_oblasti = MATCH.naziv),
        AS.k << Kompanija(idKompanija = MATCH.id, naziv = MATCH.ime, rizikPoslovanja = MATCH.rizik, provera_da_li_je_najsigurnija = "DA")
    )
    def ispis_najsigurnije(self, id, ime, rizik, naziv):
        print("Najsigurnija je [id, naziv, rizik] za " + naziv + " oblast. ")
        print("[ " + str(id) + ", " + ime + ", " + str(rizik) + " ]")

engine = sistem()
engine.reset()
engine.run()
#print(engine.facts)

# 19.28
