from experta import *
import schema

# 18.26

class Utisak(Fact):
    ime = Field(str)
    destinacija = Field(str)
    ocena = Field(schema.Or("POZITIVNA", "NEGATIVNA"))

    uracunat_utisak = Field(schema.Or(True, False), default= False)

class Zbirni_utisak(Fact):
    destinacija = Field(str)
    pozitivni = Field(int, default = 0)
    negativni = Field(int, default = 0)
    ukupno = Field(lambda x: isinstance(x, float), default = 0.0)

    vec_ocenjena = Field(schema.Or(True, False), default= False)
    za_brisanje = Field(schema.Or(True, False), default= False)
    

class Ponuda(Fact):
    destinacija = Field(str)
    br_dana = Field(int)
    cena = Field(float)

    formirana_cena = Field(schema.Or(True, False), default= False)
    izlistana = Field(schema.Or(True, False), default= False)


class sistem(KnowledgeEngine):
    @DefFacts()
    def init_cinjenice(self):
        yield Utisak(ime = "luka", destinacija = "atina", ocena = "POZITIVNA")
        yield Utisak(ime = "jelisej", destinacija = "atina", ocena = "NEGATIVNA")
        yield Utisak(ime = "atanas", destinacija = "atina", ocena = "NEGATIVNA")

        yield Utisak(ime = "luka", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "jelisej", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas", destinacija = "bg", ocena = "NEGATIVNA")
        yield Utisak(ime = "atanas4", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas5", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas6", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas7", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas8", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas9", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas10", destinacija = "bg", ocena = "POZITIVNA")
        yield Utisak(ime = "atanas11", destinacija = "bg", ocena = "NEGATIVNA")

        yield Utisak(ime = "luka", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "jelisej", destinacija = "ns", ocena = "NEGATIVNA")
        yield Utisak(ime = "atanas", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan2", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan3", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan4", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan5", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan6", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan7", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan8", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan9", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan10", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan11", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan12", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan13", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan14", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan15", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan16", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan17", destinacija = "ns", ocena = "POZITIVNA")
        yield Utisak(ime = "ivan18", destinacija = "ns", ocena = "POZITIVNA")

        yield Zbirni_utisak(destinacija = "atina")
        yield Zbirni_utisak(destinacija = "bg")
        yield Zbirni_utisak(destinacija = "ns")

        yield Ponuda(destinacija = "atina", br_dana = 15, cena = 100.0)
        yield Ponuda(destinacija = "bg", br_dana = 15, cena = 100.0)
        yield Ponuda(destinacija = "ns", br_dana = 15, cena = 100.0)

        yield Fact("popuni-zbirne-utiske")
        

    @Rule(
        Fact("popuni-zbirne-utiske"),
        AS.f << Zbirni_utisak(destinacija = MATCH.dest, pozitivni = MATCH.poz),
        AS.u << Utisak(destinacija = MATCH.dest, ocena = MATCH.o, uracunat_utisak = False), 
        TEST(lambda o: o == 'POZITIVNA')
    )
    def dodaj_pozitivnu(self, f, poz, u):
        self.modify(f, pozitivni = poz + 1)
        self.modify(u, uracunat_utisak = True)

    @Rule(
        Fact("popuni-zbirne-utiske"),
        AS.f << Zbirni_utisak(destinacija = MATCH.dest, negativni = MATCH.neg),
        AS.u << Utisak(destinacija = MATCH.dest, ocena = MATCH.o, uracunat_utisak = False), 
        TEST(lambda o: o == 'NEGATIVNA')
    )
    def dodaj_negativnu(self, f, neg, u):
        self.modify(f, negativni = neg + 1)
        self.modify(u, uracunat_utisak = True)
    
    @Rule(
        AS.f1 << Fact("popuni-zbirne-utiske"),
        salience = -10
    )
    def prelazak_na_fazu_ocene_destinacije(self, f1):
        self.retract(f1)
        self.declare(Fact("ocenjivanje-destinacija"))

    @Rule(
        Fact("ocenjivanje-destinacija"),
        AS.zu << Zbirni_utisak(negativni = MATCH.neg, pozitivni = MATCH.poz, vec_ocenjena = False)
    )        
    def ocenjivanje(self, zu, poz, neg):        
        self.modify(zu, ukupno = (poz - neg)/poz, vec_ocenjena = True )

    @Rule(
        AS.f1 << Fact("ocenjivanje-destinacija"),
        salience = -10
    )
    def prelazak_na_fazu_brisanja_destinacija(self, f1):
        self.retract(f1)
        self.declare(Fact("brisi-lose-destinacije"))

    @Rule(
        Fact("brisi-lose-destinacije"),
        AS.zu << Zbirni_utisak(ukupno = MATCH.u, za_brisanje = False),
        TEST(lambda u: u < -0.5)
    )        
    def brisanje(self, zu):        
        self.modify(zu, za_brisanje = True)

    @Rule(
        Fact("brisi-lose-destinacije"),
        AS.zu << Zbirni_utisak(destinacija = MATCH.dest, za_brisanje = True),
        AS.p << Ponuda(destinacija = MATCH.dest),
        salience = -1
    )
    def brisanje_svega(self, zu, p, dest):
        self.retract(zu)
        self.retract(p)
        self.declare(Fact(obrisi = dest))

    @Rule(
        Fact("brisi-lose-destinacije"),
        Fact(obrisi = MATCH.dest),
        AS.u << Utisak(destinacija = MATCH.dest)
    )
    def brisanje_svega_stvarno(self, u):
        self.retract(u)

    @Rule(
        AS.f1 << Fact("brisi-lose-destinacije"),
        salience = -10
    )
    def prelazak_na_fazu_formiranja_cena(self, f1):
        self.retract(f1)
        self.declare(Fact("formiranje-cena"))

    #     ukoliko je opšti utisak veći od 0.5, i pritom je broj pozitivnih utisaka veći od 15, cena se uvećava
    # za 20%
    #  ukoliko je opšti utisak veći od 0.5, a broj pozitivnih utisaka je najviše 15, cena se uvećava 10%
    #  ukoliko je opšti utisak veći od 0, a manji od 0.5, i pritom je broj pozitivnih utisaka veći od 10, cena
    # se uvećava 3%
    #  ukoliko je opšti utisak između -0.5 i 0, cena se umanjuje za 15%
    @Rule(
        Fact("formiranje-cena"),
        AS.p << Ponuda(destinacija = MATCH.dest, cena = MATCH.cena, formirana_cena = False),
        AS.zu << Zbirni_utisak(destinacija = MATCH.dest, ukupno = MATCH.utisak, pozitivni = MATCH.poz)
    )
    def formiranje_cena(self, p, cena, poz, utisak):
        if( utisak > 0.5):
            if(poz > 15):
                self.modify(p, cena = cena + cena*0.2, formirana_cena = True)
            else:
                self.modify(p, cena = cena + cena*0.1, formirana_cena = True)
        elif (utisak > 0):
            if(poz > 10):
                self.modify(p, cena = cena + cena*0.03, formirana_cena = True)
        else:
            self.modify(p, cena = cena - cena*0.15, formirana_cena = True)

    @Rule(
        AS.f1 << Fact("formiranje-cena"),
        salience = -10
    )
    def faza_listanja(self, f1):
        self.retract(f1)
        self.declare(Fact("listanje"))

    @Rule(
        Fact("listanje"),
        AS.p << Ponuda(destinacija = MATCH.dest, izlistana = False)
    )
    def listanje_dest(self, dest):
        print("Dobra destinacija za ovu sezonu: " + dest)

    @Rule(
        AS.f1 << Fact("listanje"),
        salience = -10
    )
    def faza_interakcije(self, f1):
        self.retract(f1)
        self.declare(Fact("interaktivna-faza"))

    @Rule(
        Fact("interaktivna-faza"),
        NOT(Fact(vise_info = W()))
    )
    def pitaj(self):
        print("da li zelite vise detalja o nekoj destinaciji? da/ne")
        odg = input()
        if(odg == "ne"):
            self.declare(Fact(kraj="dosta je"))
        else:
            print("o kojoj se destinaciji radi?")
            odg1 = input()
            self.declare(Fact(vise_info = odg1))

    @Rule(
        Fact("interaktivna-faza"), 
        AS.f1 << Fact(vise_info = MATCH.dest),
        Ponuda(destinacija = MATCH.dest, br_dana = MATCH.bd, cena = MATCH.c)
    )
    def vise_informacija(self, f1, dest, bd, c):
        print("Detalji o " + dest)
        print("broj dana: " + str(bd))
        print("Cena: " + str(c))
        self.retract(f1)


    @Rule(
        Fact(kraj=W()),
        AS.f1 << Fact("interaktivna-faza")
    )
    def pozdrav(self, f1):
        print("hvala na poseti")
        self.retract(f1)

engine = sistem()
engine.reset()
engine.run()
print(engine.facts)


# 19.38