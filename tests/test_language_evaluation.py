from LanguageEvaluation.language_evaluator import LanguageEvaluator, SupportedLanguages


def test_general_evaluation():
    evaluator = LanguageEvaluator(SupportedLanguages.english)
    entry = "...And I told him: 'Don't mess with me. I'll kick your butt!'"
    tokens = evaluator.tokenize_entry(entry)
    assert tokens == ['and', 'I', 'tell', 'he', 'do', 'not', 'mess', 'with', 'will', 'kick', 'your', 'butt']


def test_contraction_evaluation():
    evaluator = LanguageEvaluator(SupportedLanguages.english)
    entry = "Don't won't can't isn't I'll they'll"
    tokens = evaluator.tokenize_entry(entry)
    assert tokens == ['do', 'not', 'will', 'can', 'be', 'I', 'they']


def test_pronoun_evaluation():
    evaluator = LanguageEvaluator(SupportedLanguages.english)
    entry = "he him me we she they us them I"
    tokens = evaluator.tokenize_entry(entry)
    assert tokens == ['he', 'I', 'we', 'she', 'they']


def test_natural_language_evaluation():
    evaluator = LanguageEvaluator(SupportedLanguages.english)
    entry = "Let's eat at the high-society Big Boy Diner; it's where the New York Giants ate after their last victory."
    tokens = evaluator.tokenize_entry(entry)
    assert tokens == [
        'let', 'us', 'eat', 'at', 'the', 'high', 'society', 'Big', 'boy', 'Diner',
        'it', 'be', 'where', 'after', 'their', 'last', 'victory'
    ]
