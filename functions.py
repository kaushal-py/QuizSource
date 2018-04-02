from sklearn.feature_extraction.text import TfidfVectorizer

def calcSimilarity(query, question):
    documents = []
    documents.extend([query, question])
    tfidf = TfidfVectorizer().fit_transform(documents)
    pairwise_similarity = tfidf * tfidf.T
    return pairwise_similarity[0, 1]

# res1 = calcSimilarity("Which elements of a website can a crawler not see?", "What can't a crawler see on a website?")
res2 = calcSimilarity("Would you like an apple or an orange?", "You want to eat an apple or an orange right now?")

print(res2)