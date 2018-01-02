class Hanjie:
    @staticmethod
    def parsi_vihjeet(vihjestr):
        return [[int(a) for a in vihjerivi.strip().split()] for vihjerivi in vihjestr.strip().splitlines()]

    @staticmethod
    def partitioi_välit(vihje, leveys):
        """
        Etsii kaikki mahdolliset tyhjien välien pituudet annetuilla vihjeillä ja kokonaisleveydellä.
        Välejä on yksi enemmän kuin vihjeitä (yksi ennen jokaista vihjenumeroa, ja yksi viimeisen jälkeen).
        Vihjeiden välissä pitää olla vähintään 1 väli, mutta reunoilla voi olla 0 (eli värillinen ruutu kiinni reunassa)
        Esim. 5 ruudun mittainen rivi, vihjeellä 2 1: mahdolliset välit ovat
        [0 2 0] (eli XX__X)
        [1 1 0] (eli _XX_X)
        [0 1 1] (eli XX_X_)
        :param vihje: vihje listana numeroita
        :param leveys: rivin (tai sarakkeen) leveys (tai pituus)
        :return: Mahdolliset välit listana listoja
        """
        def jaa_tyhjiä(välit, jäljellä, nyk_kohta=0):
            if jäljellä == 0:
                return [välit]
            vastaukset = []
            for n in range(nyk_kohta, len(välit)):
                uus_välit = [a for a in välit]
                uus_välit[n] += 1
                vastaukset = vastaukset + jaa_tyhjiä(uus_välit, jäljellä - 1, n)
            return vastaukset

        tyhjiä_yhteensä = leveys - sum(vihje)
        välejä = len(vihje) + 1
        minvälit = [0] + (välejä - 2) * [1] + [0]
        tyhjiä_jäljellä = tyhjiä_yhteensä - (välejä - 2)

        return jaa_tyhjiä(minvälit, tyhjiä_jäljellä)

    @staticmethod
    def tayta(vihje, välit):
        """
        Palauttaa ruutujen värit (1 ja 0) annetuilla vihjeillä ja väleillä
        :param vihje:
        :param välit:
        :return:
        """
        värit = []
        for i in range(len(välit) - 1):
            värit += välit[i] * [0]
            värit += vihje[i] * [1]
        värit += välit[-1] * [0]
        return värit

    @staticmethod
    def aseta_varmat(ruudut, vihje, muisti, välivaihtoehdot):
        """
        Asettaa varmat ruudut paikalleen annettuun riviin tai sarakkeeseen.

        Funktio kokeillee annettuja vaihtoehtoja sen hetkiseen ruudukkoon. Pitää kirjaa ruuduista, jotka
        ovat kaikissa ruudukkoon sopivissa vaihtoehdoissa saman värisiä, ja lopuksi asetetaan löydetyt varmat
        värit niille kuuluville paikoille.
        :param ruudut:
        :param vihje:
        :param muisti:
        :param välivaihtoehdot:
        :return: Tieto siitä, muuttuiko jonkun ruudun tila
        """

        # Tarkistetaan muistista, ollaanko samassa tilanteessa kuin viimeksi. Jos kyllä, niin ei ole järkeä tehdä mitään
        if [r.varmaväri for r in ruudut] == muisti:
            return False

        muutos = False
        on_varma = len(ruudut) * [True]  # Tieto, onko varmat-muuttujan tieto varma tieto
        varmat = None  # Lista numeroita (1 tai 0), jotka saattavat olla varmoja oikeita värejä

        for v in range(len(välivaihtoehdot) - 1, -1, -1):
            vaihtoehto = välivaihtoehdot[v]
            värit = Hanjie.tayta(vihje, vaihtoehto)

            # Onko mahdollinen konfiguraatio
            for i in range(len(ruudut)):
                if ruudut[i].varmaväri is not None and ruudut[i].varmaväri != värit[i]:
                    # Jos ei, niin vaihtoehto voidaan poistaa käytöstä.
                    välivaihtoehdot[v], välivaihtoehdot[-1] = välivaihtoehdot[-1], välivaihtoehdot[v]
                    välivaihtoehdot.pop()
                    break
            else:
                # Konfiguraatio on mahdollinen -> Tarkistetaan varmat paikat
                if varmat is None:
                    varmat = värit
                for i in range(len(ruudut)):
                    # Jos varmat (eli ensimmäinen löydetty mahdollinen konfiguraatio) sisältää eri arvon kuin
                    # juuri löydetty konfiguraatio, merkitään ko kohta ei varmaksi.
                    if värit[i] != varmat[i]:
                        on_varma[i] = False

            # Jos mikään ruutu ei ole enää varma, ei ole järkeä käydä loppuja vaihtoehtoja edes läpi
            if True not in on_varma:
                break
        else:
            # Edellinen silmukka päättyi siihen, että varmoja ruutuja on -> Asetetaan varmat kohdat paikoilleen
            for i in range(len(ruudut)):
                if on_varma[i]:
                    if ruudut[i].varmaväri is None:
                        # Pidetään kirjaa, onko tapahtunut jokin muutos funktion tällä ajolla
                        muutos = True
                    ruudut[i].varmaväri = varmat[i]

        # Päivitetään muisti (alkioittain, jotta referenssi pysyy oikeaan objektiin)
        for i in range(len(ruudut)):
            muisti[i] = ruudut[i].varmaväri

        return muutos

    class Ruutu:
        """
        Ruutu. Sisältää värin (musta, valkoinen tai ei tiedossa)
        """
        def __init__(self):
            self.varmaväri = None

        def __str__(self):
            return "? " if self.varmaväri is None else "  " if self.varmaväri == 0 else "X "

    def __init__(self, ylavihjeet, vasenvihjeet):
        self.vasenvihjeet = vasenvihjeet
        self.ylavihjeet = ylavihjeet
        self.ruudut = []
        self.vaihtoehdot_rivit = []
        self.vaihtoehdot_sarakkeet = []
        for y in range(len(vasenvihjeet)):
            self.ruudut.append([Hanjie.Ruutu() for _ in range(len(ylavihjeet))])

        self.muisti_rivit = []
        self.muisti_sarakkeet = []

    def alusta(self):
        for y in range(len(self.vasenvihjeet)):
            pituus = len(self.ylavihjeet)
            vihje = self.vasenvihjeet[y]
            self.vaihtoehdot_rivit.append(Hanjie.partitioi_välit(vihje, pituus))

        for x in range(len(self.ylavihjeet)):
            pituus = len(self.vasenvihjeet)
            vihje = self.ylavihjeet[x]
            self.vaihtoehdot_sarakkeet.append(Hanjie.partitioi_välit(vihje, pituus))

        for y in range(len(self.vasenvihjeet)):
            self.muisti_rivit.append(len(self.ylavihjeet) * [0])
        for x in range(len(self.ylavihjeet)):
            self.muisti_sarakkeet.append(len(self.vasenvihjeet) * [0])

    def __str__(self):
        return "\n".join(["".join([str(ruutu) for ruutu in ruuturivi]) for ruuturivi in self.ruudut])

    def rivi(self, y):
        return self.ruudut[y]

    def sarake(self, x):
        return [self.ruudut[y][x] for y in range(len(self.ruudut))]

    def kaikki_varmat(self):
        muutokset = []
        for y in range(len(self.vasenvihjeet)):
            muutokset.append(self.varmat_rivi(y))
        for x in range(len(self.ylavihjeet)):
            muutokset.append(self.varmat_sarake(x))
        return True in muutokset

    def kyssäriruudut(self):
        määrä = 0
        for rivi in self.ruudut:
            for ruutu in rivi:
                if ruutu.varmaväri is None:
                    määrä += 1
        return määrä

    def ratkaise(self):
        print("Lasketaan vaihtoehtoja...")
        self.alusta()

        print("Ratkaistaan...")
        muutos = True
        while muutos:
            muutos = self.kaikki_varmat()
            print("{:.0f}% ratkaistu".format(100 * (1 - self.kyssäriruudut() / len(self.vasenvihjeet) / len(self.ylavihjeet))))

    def varmat_rivi(self, y):
        rivi = self.rivi(y)
        vihje = self.vasenvihjeet[y]
        muisti = self.muisti_rivit[y]
        vaihtoehdot = self.vaihtoehdot_rivit[y]
        return self.aseta_varmat(rivi, vihje, muisti, vaihtoehdot)

    def varmat_sarake(self, x):
        sarake = self.sarake(x)
        vihje = self.ylavihjeet[x]
        muisti = self.muisti_sarakkeet[x]
        vaihtoehdot = self.vaihtoehdot_sarakkeet[x]
        return self.aseta_varmat(sarake, vihje, muisti, vaihtoehdot)

ylävihje = """
6 1
1 5 1
2 6
1 4
1 2 2 3
1 1 1 2 3
1 2 2 2 2 1
1 1 3 3 2 2 2
1 1 11 2 3
1 1 3 9 2 2
1 2 2 1 1 4 3 2
1 1 2 1 3 2 1
1 1 2 2 3 3 1
2 1 2 3 5
1 1 1 1 3 4
1 1 1 1 3 3
1 1 1 4 5
1 1 1 6 3 2
5 1 2 2 5 1
7 3 2 1 3 1
10 2 2 3 2
8 1 1 3 1
9 2 4
7 3 1 4 1
5 3 1 4 2 1
1 3 2 2 2 2
1 1 2 3 3 3
2 1 2 2 2 4
1 1 2 4 2 4
1 1 2 6 2 2
"""

vasenvihje = """
3 5
4 7 3
15
7 7
20
8
1 5 2
1 1 3 2
1 2 1 1 2 2
3 1 1 2 1 2
2 1 2 1 2 1
2 3 1 1
7 2
5 2 1
2 5
12
14 1
7 2 3 2
7 2 3 1 2
3 2 3 4
2 3 2 6
2 3 1
1 2 3 3
3 2 2 3 4
3 1 3 1 7 2 1
4 10 7 2
8 9 2 2 2
6 1 5 1 3
3 4 5 1 5
2 7 6 6
"""

h = Hanjie(Hanjie.parsi_vihjeet(ylävihje), Hanjie.parsi_vihjeet(vasenvihje))
h.ratkaise()

print(h)