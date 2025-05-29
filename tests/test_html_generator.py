import unittest
import os
import sys
import tempfile
from datetime import datetime

# Aggiungi la directory principale al path per importare il modulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from whatsapp_to_html import generate_html

class TestHTMLGenerator(unittest.TestCase):
    def setUp(self):
        # Crea un file di output temporaneo
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, "test_output.html")
        
        # Dati di test
        self.test_messages = [
            {
                'type': 'date_header',
                'date': 'Venerdì 9 aprile 2024'
            },
            {
                'type': 'message',
                'sender': 'Luca',
                'content': 'Ciao a tutti!',
                'timestamp': datetime(2024, 4, 9, 17, 50)
            },
            {
                'type': 'system',
                'content': 'Marco ha aggiunto te',
                'timestamp': datetime(2024, 4, 9, 17, 51)
            }
        ]
    
    def tearDown(self):
        # Pulisci i file temporanei
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_generate_html(self):
        """Testa la generazione del file HTML"""
        # Genera l'HTML
        generate_html(self.test_messages, self.output_file, 'Luca')
        
        # Verifica che il file sia stato creato
        self.assertTrue(os.path.exists(self.output_file))
        
        # Verifica il contenuto del file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verifica che contenga elementi chiave
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('Ciao a tutti!', content)
        self.assertIn('Marco ha aggiunto te', content)
        self.assertIn('Venerdì 9 aprile 2024', content)
        
        # Verifica che i messaggi dell'utente siano allineati a destra
        self.assertIn('class="messaggio destra"', content)
        
    def test_empty_messages(self):
        """Testa la generazione con una lista di messaggi vuota"""
        generate_html([], self.output_file, 'Luca')
        self.assertTrue(os.path.exists(self.output_file))
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('</html>', content)

if __name__ == '__main__':
    unittest.main()
