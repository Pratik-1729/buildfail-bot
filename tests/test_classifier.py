from bot.classifier import FailureClassifier


def test_classifies_test_failure():
    logs = """
    =========================== short test summary info ============================
    FAILED tests/test_sample.py::test_something - AssertionError: expected 1 == 2
    """
    clf = FailureClassifier()
    results = clf.classify(logs)
    categories = [r.category for r in results]
    assert "test-failure" in categories


def test_classifies_dependency_error():
    logs = """
    Traceback (most recent call last):
      File "main.py", line 1, in <module>
        import non_existent
    ModuleNotFoundError: No module named 'non_existent'
    """
    clf = FailureClassifier()
    results = clf.classify(logs)
    categories = [r.category for r in results]
    assert "dependency-error" in categories
    # test comment
  