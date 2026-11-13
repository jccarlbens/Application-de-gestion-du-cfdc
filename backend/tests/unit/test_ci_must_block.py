# Test VOLONTAIREMENT FAUX (définition du terminé de US-001) : il prouve que la
# CI bloque une pull request dont un test échoue. Il est retiré juste après.
def test_ci_blocks_a_failing_test() -> None:
    assert 1 + 1 == 3, "échec volontaire : la CI doit bloquer cette pull request"
