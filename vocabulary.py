from wordfreq import zipf_frequency

def estimate_user_level(words):
    """
    Estimate language level based on average Zipf frequency.
    Levels roughly:
      • Beginner: avg ≥ 4.0   (common words like “is”, “go”, “come”)
      • Intermediate: 3.0 ≤ avg < 4.0
      • Advanced: avg < 3.0   (rare/technical vocabulary)
    """
    # Compute Zipf frequency for each word
    scores = [zipf_frequency(w, "en") for w in words]
    
    # Remove any words not found in the corpus (freq = 0)
    valid_scores = [s for s in scores if s > 0]
    if not valid_scores:
        return "Unknown (no valid words)"
    
    avg_score = sum(valid_scores) / len(valid_scores)
    
    # Classify
    if avg_score >= 4.0:
        return "Beginner"
    elif avg_score >= 3.0:
        return "Intermediate"
    else:
        return "Advanced"

def estimate_word_level(word):
    score = zipf_frequency(word, "en")  # Zipf ~ 1–7
    if score >= 4.0:
        return "Beginner"
    elif score >= 3.0:
        return "Intermediate"
    else:
        return "Advanced"
