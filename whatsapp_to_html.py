import re
import sys
from datetime import datetime
from pathlib import Path

def parse_whatsapp_chat(file_path):
    """
    Analizza il file di esportazione della chat WhatsApp e restituisce i messaggi come lista di dizionari.
    Supporta il formato data italiano (GG/MM/AAAA) e gestisce i messaggi su più righe.
    """
    print(f"Analisi del file: {file_path}")
    messages = []
    current_message = None
    line_count = 0
    matched_lines = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        print(f"Lettura di {len(lines)} righe dal file")
        
        # Nomi dei mesi in italiano per la formattazione delle date
        month_names = [
            'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
            'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'
        ]
        
        # Formati dei messaggi WhatsApp supportati:
        # - Nuovo formato: "GG/MM/AAAA, OO:MM - Nome: Messaggio"
        # - Vecchio formato: "GG/MM/AA, OO:MM - Nome: Messaggio"
        message_pattern = re.compile(r'^(\d{2}/\d{2}/(?:\d{2}|\d{4}), \d{2}:\d{2}) - ([^:]+): (.*)')
        action_pattern = re.compile(r'^(\d{2}/\d{2}/(?:\d{2}|\d{4}), \d{2}:\d{2}) - (.*)')
        
        current_date = None
        
        for line in lines:
            line_count += 1
            line = line.strip()
            if not line:
                continue
                
            # Prova a trovare un messaggio standard
            match = message_pattern.match(line)
            if match:
                matched_lines += 1
                # Se c'è un messaggio precedente, aggiungilo alla lista
                if current_message:
                    messages.append(current_message)
                
                timestamp_str, sender, content = match.groups()
                try:
                    # Prova entrambi i formati di data
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %H:%M")
                    except ValueError:
                        timestamp = datetime.strptime(timestamp_str, "%d/%m/%y, %H:%M")
                    
                    # Aggiungi l'intestazione della data se è un nuovo giorno
                    if current_date != timestamp.date():
                        current_date = timestamp.date()
                        month_name = month_names[timestamp.month - 1]
                        messages.append({
                            'type': 'date_header',
                            'date': f"{timestamp.day} {month_name} {timestamp.year}"
                        })
                    
                    # Crea un nuovo oggetto messaggio
                    current_message = {
                        'type': 'message',
                        'timestamp': timestamp,
                        'sender': sender.strip(),
                        'content': content.strip()
                    }
                except ValueError as e:
                    print(f"Errore nel parsing della data alla riga {line_count}: {line}")
                    continue
                    
            # Prova a trovare un'azione di sistema (come "X ha creato il gruppo")
            elif ' - ' in line and ':' not in line.split(' - ')[1]:
                action_match = action_pattern.match(line)
                if action_match:
                    matched_lines += 1
                    timestamp_str, action = action_match.groups()
                    try:
                        # Prova entrambi i formati di data
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%d/%m/%Y, %H:%M")
                        except ValueError:
                            timestamp = datetime.strptime(timestamp_str, "%d/%m/%y, %H:%M")
                        
                        if current_date != timestamp.date():
                            current_date = timestamp.date()
                            month_name = month_names[timestamp.month - 1]
                            messages.append({
                                'type': 'date_header',
                                'date': f"{timestamp.day} {month_name} {timestamp.year}"
                            })
                        
                        current_message = {
                            'type': 'system',
                            'timestamp': timestamp,
                            'content': action.strip()
                        }
                    except ValueError as e:
                        print(f"Errore nel parsing della data del messaggio di sistema alla riga {line_count}: {line}")
                        continue
            
            # Se la riga non inizia con un timestamp, è la continuazione del messaggio precedente
            elif current_message and current_message['type'] == 'message':
                current_message['content'] += '\n' + line.strip()
            else:
                print(f"Riga {line_count} non corrisponde a nessun pattern: {line[:50]}...")
        
        # Aggiungi l'ultimo messaggio se esiste
        if current_message:
            messages.append(current_message)
            
        print(f"Analisi completata: {len(messages)} messaggi elaborati da {matched_lines} righe corrispondenti")
        return messages
        
    except Exception as e:
        print(f"Errore nella lettura del file: {e}")
        return []

def generate_html(messaggi, file_uscita, nome_utente=None):
    """
    Genera un file HTML a partire dai messaggi analizzati con lo stile appropriato.
    
    Args:
        messaggi: Lista di dizionari contenenti i messaggi
        file_uscita: Percorso del file HTML da generare
        nome_utente: Nome dell'utente (i cui messaggi verranno allineati a destra)
    """
    # Stili CSS per la chat
    css = """
    <style>
    /* Stili generali */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background-color: #e5ddd5;
        color: #111b21;
        line-height: 1.5;
    }
    /* Contenitore della chat */
    .chat-container {
        background-color: #e5ddd5;
        padding: 10px;
        box-sizing: border-box;
    }
    /* Intestazione data */
    .date-header {
        text-align: center;
        color: #54656f;
        font-size: 0.85em;
        margin: 20px auto;
        padding: 8px 16px;
        background-color: #e1f7cb;
        border-radius: 15px;
        display: inline-block;
        max-width: 85%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        font-weight: 500;
    }
    /* Stile base messaggio */
    .messaggio {
        margin: 8px 0;
        padding: 8px 12px;
        border-radius: 7.5px;
        max-width: 85%;
        position: relative;
        word-wrap: break-word;
        line-height: 1.5;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.1);
    }
    /* Messaggi ricevuti */
    .messaggio.sinistra {
        background-color: white;
        margin-right: auto;
        margin-left: 5px;
        border-top-left-radius: 0;
    }
    /* Messaggi inviati */
    .messaggio.destra {
        background-color: #d9fdd3;
        margin-left: auto;
        margin-right: 5px;
        border-top-right-radius: 0;
    }
    /* Messaggi di sistema */
    .messaggio.system {
        background-color: #e1f7cb;
        margin: 15px auto;
        text-align: center;
        font-size: 0.85em;
        color: #54656f;
        max-width: 90%;
        padding: 8px 12px;
        border-radius: 15px;
        font-style: italic;
    }
    /* Stile mittente */
    .mittente {
        font-weight: 600;
        margin-bottom: 4px;
        font-size: 0.9em;
        color: #1b3c4d;
    }
    .destra .mittente {
        text-align: right;
    }
    /* Stile orario */
    .orario {
        color: #667781;
        font-size: 0.7em;
        margin-top: 4px;
        text-align: right;
    }
    /* Contenuto del messaggio */
    .contenuto {
        margin: 5px 0 3px 0;
        white-space: pre-line;
        font-size: 0.95em;
        line-height: 1.5;
    }
    .system .message-content {
        text-align: center;
    }
    a {
        color: #128c7e;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """
    
    # Estrai il titolo della chat dal nome del file
    titolo_chat = Path(file_uscita).stem.replace('Chat WhatsApp con', 'Chat con')
    
    # Genera l'intestazione HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titolo_chat}</title>
        {css}
    </head>
    <body>
        <div class="chat-container">
    """
    
    # Aggiungi ogni messaggio al contenuto HTML
    for messaggio in messaggi:
        if messaggio['type'] == 'date_header':
            html_content += f"<div class='date-header'>{messaggio['date']}</div>"
        elif messaggio['type'] == 'system':
            html_content += f"""
            <div class="messaggio system">
                <div class="contenuto">{messaggio['content']}</div>
            </div>
            """
        else:
            # Allinea a destra i messaggi dell'utente corrente
            allineamento = 'destra' if nome_utente and nome_utente.lower() in messaggio['sender'].lower() else 'sinistra'
            
            html_content += f"""
            <div class="messaggio {allineamento}">
                <div class="mittente">{messaggio['sender']}</div>
                <div class="contenuto">{messaggio['content']}</div>
                <div class="orario">
                    {messaggio['timestamp'].strftime('%H:%M')}
                </div>
            </div>
            """
    
    # Chiudi i tag HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Scrivi il file di output
    with open(file_uscita, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) != 2:
        print("Utilizzo: python whatsapp_to_html.py <file_input.txt>")
        print("Esempio: python whatsapp_to_html.py 'Chat WhatsApp.txt'")
        sys.exit(1)
    
    # Chiedi all'utente il suo nome per determinare l'allineamento
    nome_utente = input("Inserisci il tuo nome come appare nella chat (per allineare i tuoi messaggi a destra): ").strip()
    
    input_file = sys.argv[1]
    output_file = str(Path(input_file).with_suffix('.html'))
    
    if not Path(input_file).exists():
        print(f"Errore: Il file '{input_file}' non esiste")
        sys.exit(1)
    
    print(f"Elaborazione della chat WhatsApp da: {input_file}")
    messages = parse_whatsapp_chat(input_file)
    generate_html(messages, output_file, nome_utente)
    print(f"File HTML generato con successo: {output_file}")
    print("Puoi aprirlo con il tuo browser preferito per visualizzare la chat.")

if __name__ == "__main__":
    main()
