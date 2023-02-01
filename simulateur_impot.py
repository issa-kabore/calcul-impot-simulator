
# Iportation des biblio
import math
import configparser # Permet de parser le fichier de paramètres #pip install configparser
import numpy as np

# -----------------------------------------------------------------------------------------------------------
# Fonction for configuration file
# -----------------------------------------------------------------------------------------------------------
def recup_impots_param(config_file='impot.config'):
    config = configparser.RawConfigParser() # On créé un nouvel objet "config"
    config.read(config_file) # On lit le fichier de paramètres
    # On récupère les valeurs des différents paramètres
    # Récupération basique dans des variables
    annee = config.get(section='DEFAULT',option='annee')
    tranches_impots = config.get(section='Bareme des impots',option='tranches').split(',')
    for i in range(len(tranches_impots)):
        tranches_impots[i] =(int(tranches_impots[i]))
            
    taux_imposition = config.get(section='Bareme des impots',option='taux_imposition').split(',')
    for i in range(len(taux_imposition)):
        taux_imposition[i] =(float(taux_imposition[i]))


    plafond_decote = config.get(section='Reduction',option='plafond_decote').split(',')
    for i in range(len(plafond_decote)):
        plafond_decote[i] =(float(plafond_decote[i]))

    param_decote = config.get(section='Reduction',option='param_decote').split(',')
    for i in range(len(param_decote)):
        param_decote[i] =(float(param_decote[i]))

    ABATTEMENT = config.get(section='Reduction',option='ABATTEMENT').split(',')
    for i in range(len(ABATTEMENT)):
        ABATTEMENT[i] =(float(ABATTEMENT[i]))

    coef_decote = config.getfloat(section='Reduction',option='coef_decote')
    PLAFOND_QF_DEMI_PART = config.getfloat(section='Reduction',option='PLAFOND_QF_DEMI_PART')
    PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION = config.getfloat(section='Reduction',option='PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION')
    PLAFOND_REVENUS_COUPLE_POUR_REDUCTION = config.getfloat(section='Reduction',option='PLAFOND_REVENUS_COUPLE_POUR_REDUCTION')
    VALEUR_REDUC_DEMI_PART = config.getfloat(section='Reduction',option='VALEUR_REDUC_DEMI_PART')

    return annee, tranches_impots, taux_imposition, plafond_decote, param_decote, coef_decote, ABATTEMENT, \
        PLAFOND_QF_DEMI_PART, PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION, PLAFOND_REVENUS_COUPLE_POUR_REDUCTION, VALEUR_REDUC_DEMI_PART
        


def presentation(annee, marié, enfants, revenu):
    """
    Fonction de saisie
    """
    # marié : oui, non
    # enfants : nombre d'enfants
    # salaire : salaire annuel
    #print('-- DEBUT de saisie')
    enfants = int(enfants)
    assert(enfants >= 0)
    
    revenu =float(revenu) 
    assert(revenu >= 0)

    marié = marié.strip().lower()
    if (marié == "oui") | (marié == "o") | (marié == "y"):
        nb_parts = enfants*0.5 + 2
        statut_familial='oui'
    else:
        nb_parts = enfants*0.5 + 1
        statut_familial='non'

    # 1 part par enfant à partir du 3ième
    if enfants >= 3:
        # une demi-part de + pour chaque enfant à partir du 3ième
        nb_parts += 0.5 * (enfants - 2)
    #print('==> Saisie TERMINEE.')
    return statut_familial, enfants,nb_parts, revenu


# revenu_imposable = salaireAnnuel - abattement
# l'abattement a un min et un max
# ----------------------------------------
def get_revenu_imposable(salaire: int,ABATTEMENT,nb_parts) -> int:
    # abattement de 10% du salaire
    abattement = 0.1 * salaire
    # cet abattement ne peut dépasser ABATTEMENT__MAX = ABATTEMENT__MAX[1]
    if abattement > ABATTEMENT[1] :
        abattement = ABATTEMENT[1]

    # l'abattement ne peut être inférieur à ABATTEMENT_MIN = ABATTEMENT__MAX(0)
    if abattement < ABATTEMENT[0]:
        abattement = ABATTEMENT[0]

    # revenu imposable
    revenu_imposable = salaire - abattement
    # quotient familial
    quotient = revenu_imposable / nb_parts
    return revenu_imposable, quotient


    
def calcul_impôt(income, tranches_impots, taux_imposition):
    difference = np.diff(tranches_impots)
    state = True
    taxe = 0
    i = 0
    print("-- Application du barème ...")
    while state:
        if income < tranches_impots[i + 1]:
            taxe += (income -
                             tranches_impots[i]) * taux_imposition[i]
            state = False
        else:
            taxe += difference[i] * taux_imposition[i]

            state = True

        #print('Impot sur la tranche {} ({}%) = {} Euros'.format(i+1, (taux_imposition[i]*100), taxe))
        i = i + 1
    taux = taux_imposition[i-1]*100  #Le taux marginal d'imposition (TMI)
    return taxe,taux

# calcule une décôte éventuelle
def get_décôte(marié: str, salaire: int, impots: int,plafond_decote,param_decote,coef_decote) -> int:
    # au départ, une décôte nulle
    décôte = 0
    # montant maximal d'impôt pour avoir la décôte
    plafond_impôt_pour_décôte = plafond_decote[1] if marié == "oui" else plafond_decote[0]
    if impots < plafond_impôt_pour_décôte:
        # montant maximal de la décôte
        plafond_décôte = param_decote[1] if marié == "oui" else param_decote[1]
        # décôte théorique
        décôte = plafond_décôte - coef_decote * impots
        # la décôte ne peut dépasser le montant de l'impôt
        if décôte > impots:
            décôte = impots

        # pas de décôte <0
        if décôte < 0:
            décôte = 0
    #print('==> Décote : {0:2.2f} Euros'.format(décôte))
    # résultat
    return décôte
    
def calcul_réduction(marié: str, salaire: int, enfants: int, impots: int,PLAFOND_REVENUS_COUPLE_POUR_REDUCTION,
    PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION, VALEUR_REDUC_DEMI_PART, revenu_imposable) -> int:
    """la réduction d’impôt sous condition de revenu fiscal de référence (RFR)"""
    # le plafond des revenus pour avoir droit à la réduction de 20%
    plafond_revenu_pour_réduction = PLAFOND_REVENUS_COUPLE_POUR_REDUCTION if marié == "oui" else PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION
    plafond_revenu_pour_réduction += enfants * VALEUR_REDUC_DEMI_PART
    if enfants > 2:
        plafond_revenu_pour_réduction += (enfants - 2) * VALEUR_REDUC_DEMI_PART

    # réduction
    réduction = 0
    if revenu_imposable < plafond_revenu_pour_réduction:
        # réduction de 20%
        réduction = 0.2 * impots
    #print('==> Reduction de l"impot sous condition de RFR : {0:2.2f} Euros'.format(réduction))
    # résultat
    return réduction




# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask,render_template, request
import  webbrowser
from threading import Timer

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__,template_folder='./')

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def home():
    return render_template('homepage.html')



@app.route('/estimate/', methods = ['Get', 'POST'])
def estimate():
    if request.method == "POST":
        #get the configuration
        annee, tranches_impots, taux_imposition, plafond_decote, param_decote, coef_decote, ABATTEMENT, \
        PLAFOND_QF_DEMI_PART, PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION,\
             PLAFOND_REVENUS_COUPLE_POUR_REDUCTION, VALEUR_REDUC_DEMI_PART = recup_impots_param()

        result = {"marié": 0, "enfants": 0, "nb_parts": 0,"revenu": 0,"annee": 0, "reduction": 0,
            "revenu_imposable": 0,"impot": 0,"taux": 0,"quotient": 0, "decote": 0 , "taux_personnalisé" : 0}
        #get form data
        année = request.form.get('Année')
        marié = request.form.get('marié')
        enfants = request.form.get('enfants')
        revenu = request.form.get('Revenu')
        try:
            statut_familial, enfants,nb_parts,revenu = presentation(année, marié, enfants, revenu)
            result['annee']=annee
            result['nb_parts']=nb_parts
            result['revenu']=revenu
            result['marié']=statut_familial
            result['enfants']=enfants
            # Calcul de l'impot de l'année 
            
            revenu_imposable, qf = get_revenu_imposable(revenu, ABATTEMENT,nb_parts)
            result['revenu_imposable']=revenu_imposable
            result['quotient']=qf

            impot_brute, TMI = calcul_impôt(revenu,tranches_impots, taux_imposition)
            result['taux']=np.round(TMI)
            

            # calcul d'une éventuelle décôte    
            decote = get_décôte(marié, revenu_imposable, impot_brute,plafond_decote,param_decote,coef_decote)
            result['decote'] = round(decote,2)
            impot = impot_brute - decote

            # calcul d'une éventuelle réduction d'impôts
            réduction = calcul_réduction(marié, revenu_imposable, enfants, impot, PLAFOND_REVENUS_COUPLE_POUR_REDUCTION,\
                            PLAFOND_REVENUS_CELIBATAIRE_POUR_REDUCTION, VALEUR_REDUC_DEMI_PART, revenu_imposable)
            impot_total = impot - réduction
            result['reduction'] = round(réduction,2)

            result['impot'] = round(impot_total , 2)
            result['impot_mensuel'] = round(impot_total/12 , 2)
            result['taux_personnalisé'] = round(impot_total * 100 / revenu_imposable,2)

        
            
            
            #pass info to template
            return render_template('estimation.html', info = result)
        except ValueError:
            return "Please Enter valid values"
        pass
    pass

def open_browser():
      webbrowser.open_new('http://127.0.0.1:2000/')

# main driver function
if __name__ == '__main__':
	# run() method of Flask class runs the application
	# on the local development server.
    Timer(1, open_browser).start();
    app.run(port=2000)

