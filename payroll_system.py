import json
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

class IEmploye(ABC):
    @abstractmethod
    def Age(self):
        pass

    @abstractmethod
    def Anciennete(self):
        pass

    @abstractmethod
    def DateRetraite(self, ageRetraite):
        pass

class IR:
    _tranches = [0, 28001, 40001, 50001, 60001, 150001]
    _tauxIR = [0, 0.12, 0.24, 0.34, 0.38, 0.40]

    @staticmethod
    def getIR(salaire):
        for i in range(1, 6):
            if salaire < IR._tranches[i]:
                return IR._tauxIR[i - 1]
        return IR._tauxIR[5]

class Employe(IEmploye):
    cpt = 0
    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0):
        self._nom = nom
        self._dateNaissance = dateNaissance
        self._salaireBase = salaireBase
        Employe.cpt += 1
        self._mtle = Employe.cpt
        self._dateEmbauche = datetime.now() if dateEmbauche is None else dateEmbauche
        self.verifier_age_embauche()

    def verifier_age_embauche(self):
        age_embauche = (self._dateEmbauche - self._dateNaissance).days / 365
        if age_embauche < 16:
            raise ValueError("L'âge lors du recrutement doit être supérieur à 16 ans")

    @abstractmethod
    def SalaireAPayer(self):
        pass

    def Age(self):
        return int((datetime.now() - self._dateNaissance).days / 365)

    def Anciennete(self):
        return int((datetime.now() - self._dateEmbauche).days / 365)

    def DateRetraite(self, ageRetraite):
        return self._dateNaissance + timedelta(days=ageRetraite * 365)

    def __str__(self):
        return f"{self._mtle}-{self._nom}-{self._dateNaissance.strftime('%d/%m/%Y')}-{self._dateEmbauche.strftime('%d/%m/%Y')}-{self._salaireBase}"

    def __eq__(self, other):
        if not isinstance(other, Employe):
            return False
        return self._mtle == other._mtle

class Agent(Employe):
    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0, primeResponsabilite=0):
        super().__init__(nom, dateNaissance, dateEmbauche, salaireBase)
        self._primeResponsabilite = primeResponsabilite

    def SalaireAPayer(self):
        return (self._salaireBase + self._primeResponsabilite) * (1 - IR.getIR(self._salaireBase * 12))

class Formateur(Employe):
    _remunerationHSup = 70.00

    def __init__(self, nom="", dateNaissance=datetime(2000, 1, 1), dateEmbauche=None, salaireBase=0, heureSup=0):
        super().__init__(nom, dateNaissance, dateEmbauche, salaireBase)
        self._heureSup = heureSup

    def SalaireAPayer(self):
        heuresSup = self._heureSup
        if heuresSup >= 30:
            heuresSup = 30
        return (self._salaireBase + heuresSup * Formateur._remunerationHSup) * (1 - IR.getIR(self._salaireBase * 12))

    def __str__(self):
        return super().__str__() + "-" + str(self._heureSup)

def employe_encoder(obj):
    if isinstance(obj, Employe):
        return obj.__dict__
    return obj

def employe_decoder(dct):
    if 'nom' in dct:
        if 'heureSup' in dct:
            return Formateur(**dct)
        if 'primeResponsabilite' in dct:
            return Agent(**dct)
    return dct

def charger_comptes(fichier):
    try:
        with open(fichier, 'r') as file:
            return json.load(file, object_hook=employe_decoder)
    except FileNotFoundError:
        return []

def sauvegarder_comptes(comptes, fichier):
    with open(fichier, 'w') as file:
        json.dump(comptes, file, default=employe_encoder)

def ajouter_compte(comptes):
    print("\\nAjout d'un nouveau compte:")
    nom = input("Entrez le nom: ")
    dateNaissance = input("Entrez la date de naissance (AAAA-MM-JJ): ")
    dateEmbauche = input("Entrez la date d'embauche (AAAA-MM-JJ): ")
    salaireBase = float(input("Entrez le salaire de base: "))

    type_employe = input("Entrez le type d'employé (Agent/Formateur): ").lower()
    if type_employe == 'agent':
        primeResponsabilite = float(input("Entrez la prime de responsabilité: "))
        nouveau_compte = Agent(nom, datetime.fromisoformat(dateNaissance), 
                            datetime.fromisoformat(dateEmbauche), salaireBase, primeResponsabilite)
    elif type_employe == 'formateur':
        heureSup = float(input("Entrez le nombre d'heures supplémentaires: "))
        nouveau_compte = Formateur(nom, datetime.fromisoformat(dateNaissance), 
                                datetime.fromisoformat(dateEmbauche), salaireBase, heureSup)
    else:
        print("Type d'employé invalide. Veuillez choisir 'Agent' ou 'Formateur'.")
        return

    comptes.append(nouveau_compte)
    print("Compte ajouté avec succès.")

def supprimer_compte(comptes):
    if not comptes:
        print("Aucun compte à supprimer.")
        return

    print("\\nSuppression d'un compte:")
    mtle_a_supprimer = int(input("Entrez le matricule de l'employé à supprimer: "))
    for i, compte in enumerate(comptes):
        if compte.Matricule == mtle_a_supprimer:
            del comptes[i]
            print("Compte supprimé avec succès.")
            return
    print("Compte introuvable.")

def afficher_comptes(comptes):
    if not comptes:
        print("Aucun compte à afficher.")
        return

    print("\\nListe des comptes:")
    for compte in comptes:
        print(compte)

def menu_principal():
    comptes = charger_comptes('comptes.json')
    while True:
        print("1. Afficher les comptes \n2. Ajouter un compte \n3. Supprimer un compte \n4. Quitter")
        choix = input("Entrez votre choix: ")
        if choix == '1':
            afficher_comptes(comptes)
        elif choix == '2':
            ajouter_compte(comptes)
        elif choix == '3':
            supprimer_compte(comptes)
        elif choix == '4':
            sauvegarder_comptes(comptes, 'comptes.json')
            break
        else:
            print("Choix invalide. Veuillez réessayer.")


menu_principal()