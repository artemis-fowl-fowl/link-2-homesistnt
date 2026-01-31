# Link 2 Home Assistant (HACS)

Relie deux instances Home Assistant et synchronise un switch distant.

## Installation (HACS)
1. Ajoutez ce dépôt comme **Custom Repository** dans HACS (type Integration).
2. Installez l'intégration.
3. Redémarrez Home Assistant.

## Configuration (UI)
Allez dans **Paramètres → Appareils & Services → Ajouter une intégration** puis cherchez **Link 2 Home Assistant**.

Vous pourrez renseigner :
- URL distante
- Jeton d’accès longue durée
- entity_id du switch distant
- (Optionnel) switch local à relayer
- Intervalle de rafraîchissement

## Configuration (configuration.yaml)

```yaml
switch:
  - platform: link_2_homesistant
    name: "Gabriel Link"
    remote_url: "http://192.168.1.50:8123"
    remote_token: "LONG_LIVED_ACCESS_TOKEN"
    remote_entity_id: "switch.receiver"
    # Optionnel : écoute un switch local et le transmet au remote
    source_entity_id: "switch.gabriel"
    poll_interval: 5
```

## Fonctionnement
- Le switch créé reflète l'état du switch distant.
- Si `source_entity_id` est défini, chaque changement local est envoyé au distant.
