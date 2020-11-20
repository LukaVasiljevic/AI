from experta import *
import schema

# 19.41

class Putnik(Fact):
    ime = Field(str)
    drzava = Field(str)
    godine = Field(lambda x: isinstance(x, int) and x >0)
    sadrzaj_torbe = Field(list)
    ima_dosije = Field(schema.Or("DA", "NE"))
    procena_rizika = Field(lambda x: 0 <= x <= 1 and isinstance(x, float), default = 0.5)

    vec_prosao_ima_dosije_proveru = Field(schema.Or("DA","NE"), default = "NE")
    vec_prosao_libija_iran_proveru = Field(schema.Or("DA","NE"), default = "NE")
    vec_prosao_da_li_je_iz_nigerije_proveru = Field(schema.Or("DA", "NE"), default = "NE")
    vec_prosao_proveru_godina = Field(schema.Or("DA", "NE"), default = "NE")
    najopasnija = Field(schema.Or("DA", "NE"), default = "DA")

class Aerodrom(KnowledgeEngine):

    @DefFacts()
    def unesi_putnike(self):
        yield Fact("inicijalna-provera")
        yield Putnik(ime = "Pera", drzava = "Kolumbija", godina = 19, sadrzaj_torbe = ["patike", "peskiri"], ima_dosije = "NE")
        yield Putnik(ime = "Luka", drzava = "Srbija", godina = 21, sadrzaj_torbe = ["kalas", "hekler", "utoke", "uzi"], ima_dosije = "NE")
        yield Putnik(ime = "Predrag", drzava = "Crna Gora", godina = 54, sadrzaj_torbe = ["tupi nozevi", "pena za brijanje", "lopta"], ima_dosije = "NE")
        yield Putnik(ime = "Novak", drzava = "Senegal", godina = 33, sadrzaj_torbe = ["avio karta", "sako", "marama"], ima_dosije = "DA")
        yield Putnik(ime = "Abdulah", drzava = "Iran", godina = 23, sadrzaj_torbe = ["noz", "cigare", "dinamit"], ima_dosije = "DA")
        yield Putnik(ime = "Akuwuwu", drzava = "Nigerija", godina = 30, sadrzaj_torbe = ["naocare za sunce", "narukvice hakuna matata", "torbice"], ima_dosije = "NE")
        yield Putnik(ime = "Zabawaba", drzava = "Nigerija", godina = 20, sadrzaj_torbe = ["pistolj", "naocare za sunce", "narukvice hakuna matata", "torbice"], ima_dosije = "DA")
        yield Putnik(ime = "Dzon", drzava = "Libija", godina = 43, sadrzaj_torbe = ["patike", "duks", "posteljina", "torbice"], ima_dosije = "NE")
        yield Putnik(ime = "Ingrid", drzava = "Svedska", godina = 14, sadrzaj_torbe = ["mali toma"], ima_dosije = "NE")

    #faza inicijalne provere

        # da li ima dosije
    @Rule(
        Fact("inicijalna-provera"),
        AS.osoba << Putnik(ima_dosije = 'DA', procena_rizika = MATCH.procena_rizika, vec_prosao_ima_dosije_proveru = "NE")
    )
    def da_li_ima_dosije(self, osoba, procena_rizika):
        self.modify(osoba, procena_rizika = procena_rizika + 0.2, vec_prosao_ima_dosije_proveru = "DA")

        #  Kreiratipravilo koje putnicimačija je država porekla Libija ili Iran povećavaprocenu rizika za 0.25
    @Rule(
        Fact("inicijalna-provera"),
        AS.osoba << Putnik(drzava= L("Libija") | L("Iran"), procena_rizika = MATCH.procena_rizika, vec_prosao_libija_iran_proveru= "NE")
    )
    def da_li_je_iz_libije_ili_irana(self, osoba, procena_rizika):
        self.modify(osoba, procena_rizika = procena_rizika + 0.25, vec_prosao_libija_iran_proveru = "DA")

        # Kreirati pravilo koje putnicima čija je država porekla nije Nigerija umanjuje procenu rizika za 0.1. Ovo pravilo se ne odnosi na putnike iz Libije ili Irana.
    @Rule(
        Fact("inicijalna-provera"),
        AS.osoba << Putnik(drzava = ~L("Nigerija") & ~L("Libija") & ~L("Iran"), procena_rizika = MATCH.procena_rizika, vec_prosao_da_li_je_iz_nigerije_proveru="NE")
    )
    def da_li_je_iz_nigerije(self, osoba, procena_rizika):
        self.modify(osoba, procena_rizika = procena_rizika - 0.1, vec_prosao_da_li_je_iz_nigerije_proveru = "DA")

        # Kreirati pravilo koje putnicima s brojem godina manjim od 18 ili većim od 50 umanjuje procenu rizika za 0.15
    @Rule(
        Fact("inicijalna-provera"),
        AS.osoba << Putnik(godina = MATCH.god, procena_rizika = MATCH.procena_rizika, vec_prosao_proveru_godina = "NE"),
        TEST(lambda god: god < 18 or god > 50)
    )
    def provera_godina(self, osoba, procena_rizika):
        self.modify(osoba, procena_rizika = procena_rizika - 0.15, vec_prosao_proveru_godina = "DA")

    
    # ISPIS FAZA
    # Nakon završene inicijalne provere svih putnika ispisati sve osobe čija je procena rizika veća od 0.5.
    @Rule(
        AS.cinjenica << Fact("inicijalna-provera"),
        salience = -10
    )
    def promena_faze_sa_inicijalne_na_ispis(self, cinjenica):
        print("PRELAZAK SA INICIJALNE FAZE NA FAZU ISPISA")
        self.retract(cinjenica)
        self.declare(Fact("ispis-faza"))

    @Rule(
        Fact("ispis-faza"),
        AS.osoba << Putnik(procena_rizika = MATCH.procena, ime = MATCH.ime),
        TEST(lambda procena: procena > 0.5)
    )
    def ispisi_problematicne(self, ime, procena):
        print("ovaj je problematican: " + ime + " procena rizika je: " + str(procena))


    # Potom putnici sa faktorom rizika preko 0.5 daju torbe na pregled skenerom.Ukoliko skener unutar torbe pronađe
    #  nož ili pištolj ispisuje se ime te osobe i odmahse uklanja iz spiska putnika.
    @Rule(
        Fact("ispis-faza"),
        AS.osoba << Putnik(ime = MATCH.ime, procena_rizika = MATCH.procena, sadrzaj_torbe = MATCH.sadrzaj),
        TEST(lambda procena: procena > 0.5),
        TEST(lambda sadrzaj: 1 if ("pistolj" in sadrzaj or "noz" in sadrzaj) else 0)
    )
    def ima_noz_ili_pistolj(self, osoba, ime):
        self.retract(osoba)
        print("ima noz ili pistolj: " + ime + ". Izbacen je")

    # poslednja faza- rucna provera
    @Rule(
        AS.cinjenica << Fact("ispis-faza"),
        salience = -10
    )
    def poslednja_faza(self, cinjenica):
        print("PRELAZAK SA ISPIS FAZE NA FAZU RUCNE PROVERE")
        self.retract(cinjenica)
        self.declare(Fact("rucna-provera"))
    
    #  Poslednji korak je provere je dodano analiza rizika koju sprovodi
    #  službenik nakon što svi putnici prođu kontrolu skenerom.Ekspertski 
    # sistem treba pronaći osobu sa najvećom procenom rizika i ispisati njegovo ime.
    @Rule(
        Fact("rucna-provera"),
        AS.osoba1 << Putnik(ime = MATCH.ime1, procena_rizika = MATCH.procena_rizika, najopasnija = "DA"),
        AS.osoba2 << Putnik(ime = ~MATCH.ime1, procena_rizika = MATCH.procena_rizika2, najopasnija = "DA"),
        TEST(lambda procena_rizika, procena_rizika2: procena_rizika < procena_rizika2)
    )
    def najopasniji_putnik(self, osoba1):
        self.modify(osoba1, najopasnija = "NE")

    @Rule(
        Fact("rucna-provera"),
        Putnik(ime = MATCH.ime, procena_rizika = MATCH.procena, najopasnija = "DA")
    )
    def ispisi_najopasnijeg(self, ime, procena):
        print("Najopasnija osoba na aerodromu je: " + ime + " sa procenom rizika: " + str(procena))
    

engine = Aerodrom()
engine.reset()
#print(engine.facts)
engine.run()
print("_____________________________")
print("ISPIS CINJENICA NA KRAJU:")
print(engine.facts)

# 21: 46