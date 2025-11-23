# Resa-Scrapper

## Présentation

Resa-Scrapper est un script python qui se connecte pour vous à votre compte https://resa.centralesupelec.fr/ et gère pour vous la réservations des salles de musiques. Le script prend en entrée la date et l'heure à laquelle vous souhaitez avoir accès à une salle de musique et s'execute sous 4 modes :
- Mode "solo" : le script essaie de réserver une petite salle pour vous permettre de répéter tranquillement
- Mode "group" : le script essaie de réserver une grande salle pour vous permettre de répeter à plusieurs
- Mode "studio" (*Pas encore implémenté*): le script essaie de réserver le studio pour vous
- Mode "par défaut" : le script vous renvoie simplement la disponibilité des salles durant l'horaire précisé

## Prérequis

Resa-Scrapper utilise le module Selenium avec le navigateur Firefox. Vous avez donc besoin d'installer le driver "geckodriver".

Pour installer les modules pythons utilisés vous pouvez utiliser la commande
```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Identifiants resa.centralesupelec.fr

Le script se connecte via votre compte sur https://resa.centralesupelec.fr/ pour réserver directement pour vous. Vous devez donc fournir vos identifiants de votre compte CS. *Ces identifiants sont conservés localement sur un fichier à part et ne sont donc pas transmis à qui que ce soit*.

Pour se faire, vous devez créer un fichier `.env` dans la racine du projet dans lequel vous entrez vos identifiants sous le format suivant :
```js
USERNAME=prenom.nom@student-cs.fr
PASSWORD=votre_mot_de_passe
TITLE=le_titre_de_vos_futurs_réservations
```

### 2. Éxecution du script

Ouvez une invite de commande dans la racine du projet et lancez le script comme suit

```bash
python3 main.py <date:YYYY-MM-DD> <timeslot:HH:MM-HH:MM> <mode: /solo/group/studio>
```
Exemple : la commande
```bash
python3 main.py 2025-11-27 11:30-12:30
```
Va chercher quelles salles sont disponibles le 11 novembre 2025 entre 11h30 et 12h30. Voici ce que le script renvoie sur l'invite de commandes
```
--------------------------------------------
LE 2025-11-27 À 11:30-12:30
--------------------------------------------
SALLE: e.008
  ETAT: DISPONIBLE
  RESERVATIONS:
    - Piano: 13:0-14:30 | RÉSERVÉE PAR: Eglantine Jacquinet--jeangout
--------------------------------------------
SALLE: e.010
  ETAT: DISPONIBLE
  RESERVATIONS:
    - Paris 2026: 14:0-15:59 | RÉSERVÉE PAR: Mehdi Tanana
    - HEBCHA: 17:0-19:0 | RÉSERVÉE PAR: Jean-loup Chabas
    - L'FSF là: 19:30-21:15 | RÉSERVÉE PAR: Quentin Scholler
--------------------------------------------
SALLE: e.012
  ETAT: DISPONIBLE
  RESERVATIONS:
    - Répétition: 20:0-21:59 | RÉSERVÉE PAR: Mehdi Tanana
--------------------------------------------
SALLE: e.090
  ETAT: DISPONIBLE
--------------------------------------------
SALLE: e.091
  ETAT: DISPONIBLE
  RESERVATIONS:
    - Quintet Cuivres: 18:0-20:0 | RÉSERVÉE PAR: Raphaël Lubineau
    - répétition brass'art: 20:15-22:15 | RÉSERVÉE PAR: Julien Baltazar
--------------------------------------------
SALLE: e.092
  ETAT: DISPONIBLE
--------------------------------------------
SALLE: e.094 (SECS)
  ETAT: DISPONIBLE
--------------------------------------------
```
Rajouter un argument "solo","group" ou "studio" va réserver une salle appropriée s'il y'en a une de disponible selon l'ordre de priorité suivant :
- "solo" : e.090, e.008 ou e.092
- "group" : e.010, e.012, e.091
- "studio" : e.094

### 3. Attention
- Vous ne pouvez pas réserver une salle sur un créneau supérieur à 2h (limitation imposée par le site). Le script vous en empêchera de le faire dans tous les cas.
- Je n'ai aucune idée de comment le script réagit si on essaie de réserver pour une date trop éloignée, mais de toute façon si vous essayez de réserver une salle pour dans 30 jours, vous êtes tarés.
- L'argument "studio" n'est pas encore implémenté : ça arrive bientôt j'ai juste eu la flemme pour le moment.