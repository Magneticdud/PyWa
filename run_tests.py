#!/usr/bin/env python3
"""
Esegui tutti i test del progetto.
"""
import unittest
import sys

def run_tests():
    """Esegui tutti i test."""
    # Trova tutti i test nella cartella tests
    test_suite = unittest.defaultTestLoader.discover('tests')
    
    # Esegui i test
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Restituisci un codice di uscita appropriato
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
