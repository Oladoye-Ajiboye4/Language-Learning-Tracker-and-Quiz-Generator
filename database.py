'''
This creates a simple database using JSON file to store user's details. So that the user will not have to restart everything when the program js loaded
'''
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class UserDatabase:
    def __init__(self, db_file: str = "user_db.json"):
        self.db_file = db_file
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        # Create database file if it doesn't exist.
        if not os.path.exists(self.db_file):
            initial_data = {
                "users": {},
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self._write_db(initial_data)

    def _read_db(self) -> Dict:
        # Read entire database.
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "users": {}, "metadata": {}}

    def _write_db(self, data: Dict):
        # Write entire database.
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_user(self, username: str, initial_level: str = "Beginner"):
        # Create a new user.
        db = self._read_db()

        if username in db["users"]:
            return False  
        # creates JSON table to store data
        db["users"][username] = {
            "username": username,
            "level": initial_level,
            "words_learned": {},  
            "words_mastered": [],
            "difficult_words": [],
            "retention_rate": 0,
            "total_score": 0,
            "total_questions": 0,
            "overall_accuracy": 0,
            "created": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }

        self._write_db(db)
        return True

    def get_user(self, username: str) -> Optional[Dict]:
        # Get user data.
        db = self._read_db()
        return db["users"].get(username)

    def update_user_progress(self, username: str, score: int, total_questions: int, correct_words: list,
                             words_tested: List[str], words_mastered: List[str] = None):
        db = self._read_db()

        if username not in db["users"]:
            return False

        user = db["users"][username]
        user["total_score"] += score
        user["total_questions"] += total_questions
        user["last_active"] = datetime.now().isoformat()

        # Update the word learned with dictionary data type
        if words_tested:
            for word in words_tested:
                if word not in user["words_learned"]:
                    user["words_learned"][word] = {
                        'question_freq': 0,
                        'answered_correctly': 0
                    }

                # Get the dictionary for this word's data
                word_data = user["words_learned"][word]

                # Increment the count of times this word was presented
                word_data['question_freq'] += 1
                word_data['answered_correctly'] += 1

                # Calculate and update the perfection ratio
                if (word_data['question_freq'] > 0) and ('perfection' in word_data):
                    new_perfection = word_data['answered_correctly'] / word_data['question_freq']
                    word_data['perfection'] = (word_data['perfection'] + new_perfection) / 2
                    word_data['perfection'] = round(word_data['perfection'], 2)
                else:
                    word_data['perfection'] = 0.0
                # Determine and update word mastered
                if (word not in user["words_mastered"]) and (word_data['question_freq'] >= 5) and (word_data['perfection'] > 0.89):
                    words_mastered = user["words_mastered"].append(word)
            

                # Determine difficult words
                if (word not in user.get('difficult_words', [])) and (word_data.get('question_freq', -1) > 4) and (word_data.get('perfection', 1.0) < 0.4):
                    # Check if difficult_words list exists and is a list
                    if not isinstance(user.get('difficult_words'), list):
                        print(f"DEBUG: ERROR - user['difficult_words'] is not a list! It is {type(user.get('difficult_words'))}")
                        user['difficult_words'] = []
                
                    hard_words = user['difficult_words'].append(word)
                elif (word in user.get('difficult_words', [])) and (word_data.get('question_freq', -1) > 4) and (word_data.get('perfection', -1) > 0.6):
                    # Check if difficult_words list exists and is a list
                    if isinstance(user.get('difficult_words'), list):
                        try:
                            user['difficult_words'].remove(word)
                            print(f"DEBUG: Removed '{word}' from difficult_words.")
                        except ValueError:
                            print(f"DEBUG: WARNING - '{word}' not found in difficult_words list during removal attempt.")
                    else:
                        print(f"DEBUG: ERROR - Cannot remove from user['difficult_words'], it's not a list! It is {type(user.get('difficult_words'))}")

        # Add new words to mastered list (avoid duplicates)
        if words_mastered:
            currently_mastered = set(user["words_mastered"])
            currently_mastered.update(words_mastered)
            user["words_mastered"] = list(currently_mastered)

        # Calculate Word Mastery Retention Rate
        learned_count = len(user.get("words_learned", {}))
        mastered_count = len(user.get("words_mastered", []))
        # Calculate retention rate, handling division by zero
        if learned_count > 0:
            retention_rate = (mastered_count / learned_count) * 100
            user["retention_rate"] = round(retention_rate, 2)
        else:
            user["retention_rate"] = 0.0

        # Calculates overall accuracy of the user
        overall_accuracy = (user["total_score"] / user["total_questions"]) * 100 if user["total_questions"] > 0 else 0
        user['overall_accuracy'] = round(overall_accuracy, 2)

        # Update level based on performance (simple algorithm)
        if user["total_questions"] > 0:
            accuracy = user["total_score"] / user["total_questions"]
            if accuracy >= 0.9:
                user["level"] = "Advanced"
            elif accuracy >= 0.7:
                user["level"] = "Intermediate"
            else:
                user["level"] = "Beginner"

        self._write_db(db)
        return True

    def get_user_stats(self, username: str) -> Dict:
        # Get comprehensive user statistics.
        user = self.get_user(username)
        if not user:
            return {}

        # Calculates number of words learned and encountered
        words_learned_count = len(user.get("words_learned", {}))
        total_word_encounters = sum(
            word_data.get('frequency', 0) for word_data in user.get("words_learned", {}).values()
        )

        stats = {
            "username": user["username"],
            "current_level": user["level"],
            "words_learned": user["words_learned"],
            "words_learned_count": words_learned_count,  
            "total_word_encounters": total_word_encounters, 
            "words_mastered_count": len(user["words_mastered"]),
            "words_mastered": user["words_mastered"],
            "difficult_words": user["difficult_words"],
            "retention_rate": user["retention_rate"],
            "total_score": user["total_score"],
            "total_questions": user["total_questions"],
            "overall_accuracy":  user["overall_accuracy"]
        }

        return stats

    
# Global database instance
db = UserDatabase()
