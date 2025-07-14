import json
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

# === Chargement du modèle de classification (entraîné par toi) ===
classifier = pipeline(
    "text-classification",
    model="D:/Soutenance MOIS 9/env/intent_classifier_model",
    tokenizer="D:/Soutenance MOIS 9/env/intent_classifier_model"
)

# === Chargement du modèle d'embedding sémantique ===
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# === Chemins des fichiers JSON ===
faq_augmented_path = r"D:\Soutenance MOIS 9\env\faq_augmented.json"
faq_sfr_complet_path = r"D:\Soutenance MOIS 9\env\faq_sfr_complet.json"

with open(faq_augmented_path, 'r', encoding='utf-8') as f:
    faq_augmented = json.load(f)

with open(faq_sfr_complet_path, 'r', encoding='utf-8') as f:
    faq_sfr_complet = json.load(f)

# === Recherche sémantique dans une liste de questions ===
def find_best_match_semantic(question, faqs):
    questions_list = [item['question'] for item in faqs]
    question_embedding = embedder.encode(question, convert_to_tensor=True)
    faq_embeddings = embedder.encode(questions_list, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(question_embedding, faq_embeddings)[0]

    best_idx = cosine_scores.argmax().item()
    best_score = cosine_scores[best_idx].item()

    if best_score > 0.6:  # seuil de confiance ajustable
        return faqs[best_idx]['réponse']
    return None

# === Trouver la réponse dans les fichiers JSON ===
def get_answer(label, question):
    for source in [faq_augmented, faq_sfr_complet]:
        answers = source.get(label)
        if answers:
            if isinstance(answers, list):
                res = find_best_match_semantic(question, answers)
                if res:
                    return res
                else:
                    return answers[0].get('réponse', "Pas de réponse disponible.")
            elif isinstance(answers, str):
                return answers
    return None

# === Boucle principale ===
def main():
    print("Pose ta question (tape 'exit' pour quitter).")
    while True:
        question = input("> ").strip()
        if question.lower() == 'exit':
            print("Au revoir !")
            break

        result = classifier(question)
        best_label = result[0]['label']
        score = result[0]['score']
        print(f"Catégorie prédite : {best_label} (confiance {score:.2f})")

        answer = get_answer(best_label, question)
        if answer:
            print(f"Réponse : {answer}")
        else:
            print("❌ Désolé, je n'ai pas trouvé de réponse pour cette question.")

if __name__ == "__main__":
    main()
