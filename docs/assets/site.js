/* Kasalma — script commun à toutes les pages. */
(function () {
  'use strict';

  /* Cloudflare Web Analytics : mesure d'audience sans cookie.
     Coller ici le jeton fourni par Cloudflare (Web Analytics > Add a site > kasalma.com).
     Vide = aucune mesure. Jamais en local, pour ne pas compter nos propres visites. */
  var CF_BEACON_TOKEN = '1cbac80efe624542977195f052f7c6be';

  var host = location.hostname;
  var enLigne = /(^|\.)kasalma\.(com|fr)$/.test(host) || /\.github\.io$/.test(host);
  if (CF_BEACON_TOKEN && enLigne) {
    var s = document.createElement('script');
    s.defer = true;
    s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    s.setAttribute('data-cf-beacon', JSON.stringify({ token: CF_BEACON_TOKEN }));
    document.head.appendChild(s);
  }

  /* Liste d'attente : envoi en arrière-plan, message annoncé aux lecteurs d'écran. */
  document.querySelectorAll('form[data-waitlist]').forEach(function (form) {
    var status = form.querySelector('[data-status]');
    var button = form.querySelector('button[type="submit"]');

    function dire(message, etat) {
      status.textContent = message;
      status.dataset.state = etat;
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      if (/FORMSPREE_ID/.test(form.action)) {
        dire("La liste d'attente n'est pas encore branchée (aperçu local).", 'error');
        return;
      }
      button.disabled = true;
      dire('Envoi en cours…', 'pending');
      fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      })
        .then(function (response) {
          if (!response.ok) throw new Error(String(response.status));
          form.reset();
          dire("C'est noté ! Alma te prévient dès que Kasalma est prête.", 'ok');
        })
        .catch(function () {
          dire("Oups, l'envoi n'a pas marché. Réessaie dans un instant ou écris-nous à contact@kasalma.com.", 'error');
        })
        .finally(function () {
          button.disabled = false;
        });
    });
  });
})();
