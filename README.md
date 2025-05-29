# Convertitore Chat WhatsApp in HTML

![Icona progetto](icon.png)

Uno strumento a riga di comando in Python che converte le esportazioni delle chat WhatsApp in file HTML formattati.

## Caratteristiche

- Converte le esportazioni delle chat WhatsApp (.txt) in formato HTML
- Mantiene la formattazione della chat e i timestamp
- Raggruppa i messaggi per data
- Supporta allineamenti diversi per i messaggi in base al mittente
- Gestisce correttamente i messaggi di sistema e le date in formato italiano

## Utilizzo

Prima esporta la chat come testo da WhatsApp, poi copiala sul computer ed esegui:

```bash
python whatsapp_to_html.py nome_chat.txt
```

Ti sarà chiesto il tuo nome per allineare a destra i tuoi messaggi.

L'output verrà salvato come `nome_chat.html` nella stessa cartella del file di input.

## Requisiti

- Python 3.6 o superiore

## Licenza

Questo progetto è rilasciato sotto licenza GNU General Public License v3.0 - vedi il file [LICENSE](LICENSE) per i dettagli.
