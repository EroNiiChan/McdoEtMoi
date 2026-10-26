import random

def generer_commentaire():
    style_client = random.choices(
        ["ultra_court", "focus_repas", "focus_service", "phrase_complete"],
        weights=[25, 30, 25, 20],
        k=1
    )[0]

    if style_client == "ultra_court":
        mots = [
            "Nickel", "Parfait", "Top", "Rien à dire", "RAS", 
            "Super rapide", "Très bien", "Au top comme d'hab", 
            "Tout était parfait", "Impeccable", "Bien chaud et rapide",
            "Service au top", "Rien a signaler", "Super"
        ]
        phrase = random.choice(mots)

    elif style_client == "focus_repas":
        debuts = [
            "Commande complète", "Repas bien chaud", "Frites bien chaudes", 
            "Burgers bien chauds", "Il ne manquait rien", "Tout était chaud",
            "Commande prête rapidement"
        ]
        suites = [
            "et service rapide", "c'est appréciable", "nickel", 
            "rien à redire", "comme d'habitude", "et bon accueil",
            "même les frites", "top", ""
        ]
        d = random.choice(debuts)
        s = random.choice(suites)
        
        if s:
            liaison = random.choice([", ", " ", " et "]) if not s.startswith("et ") else " "
            phrase = f"{d}{liaison}{s}"
        else:
            phrase = d

    elif style_client == "focus_service":
        sujets_masc = ["Le service", "L'accueil", "Le personnel", "Le resto"]
        qualif_masc = ["super rapide", "au top", "vraiment sympa", "très pro", "nickel", "efficace", "propre et rapide"]
        
        sujets_fem = ["L'équipe", "La personne au comptoir", "La commande"]
        qualif_fem = ["très souriante", "super efficace", "au top", "rapide", "vraiment sympa", "impeccable"]

        if random.random() < 0.5:
            verbe = random.choice(["était ", "est ", "toujours ", ""])
            phrase = f"{random.choice(sujets_masc)} {verbe}{random.choice(qualif_masc)}"
        else:
            verbe = random.choice(["était ", "est ", "vraiment ", ""])
            phrase = f"{random.choice(sujets_fem)} {verbe}{random.choice(qualif_fem)}"

    else:
        debuts = [
            "Toujours un plaisir de passer", "Servi rapidement malgré le monde",
            "Pas d'attente et commande complète", "Jamais déçu dans ce McDo",
            "Rapide et efficace", "Bon accueil et service rapide",
            "Toujours propre et service rapide", "Pas d'oubli dans les sacs"
        ]
        fins = [
            "", ", merci", " merci à l'équipe", ", je recommande", 
            ", c'est top", ", rien à dire", " comme d'hab"
        ]
        phrase = f"{random.choice(debuts)}{random.choice(fins)}"

    ponctuation = random.choices(
        ["", ".", " !", " !!", " :)"],
        weights=[45, 30, 15, 5, 5],
        k=1
    )[0]
    phrase = phrase + ponctuation

    if random.random() < 0.30 and phrase != "RAS":
        phrase = phrase[0].lower() + phrase[1:]

    return phrase