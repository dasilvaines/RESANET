#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import *
from modeles import modeleResanet
from technique import datesResanet


app = Flask( __name__ )
app.secret_key = 'resanet'


@app.route( '/' , methods = [ 'GET' ] )
def index() :
	return render_template( 'vueAccueil.html' )

@app.route( '/usager/session/choisir' , methods = [ 'GET' ] )
def choisirSessionUsager() :
	return render_template( 'vueConnexionUsager.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

@app.route( '/usager/seConnecter' , methods = [ 'POST' ] )
def seConnecterUsager() :
	numeroCarte = request.form[ 'numeroCarte' ]
	mdp = request.form[ 'mdp' ]
	
	print numeroCarte  , " " , mdp

	if numeroCarte != '' and mdp != '' :
		usager = modeleResanet.seConnecterUsager( numeroCarte , mdp )
		if len(usager) != 0 :
			if usager[ 'activee' ] == True :
				session[ 'numeroCarte' ] = usager[ 'numeroCarte' ]
				session[ 'nom' ] = usager[ 'nom' ]
				session[ 'prenom' ] = usager[ 'prenom' ]
				session[ 'mdp' ] = mdp
				
				return redirect( '/usager/reservations/lister' )
				
			else :
				return render_template('vueConnexionUsager.html', carteBloquee = True , echecConnexion = False , saisieIncomplete = False )
		else :
			return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionUsager.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)


@app.route( '/usager/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterUsager() :
	session.pop( 'numeroCarte' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	return redirect( '/' )


@app.route( '/usager/reservations/lister' , methods = [ 'GET' ] )
def listerReservations() :
	tarifRepas = modeleResanet.getTarifRepas( session[ 'numeroCarte' ] )
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	
	solde = '%.2f' % ( soldeCarte , )

	aujourdhui = datesResanet.getDateAujourdhuiISO()
	aujourdhuis = datesResanet.getDateAujourdhuiFR()
	jours = [ "Lundi" , "Mardi" , "Mecredi" , "Jeudi" , "Vendredi"  ]
	datesPeriodeISO = datesResanet.getDatesPeriodeCouranteISO()
	
	datesResas = modeleResanet.getReservationsCarte( session[ 'numeroCarte' ] , datesPeriodeISO[ 0 ] , datesPeriodeISO[ -1 ] )
	
	dates = []
	for uneDateISO in datesPeriodeISO :
		uneDate = {}
		uneDate[ 'iso' ] = uneDateISO
		uneDate[ 'fr' ] = datesResanet.convertirDateISOversFR( uneDateISO )
		estFerie = modeleResanet.estJoursFeries(uneDateISO)
		
		if uneDateISO <= aujourdhui or estFerie == True :
			uneDate[ 'verrouillee' ] = True
		else :
			uneDate[ 'verrouillee' ] = False

		if uneDateISO in datesResas :
			uneDate[ 'reservee' ] = True
		else :
			uneDate[ 'reservee' ] = False
			
		if soldeCarte < tarifRepas and uneDate[ 'reservee' ] == False :
			uneDate[ 'verrouillee' ] = True
			
			
		dates.append( uneDate )
	
	if soldeCarte < tarifRepas :
		soldeInsuffisant = True
	else :
		soldeInsuffisant = False
		
	
	return render_template( 'vueListeReservations.html' , laSession = session , leSolde = solde , lesDates = dates , soldeInsuffisant = soldeInsuffisant , aujourdhui = aujourdhuis , jours= jours )

	
@app.route( '/usager/reservations/annuler/<dateISO>' , methods = [ 'GET' ] )
def annulerReservation( dateISO ) :
	modeleResanet.annulerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.crediterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )
	
@app.route( '/usager/reservations/enregistrer/<dateISO>' , methods = [ 'GET' ] )
def enregistrerReservation( dateISO ) :
	modeleResanet.enregistrerReservation( session[ 'numeroCarte' ] , dateISO )
	modeleResanet.debiterSolde( session[ 'numeroCarte' ] )
	return redirect( '/usager/reservations/lister' )

@app.route( '/usager/mdp/modification/choisir' , methods = [ 'GET' ] )
def choisirModifierMdpUsager() :
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = '' )

@app.route( '/usager/mdp/modification/appliquer' , methods = [ 'POST' ] )
def modifierMdpUsager() :
	ancienMdp = request.form[ 'ancienMDP' ]
	nouveauMdp = request.form[ 'nouveauMDP' ]
	
	soldeCarte = modeleResanet.getSolde( session[ 'numeroCarte' ] )
	solde = '%.2f' % ( soldeCarte , )
	
	if ancienMdp != session[ 'mdp' ] or nouveauMdp == '' :
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Nok' )
		
	else :
		modeleResanet.modifierMdpUsager( session[ 'numeroCarte' ] , nouveauMdp )
		session[ 'mdp' ] = nouveauMdp
		return render_template( 'vueModificationMdp.html' , laSession = session , leSolde = solde , modifMdp = 'Ok' )


@app.route( '/gestionnaire/session/choisir' , methods = [ 'GET' ] )
def choisirSessionGestionnaire() :
	return render_template( 'vueConnexionGestionnaire.html' , carteBloquee = False , echecConnexion = False , saisieIncomplete = False )

	
@app.route( '/gestionnaire/seConnecter' , methods = [ 'POST' ] )
def seConnecterGestionnaire() :
	login = request.form[ 'identifiant' ]
	mdp = request.form[ 'mdp' ]

	if login != '' and mdp != '' :
		gestionnaire = modeleResanet.seConnecterGestionnaire( login , mdp )
		if len(gestionnaire) != 0 :
				session[ 'login' ] = gestionnaire[ 'login' ]
				session[ 'nom' ] = gestionnaire[ 'nom' ]
				session[ 'prenom' ] = gestionnaire[ 'prenom' ]
				session[ 'mdp' ] = mdp
					
				return redirect( '/gestionnaire/personnelAvecCarte/lister' )	
		else :
			return render_template('vueConnexionGestionnaire.html', carteBloquee = False , echecConnexion = True , saisieIncomplete = False )
	else :
		return render_template('vueConnexionGestionnaire.html', carteBloquee = False , echecConnexion = False , saisieIncomplete = True)

@app.route( '/gestionnaire/personnelAvecCarte/lister' , methods = [ 'GET' ] )
def listerPersonnelAvecCarte() :
	
	personnels = modeleResanet.getPersonnelsAvecCarte()

	return render_template( 'vuePersonnelsAvecCarte.html' , personnels = personnels)
	
@app.route( '/gestionnaire/personnelSansCarte/lister' , methods = [ 'GET' ] )
def listerPersonnelSansCarte() :
	
	personnels = modeleResanet.getPersonnelsSansCarte()

	return render_template( 'vuePersonnelSansCarte.html' , personnels = personnels)
	
@app.route( '/gestionnaire/listerPersonnelAvecCarte/bloquer' , methods=['POST'] )
def desactiverCarte() :
	numeroCarte = request.form[ 'numeroCarte' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.bloquerCarte(numeroCarte)
	return redirect( '/gestionnaire/personnelAvecCarte/lister' )
	
@app.route( '/gestionnaire/listerPersonneAvecCarte/activer' , methods=['POST'] )
def activeeCarte() :
	numeroCarte = request.form[ 'numeroCarte' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.activerCarte(numeroCarte)
	return redirect( '/gestionnaire/personnelAvecCarte/lister' )

@app.route( '/gestionnaire/listerPersonneAvecCarte/initMdp' , methods=['POST'] )
def initMDP() :
	changer = True
	personnels = modeleResanet.getPersonnelsAvecCarte()
	numeroCarte = request.form[ 'numeroCarte' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.reinitialiserMdp(numeroCarte)
	return render_template( 'vuePersonnelsAvecCarte.html' , changer = changer , personnels = personnels)
	
@app.route( '/gestionnaire/listerPersonneSansCarte/creationCompte' , methods=['POST'] )
def creerCompte() :
	
	matricule = request.form[ 'matricule' ]
	
	print "\n\n\nMatricule : " , matricule
	
	
	if request.form.has_key('activerCarte') :
		modeleResanet.creerCarte(matricule,True)
	else :
		#ModeleResanet.creerCarte(matricule)
		modeleResanet.creerCarte(matricule,False)
		
	
	
	creer = True
	personnels = modeleResanet.getPersonnelsSansCarte()
	
	return render_template( 'vuePersonnelSansCarte.html' , creer = creer , personnels = personnels)
	
		
@app.route( '/gestionnaire/listerPersonnelAvecCarte/crediter' , methods=['POST'] )
def goCredit() :
	numCarte = request.form[ 'numeroCarte' ]
	solde = request.form[ 'solde' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]	
	personnels = modeleResanet.getPersonnelsAvecCarte()
	lePersonnel = [ numCarte , nom , prenom , service , solde ]
	return render_template( 'vuePersonnelsAvecCarte.html'  , personnels = personnels , cardC = True , lePersonnel = lePersonnel )

@app.route( '/gestionnaire/listerPersonnelAvecCarte/crediter/credit' , methods=['POST'] )
def credit() :
	nom = request.form['nom']
	prenom = request.form['prenom']
	credit = request.form['credit']
	numCarte = request.form['numCarte']
	rep = modeleResanet.crediterCarte( numCarte , credit )
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'vuePersonnelsAvecCarte.html'  , personnels = personnels , credit = True , nom = nom , prenom = prenom )
	
@app.route( '/gestionnaire/listerPersonnelAvecCarte/historique' , methods=['POST'] )
def historique() :
	
	dates = []
	numCarte = request.form[ 'numeroCarte' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]
	lePersonnel = [ numCarte , nom , prenom , service  ]
	date = modeleResanet.getHistoriqueReservationsCarte( numCarte )
	
	if len(date) == 0 :
		rien = True
	else :
		rien = False
	for uneDate in date :
		dates.append(datesResanet.convertirDateISOversFR( uneDate ))		
	personnels = modeleResanet.getPersonnelsAvecCarte()
	
	return render_template( 'vuePersonnelsAvecCarte.html'  , personnels = personnels , cardH = True , dates = dates , lePersonnel = lePersonnel , rien = rien )
	
	
@app.route( '/gestionnaire/gererCarte' , methods=['GET'] )
def goGerer() :
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'gererCarte.html' , personnels = personnels )
	
	
@app.route( '/gestionnaire/gererCarte/bloquer' , methods=['POST'] )
def desactiverC() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)
	rep = modeleResanet.bloquerCarte(numeroCarte)
	return redirect( '/gestionnaire/gererCarte' )
	
@app.route( '/gestionnaire/gererCarte/activer' , methods=['POST'] )
def activeeC() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)
	print numeroCarte
	rep = modeleResanet.activerCarte(numeroCarte)
	return redirect( '/gestionnaire/gererCarte' )

@app.route( '/gestionnaire/gererCarte/initMdp' , methods=['POST'] )
def initMDPCarte() :
	numeroCarte = request.form[ 'matricule' ]
	numeroCarte = str(numeroCarte)	
	mdp = modeleResanet.getMdp( numeroCarte )
	ddn = modeleResanet.getNaissance( numeroCarte )
	if str(ddn) != str(mdp) :
		rep = modeleResanet.reinitialiserMdp(numeroCarte)
		changer = True
	else :		
		changer = False
	personnels = modeleResanet.getPersonnelsAvecCarte()
	for unPersonnel in personnels :
		if unPersonnel['numeroCarte'] == int(numeroCarte) :
			nom = unPersonnel['nom']
			prenom = unPersonnel['prenom']
	return render_template( 'gererCarte.html'  , personnels = personnels , changer = changer , nom = nom , prenom = prenom )	
	
@app.route( '/gestionnaire/gererCarte/history' , methods=['POST'] )
def historiqueC() :
	dates = []
	numCarte = request.form[ 'numeroCarte' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]
	lePersonnel = [ numCarte , nom , prenom , service  ]
	date = modeleResanet.getHistoriqueReservationsCarte( numCarte )
	if len(date) == 0 :
		rien = True
	else :
		rien = False
	for uneDate in date :
		dates.append(datesResanet.convertirDateISOversFR( uneDate ))		
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'gererCarte.html'  , personnels = personnels , cardH = True , dates = dates , lePersonnel = lePersonnel , rien = rien )
	
@app.route( '/gestionnaire/gererCarte/crediter' , methods=['POST'] )
def goCreditC() :
	numCarte = request.form[ 'numeroCarte' ]
	solde = request.form[ 'solde' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]	
	personnels = modeleResanet.getPersonnelsAvecCarte()
	lePersonnel = [ numCarte , nom , prenom , service , solde ]
	return render_template( 'gererCarte.html'  , personnels = personnels , cardC = True , lePersonnel = lePersonnel )
	
@app.route( '/gestionnaire/gererCarte/crediter/credit' , methods=['POST'] )
def creditC() :
	nom = request.form['nom']
	prenom = request.form['prenom']
	credit = request.form['credit']
	numCarte = request.form['numCarte']
	rep = modeleResanet.crediterCarte( numCarte , credit )
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'gererCarte.html'  , personnels = personnels , credit = True , nom = nom , prenom = prenom )
	
@app.route( '/gestionnaire/gererCarte/debiter' , methods=['POST'] )
def goDebitC() :
	numCarte = request.form[ 'numeroCarte' ]
	solde = request.form[ 'solde' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]	
	personnels = modeleResanet.getPersonnelsAvecCarte()
	lePersonnel = [ numCarte , nom , prenom , service , solde ]
	return render_template( 'gererCarte.html'  , personnels = personnels , cardD = True , lePersonnel = lePersonnel  )
	
@app.route( '/gestionnaire/gererCarte/debiter/debit' , methods=['POST'] )
def debitC() :
	nom = request.form['nom']
	prenom = request.form['prenom']
	credit = request.form['credit']
	numCarte = request.form['numCarte']
	rep = modeleResanet.debiterCarte( numCarte , credit )
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'gererCarte.html'  , personnels = personnels , debit = True , nom = nom , prenom = prenom )
	
@app.route( '/gestionnaire/gererCarte/supprimer' , methods=['POST'] )
def suppCarte() :
	nom = request.form['nom']
	prenom = request.form['prenom']
	numCarte = request.form['numCarte']
	rep = modeleResanet.supprimerCarte( numCarte )
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'gererCarte.html'  , personnels = personnels , supp = True , nom = nom , prenom = prenom )
	
@app.route( '/gestionnaire/creerCarte' , methods = [ 'GET' ] )
def goCreerCarte() :		
	aujourdhui = datesResanet.getDateAujourdhuiISO()	
	aujourdhuis = datesResanet.convertirDateISOversFR(aujourdhui)
	personnels = modeleResanet.getPersonnelsSansCarte()
			
	return render_template( 'creerCarte.html' , aujourdhuis = aujourdhuis , personnels = personnels )
	
@app.route( '/gestionnaire/creerCarte/creation' , methods=['POST'] )
def creationCarte() :
	prenom = request.form[ 'prenom' ]
	nom = request.form[ 'nom' ]
	matricule = request.form[ 'matricule' ]
	activation = request.form[ 'activ' ]
	
	if activation == "False" :
		activation = False
		rep = modeleResanet.creerCarte( matricule , activation )	
		personnels = modeleResanet.getPersonnelsSansCarte()				
		return render_template( 'creerCarte.html' , personnels = personnels , activation = "bloque" , cree = True  , nom = nom , prenom = prenom )
	elif activation == "True" :		
		activation = True
		rep = modeleResanet.creerCarte( matricule , activation )	
		personnels = modeleResanet.getPersonnelsSansCarte()		
		return render_template( 'creerCarte.html' , personnels = personnels , activation = "active" , cree = True , nom = nom , prenom = prenom )

@app.route( '/gestionnaire/listerHistCarte' , methods=['GET'] )
def histCarte():
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'listerHistCarte.html'  , personnels = personnels )

@app.route( '/gestionnaire/listerHistCarte/history' , methods=['POST'] )
def historiqueCarte():
	dates = []
	numCarte = request.form[ 'numeroCarte' ]
	nom = request.form[ 'nom' ]
	service = request.form[ 'service' ]
	prenom = request.form[ 'prenom' ]
	lePersonnel = [ numCarte , nom , prenom , service  ]
	date = modeleResanet.getHistoriqueReservationsCarte( numCarte )
	if len(date) == 0 :
		rien = True
	else :
		rien = False
	for uneDate in date :
		dates.append(datesResanet.convertirDateISOversFR( uneDate ))		
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'listerHistCarte.html'  , personnels = personnels , cardH = True , dates = dates , lePersonnel = lePersonnel , rien= rien )
	
	
@app.route( '/gestionnaire/listerHistDate' , methods=['GET'] )
def historiqueDate():
	personnels = modeleResanet.getPersonnelsAvecCarte()
	return render_template( 'listerHistDate.html' , personnels = personnels )
	

@app.route( '/gestionnaire/resa/date' , methods = ['POST'] )
def resaDate():
	laDate = request.form['date']
	print "> " + laDate
	resas = modeleResanet.getReservationsDate( datesResanet.convertirDateFRversISO(laDate) )
	print "> " + str( resas )
	return render_template( 'listerCartesPourDate.html' , resas = resas )
	
	
@app.route( '/gestionnaire/joursFeries/lister' , methods= [ 'GET' ] )
def listerJoursFeries():
	ferie = modeleResanet.getJoursFeries()
	print "Jours feries : " , ferie
	
	return render_template('joursFeries.html' , ferie = ferie )
	
	
@app.route( '/gestionnaire/joursFeries/supp' , methods=['POST'] )
def supJoursFeries():
	jour = request.form[ 'jour' ]
	mois = request.form[ 'mois' ]
	print jour 
	print mois
	rep = modeleResanet.suppJoursFeries( jour , mois )
	jours = modeleResanet.getJoursFeries()
	return render_template( 'joursFeries.html' , ferie = jours , cardS = True , jour = jour , mois = mois)
	 
	
@app.route( '/gestionnaire/joursFeries/ajouter' , methods=['POST'] )
def ajouterJoursFeries():
	jour = request.form[ 'jour' ]
	mois = request.form[ 'mois' ]
	libelle = request.form[ 'libelle' ]
	rep = modeleResanet.setJoursFeries( jour , mois , libelle )
	jours = modeleResanet.getJoursFeries()
	return render_template( 'joursFeries.html' , ferie = jours , card = True , jour = jour , mois = mois)
	
@app.route( '/gestionnaire/joursFeries/goAjout' , methods=['GET'] )	
def goAjouterJoursFeries():
	jours = modeleResanet.getJoursFeries()
	return render_template( 'joursFeries.html' , ferie = jours , cardAjout = True )
	
@app.route( '/gestionnaire/seDeconnecter' , methods = [ 'GET' ] )
def seDeconnecterGestionnaire() :
	session.pop( 'login' , None )
	session.pop( 'nom' , None )
	session.pop( 'prenom' , None )
	session.pop( 'mdp' , None )
	return redirect( '/' )


if __name__ == '__main__' :
	app.run( debug = True , host = '0.0.0.0' , port = 5000 )
