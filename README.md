# MediCalendar

Webapp (PWA) de rappel de prise de médicaments et de commande en pharmacie.

## Contenu du dossier

- `index.html` : toute l'application (écrans, logique, stockage local)
- `manifest.webmanifest` : nom, icône, mode plein écran
- `sw.js` : fonctionnement hors ligne, clic sur notification, réception de push
- `icons/` : icône blanche au caducée rouge (192, 512, maskable, Apple, badge)

## Mettre en ligne (sans Mac)

L'app doit être servie en HTTPS pour s'installer et recevoir des notifications.
Le plus simple : GitHub Pages ou Netlify Drop.

1. Netlify Drop : glissez le dossier `MediCalendar` sur https://app.netlify.com/drop
2. Ou GitHub Pages : créez un dépôt, envoyez le contenu du dossier, puis Settings → Pages → branche `main`.

## Installer sur iPhone (iOS 16.4 ou plus)

1. Ouvrez l'adresse dans **Safari**.
2. Partager → **Sur l'écran d'accueil**.
3. Lancez MediCalendar depuis l'icône, puis Réglages → **Activer les notifications**.

Sur Android : Chrome → menu → **Installer l'application**.

## Fonctionnement des rappels

- Heures par défaut : matin 08:00, midi 12:30, soir 19:30 (modifiables dans Réglages).
- La pastille de l'icône affiche le nombre de prises restantes du jour.
- Commande : l'app rappelle « X jours / semaines / mois » avant la date de fin de la boîte.
  Touchez « C'est commandé » puis indiquez la nouvelle date de fin.

### Limite actuelle

Les notifications partent quand l'app tourne (ouverte ou récemment en arrière-plan).
Pour des notifications garanties app fermée, il faut un petit serveur Web Push
(par exemple une tâche planifiée Cloudflare Workers). `sw.js` sait déjà les recevoir :
charge utile JSON `{ "title": "...", "body": "...", "count": 3 }`.

## Données

Tout est stocké sur l'appareil (localStorage). Rien n'est envoyé sur Internet.
