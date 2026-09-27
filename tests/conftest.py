from kestra import Kestra

def pytest_sessionfinish(session, exitstatus):
    """
    Hook appelé automatiquement par pytest à la fin de la session de tests,
    que les tests passent ou échouent (contrairement à un simple print en fin de fichier).
    exitstatus == 0 signifie que tous les tests sont passés.
    """
    test_ok = (exitstatus == 0)
    print()  # force un retour à la ligne pour ne pas coller au "[100%]" de pytest
    Kestra.outputs({"test_ok": test_ok})