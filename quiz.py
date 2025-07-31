from abc import ABC, abstractmethod
import random
import nltk
from nltk.corpus import wordnet
import string
from vocabulary import estimate_word_level
import re
import random
from typing import Dict, List, Optional
from sentence_map import sentence_map 

try:
    _ = wordnet.synsets('test')
except LookupError:
    print("Downloading NLTK WordNet data…")
    nltk.download('wordnet')
    nltk.download('omw-1.4')


class QuestionGenerator(ABC):
    @abstractmethod
    def generate(self, words: list[str], all_words: list[str]) -> list[dict]:
        """
        Given a list of words, return a list of question dicts:
          {
            'prompt': str,
            'choices': list[str] (optional),
            'answer': str
          }
        """
        pass

class DefinitionGenerator(QuestionGenerator):
    def generate(self, words, all_words):
        questions = []
        for w in words:
            syns = wordnet.synsets(w)
            if not syns:
                continue
            correct = syns[0].definition()
            # gather distractors
            defs = [s.definition() for s in syns[1:]]
            if len(defs) < 3:
                continue
            
            distractors = random.sample(defs, k=min(3, len(defs)))
            choices = distractors + [correct]
            if len(choices) != 4:
                continue
            random.shuffle(choices)
            questions.append({
                'word': w,
                'level': estimate_word_level(w),
                'prompt': f"Which best defines “{w}”?",
                'choices': choices,
                'answer': correct
            })
        return questions


def clean_synonyms(raw_syns, word):
    clean = set()
    for s in raw_syns:
        # normalize
        s_norm = s.lower().replace('_',' ')
        # skip anything that isn’t a single word or equals the target
        if ' ' in s_norm or s_norm == word.lower():
            continue
        # skip proper-case leftovers
        if not s_norm.isalpha():
            continue
        clean.add(s_norm)
    return list(clean)


class SynonymGenerator(QuestionGenerator):
    def __init__(self, num_choices=4, custom_syns=None):
        self.num_choices = num_choices
        self.custom_syns = custom_syns or {}

    def generate(self, words, all_words):
        questions = []

        for w in words:
            # 1) Gather raw synonyms from custom map + WordNet
            raw = set(self.custom_syns.get(w, []))
            raw |= {
                lemma.name().replace('_', ' ')  # Replace underscores with spaces
                for syn in wordnet.synsets(w)
                for lemma in syn.lemmas()
            }
            raw.discard(w)

            # 2) Clean them
            syns = clean_synonyms(raw, w)

            # 3) Decide correct answer and distractors
            if syns:
                correct = random.choice(syns)
                pool = [x for x in all_words if x not in syns and x != w]
                prompt = f"Which of these is a synonym of “{w}”?"
            else:
                # If no synonyms, fallback to similarity (use all other words)
                pool = [x for x in all_words if x != w]
                correct = random.choice(pool)
                prompt = f"Which word is most similar to “{w}”?"

            # Ensure enough distractors
            num_distractors = min(self.num_choices - 1, len(pool))
            if num_distractors < 1:
                continue  # Not enough choices to form a question

            distractors = random.sample(pool, k=num_distractors)
            choices = distractors + [correct]
            random.shuffle(choices)
            if len(choices) < 2:
                continue
            questions.append({
                'word': w,
                'level': estimate_word_level(w),
                'prompt': prompt,
                'choices': choices,
                'answer': correct
            })

        return questions
        
class FillBlankGenerator(QuestionGenerator):
    def __init__(self, sentence_map: dict[str, list[str]], num_choices: int = 4):
        self.sentence_map = sentence_map
        self.num_choices = num_choices

    def _replace_word_with_blank(self, sentence: str, word: str) -> str:
        """Replace all occurrences of a word in a sentence with blanks."""
        import re
        escaped_word = re.escape(word.lower())
        pattern = r'\b' + escaped_word + r'\b'
        
        def replace_func(match):
            return '___'
        
        result = re.sub(pattern, replace_func, sentence, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', result).strip()

    def _validate_sentence(self, sentence: str, word: str) -> bool:
        """Validate that a sentence is suitable for fill-in-the-blank."""
        import re
        # Check for empty inputs
        if not sentence or not word:
            return False
        # Check if word exists in sentence (case-insensitive)
        if not re.search(r'\b' + re.escape(word.lower()) + r'\b', sentence.lower()):
            return False
        # Check sentence length
        if len(sentence) > 200:
            return False
        # Check that sentence contains exactly one occurrence of the word
        word_count = len(re.findall(r'\b' + re.escape(word.lower()) + r'\b', sentence.lower()))
        return word_count == 1

    def generate(self, words: list[str], all_words: list[str]) -> list[dict]:
        """Generate context-based fill-in-the-blank questions."""
        questions = []
        
        for w in words:
            # Get sentences for this word
            sentences = self.sentence_map.get(w, [])
            
            # Filter valid sentences
            valid_sentences = []
            for sent in sentences:
                if self._validate_sentence(sent, w):
                    valid_sentences.append(sent)
            
            if not valid_sentences:
                continue
                
            # Choose a random valid sentence
            sentence = random.choice(valid_sentences)
            
            # Create the prompt with blank
            prompt_sentence = self._replace_word_with_blank(sentence, w)
            prompt = f"Which word best fits the sentence: \"{prompt_sentence}\""
            
            # Create choices
            correct = w
            
            # Create distractor pool
            pool = [word for word in all_words if word != w and word.strip()]
            num_distractors = min(self.num_choices - 1, len(pool))
            
            if num_distractors < 1:
                continue
                
            distractors = random.sample(pool, k=num_distractors)
            choices = distractors + [correct]
            random.shuffle(choices)
            
            questions.append({
                'word': w,
                'level': estimate_word_level(w),
                'prompt': prompt,
                'choices': choices,
                'answer': correct
            })
            
        return questions        
        
        
class QuizEngine:
    def __init__(self, generators: list[QuestionGenerator]):
        self.generators = generators
    
    def extract_words(self, words: list[str], user_level: str) -> list[dict]:
        # Bucket the words
        buckets = {"Beginner": [], "Intermediate": [], "Advanced": []}
        for w in words:
            lvl = estimate_word_level(w)
            buckets[lvl].append(w)
    
        # Determine “next level” for sprinkling new words
        order = ["Beginner", "Intermediate", "Advanced"]
        idx = order.index(user_level)
        next_level = order[min(idx + 1, len(order)-1)]
    
        # Sample 8 from user_level, 2 from next_level (or as many as available)
        primary_pool = buckets[user_level]
        secondary_pool = buckets[next_level]
       
        primary_sample = random.sample(primary_pool, min(12, len(primary_pool)))
        secondary_sample = random.sample(secondary_pool, min(6, len(secondary_pool)))
    
        # Combine and shuffle
        selected_words = primary_sample + secondary_sample
        random.shuffle(selected_words)
        return selected_words
        
    def build_questions(self, selected_words: list[str]):    
        # Now generate one question per word (using whichever generator you like)
        quiz_questions = []
        question_counter = 1
        for word in selected_words:
            # pick a generator at random or in sequence
            if question_counter <= 10:
                gen = random.choice(self.generators)
                qs = gen.generate([word], all_words=selected_words)  # most gens take a list of words
                
                if qs:
                    quiz_questions.append(qs[0])  # take the single generated question
                    question_counter += 1
            else:
                break
            
        return quiz_questions

    def user_answer(self, valid_letters=None, allow_text=True):
        """
        Prompt until the user enters either:
          • a single letter in valid_letters (e.g. ['a','b','c','d']), or
          • if allow_text=True, any non-empty text response
        """
        while True:
            ans = input("Your answer: ").strip().lower()

            # 1) Empty?
            if not ans:
                print("Invalid answer: Enter tbe option of the correct answer")
                continue

            # 2) Letter choice?
            if valid_letters and len(ans) == 1 and ans in valid_letters:
                return ans

            # 3) Full-text answer?
            if allow_text and any(ch in string.ascii_lowercase for ch in ans):
                return ans

            # 4) Invalid
            vl = f" ({', '.join(valid_letters)})" if valid_letters else ""
            print(f"Invalid input. Enter a letter{vl} or text answer.")
    
    
    def run(self, questions: list[dict]):
        """
        Run quiz and return (total_score, total_questions, list_of_correct_words, dict_of_word_results).
        
        Returns:
            tuple: (total_score, total_questions, correct_words_list, {word: is_correct})
        """
        score = 0
        word_results = {} # Dictionary to store {word: True/False}
    
        for i, q in enumerate(questions, 1):
            word = q['word'] # Extract the word being tested
            lvl = q.get('level', 'Unknown')
            print(f"\nQ{i} [{lvl}]: {q['prompt']}")
            
            # Setup choices if available
            labels = []
            if 'choices' in q and q['choices'] and len(q['choices']) >= 2:
                # Generate labels a, b, c, … up to the number of choices
                labels = list(string.ascii_lowercase[:len(q['choices'])])
                for label, choice in zip(labels, q['choices']):
                    print(f"  {label}) {choice}")
                valid_inputs = set(labels)
            else:
                valid_inputs = None
    
            ans = self.user_answer(valid_letters=valid_inputs, allow_text=True)
    
            # Determine correctness
            correct = q['answer']
            is_correct = False
    
            if 'choices' in q and labels: # Check if labels exist for MCQ
                # If they typed a letter, map it back to the choice text
                if ans in valid_inputs:
                    chosen_idx = labels.index(ans)
                    if 0 <= chosen_idx < len(q['choices']):
                        chosen = q['choices'][chosen_idx]
                        is_correct = (chosen.lower() == correct.lower())
                # Or if they typed the full text of the answer
                elif ans == correct.lower():
                    is_correct = True
            else:
                # Open-ended: compare text directly
                is_correct = (ans == correct.lower())
    
            # Store the result for this specific word
            word_results[word] = 1 if is_correct== True else 0
    
            if is_correct:
                print("Correct!")
                score += 1
            else:
                print(f"Wrong. Answer: {correct}")
    
        # Create a list of words answered correctly
        correct_words = [word for word, is_correct in word_results.items() if is_correct]
    
        print(f"Final score: {score}/{len(questions)}")
        # Return total score, total questions, list of correct words, and detailed results
        return score, len(questions), correct_words, word_results

    