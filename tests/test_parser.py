import unittest
import os
import sys
from datetime import datetime

# Aggiungi la directory principale al path per importare il modulo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from whatsapp_to_html import parse_whatsapp_chat

class TestWhatsAppParser(unittest.TestCase):
    def setUp(self):
        # Crea un file di test temporaneo
        self.test_file = "test_chat.txt"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("""09/04/24, 17:50 - Luca: Ciao a tutti!
09/04/24, 17:51 - Marco: Ciao Luca, come stai?
09/04/24, 17:52 - Luca: Tutto bene, grazie! E tu?
""")
    
    def tearDown(self):
        # Rimuovi il file di test dopo i test
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_parse_messages(self):
        """Testa il parsing dei messaggi standard"""
        messages = parse_whatsapp_chat(self.test_file)
        # Ci aspettiamo 4 elementi: 1 data + 3 messaggi
        self.assertEqual(len(messages), 4)
        
        # Verifica il primo messaggio (dopo l'intestazione della data)
        self.assertEqual(messages[1]['type'], 'message')
        self.assertEqual(messages[1]['sender'], 'Luca')
        self.assertEqual(messages[1]['content'], 'Ciao a tutti!')
        self.assertIsInstance(messages[1]['timestamp'], datetime)
        
    def test_system_message(self):
        """Testa il parsing dei messaggi di sistema"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("09/04/24, 17:50 - ‎Luca ha creato il gruppo")
        
        messages = parse_whatsapp_chat(self.test_file)
        # Il primo elemento è l'intestazione della data, il secondo è il messaggio di sistema
        self.assertEqual(messages[1]['type'], 'system')
        self.assertIn('ha creato il gruppo', messages[1]['content'])
    
    def test_multiline_message(self):
        """Testa i messaggi su più righe"""
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("09/04/24, 17:50 - Luca: Riga 1\nRiga 2\nRiga 3")
        
        messages = parse_whatsapp_chat(self.test_file)
        # Il primo elemento è l'intestazione della data, il secondo è il messaggio
        self.assertEqual(messages[1]['content'], 'Riga 1\nRiga 2\nRiga 3')

if __name__ == '__main__':
    unittest.main()
