import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
import random

# Dataset d'entraînement (phrases + étiquette)
train_data = [
    # SALUTATIONS (exemples variés)
    ("bonjour", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salut", {"cats": {"SALUTATION": True, "NON": False}}),
    ("coucou", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonsoir", {"cats": {"SALUTATION": True, "NON": False}}),
    ("hey", {"cats": {"SALUTATION": True, "NON": False}}),
    ("hello", {"cats": {"SALUTATION": True, "NON": False}}),
    ("yo", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salutations", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salut tout le monde", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonjour à tous", {"cats": {"SALUTATION": True, "NON": False}}),
    ("hello tout le monde", {"cats": {"SALUTATION": True, "NON": False}}),
    ("coucou tout le monde", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bon matin", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonne journée", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonne soirée", {"cats": {"SALUTATION": True, "NON": False}}),
    ("hey salut", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salut salut", {"cats": {"SALUTATION": True, "NON": False}}),
    ("hello hello", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonjour monsieur", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonjour madame", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salutations cordiales", {"cats": {"SALUTATION": True, "NON": False}}),
    ("salut ça va ?", {"cats": {"SALUTATION": True, "NON": False}}),
    ("bonjour comment ça va ?", {"cats": {"SALUTATION": True, "NON": False}}),

    # NON SALUTATIONS (exemples de phrases neutres ou autres)
    ("comment ça va ?", {"cats": {"SALUTATION": False, "NON": True}}),
    ("quels sont vos horaires ?", {"cats": {"SALUTATION": False, "NON": True}}),
    ("je voudrais un rendez-vous", {"cats": {"SALUTATION": False, "NON": True}}),
    ("où est la salle de réunion ?", {"cats": {"SALUTATION": False, "NON": True}}),
    ("pouvez-vous m'aider ?", {"cats": {"SALUTATION": False, "NON": True}}),
    ("merci beaucoup", {"cats": {"SALUTATION": False, "NON": True}}),
    ("à plus tard", {"cats": {"SALUTATION": False, "NON": True}}),
    ("bonne chance", {"cats": {"SALUTATION": False, "NON": True}}),
    ("quelle heure est-il ?", {"cats": {"SALUTATION": False, "NON": True}}),
    ("je ne comprends pas", {"cats": {"SALUTATION": False, "NON": True}}),
]

# Créer un modèle vide
nlp = spacy.blank("fr")

# Ajouter le pipe de text categorization
textcat = nlp.add_pipe("textcat")

# Ajouter les labels
textcat.add_label("SALUTATION")
textcat.add_label("NON")

# Entraînement
n_iter = 10
optimizer = nlp.begin_training()

for i in range(n_iter):
    random.shuffle(train_data)
    losses = {}
    batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
    for batch in batches:
        texts, annotations = zip(*batch)
        examples = []
        for text, annotation in zip(texts, annotations):
            doc = nlp.make_doc(text)
            examples.append(Example.from_dict(doc, annotation))
        nlp.update(examples, sgd=optimizer, drop=0.2, losses=losses)
    print(f"Iteration {i+1}, Losses: {losses}")

# Après la boucle d'entraînement
output_dir = "./mon_modele_salutation"  # dossier où enregistrer le modèle
nlp.to_disk(output_dir)
print(f"Modèle sauvegardé dans {output_dir}")

