import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity





# Load dataset
df = pd.read_csv("indian_movies_2000_2025.csv")

# Basic cleanup
df["tags"] = df["tags"].fillna("")
df["overview"] = df["overview"].fillna("")
df["year"] = pd.to_numeric(df["year"], errors="coerce")





OCCASION_RULES = {
    "Just watching a movie": {
        "exclude_tags": []
    },
    "Movie date": {
        "exclude_tags": ["Horror", "Extreme", "Violence"]
    },
    "Family movie time": {
        "exclude_tags": ["Violence", "Adult", "Dark", "Crime"]
    },
    "Friends movie time": {
        "exclude_tags": []
    },
    "Binge watch": {
        "exclude_tags": []
    },
    "Solo watch": {
        "exclude_tags": []
    }
}





GENRE_MAP = {
    "Action": ["Action", "Action Epic"],
    "Thriller": ["Thriller", "Political Thriller", "Spy"],
    "Drama": ["Drama", "Political Drama"],
    "Crime": ["Crime", "Gangster"],
    "Romance": ["Romance"],
    "Comedy": ["Comedy", "Satire"],
    "Adventure": ["Adventure"],
    "Horror": ["Horror"],
    "Mystery": ["Mystery"],
    "Biography / True Story": ["Based on true events"],
    "Political": ["Political"],
    "Social / Realistic": ["Social issues"],
    "Experimental / Indie": ["Experimental"],
    "Feel-good": ["Inspirational", "Feel-Good"]
}





MOOD_MAP = {
    "Feel-good": ["Comedy", "Inspirational", "Feel-Good"],
    "Light & fun": ["Comedy", "Romance"],
    "Emotional": ["Drama", "Romantic Drama"],
    "Intense": ["Thriller", "Action", "Crime"],
    "Dark": ["Crime", "Psychological", "Thriller"],
    "Thought-provoking": ["Political", "Social issues"],
    "Inspiring": ["Inspirational", "Based on true events"]
}





df["text"] = df["overview"] + " " + df["tags"]





vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

tfidf_matrix = vectorizer.fit_transform(df["text"])





def apply_recency_filter(data, recency):
    if recency == "Latest":
        return data[data["year"] >= (data["year"].max() - 5)]
    elif recency == "Modern":
        return data[data["year"] >= (data["year"].max() - 10)]
    return data





def apply_occasion_filter(data, occasion):
    rules = OCCASION_RULES.get(occasion, {})
    exclude = rules.get("exclude_tags", [])

    if not exclude:
        return data

    mask = ~data["tags"].str.contains("|".join(exclude), case=False)
    return data[mask]





def apply_genre_filter(data, selected_genres):
    if not selected_genres:
        return data

    genre_tags = []
    for g in selected_genres:
        genre_tags.extend(GENRE_MAP.get(g, []))

    mask = data["tags"].str.contains("|".join(genre_tags), case=False)
    return data[mask]





def build_user_query(genres, interests, mood):
    query = []

    for g in genres:
        query.append(g)

    for i in interests:
        query.append(i)

    if mood:
        query.extend(MOOD_MAP.get(mood, []))

    return " ".join(query)





def recommend_movies(
    occasion,
    genres,
    interests,
    mood,
    recency,
    top_n=10
):
    filtered = df.copy()

    # 1. Hard filters
    filtered = apply_occasion_filter(filtered, occasion)
    filtered = apply_genre_filter(filtered, genres)
    filtered = apply_recency_filter(filtered, recency)

    if filtered.empty:
        return pd.DataFrame()

    # 2. Build user query
    user_query = build_user_query(genres, interests, mood)
    user_vec = vectorizer.transform([user_query])

    # 3. Similarity
    filtered_idx = filtered.index
    similarity = cosine_similarity(
        user_vec,
        tfidf_matrix[filtered_idx]
    )[0]

    filtered = filtered.copy()
    filtered["score"] = similarity

    # 4. Rank & return
    return (
        filtered
        .sort_values("score", ascending=False)
        .head(top_n)[
            ["movie_name", "year", "tags", "overview", "score"]
        ]
    )





results = recommend_movies(
    occasion="Solo watch",
    genres=["Thriller", "crime","Horror"],
    interests=["Intense", "Dark"],
    mood="Dark",
    recency="modern",
    top_n=10
)

print(results)