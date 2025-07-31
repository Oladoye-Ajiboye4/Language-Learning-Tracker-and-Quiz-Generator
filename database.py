import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class UserDatabase:
    def __init__(self, db_file: str = "user_db.json"):
        self.db_file = db_file
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        if not os.path.exists(self.db_file):
            initial_data = {
                "users": {},
                "sessions": [],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            self._write_db(initial_data)

    def _read_db(self) -> Dict:
        """Read entire database."""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "users": {}, "sessions": [], "metadata": {}}

    def _write_db(self, data: Dict):
        """Write entire database."""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_user(self, username: str, initial_level: str = "Beginner") -> bool:
        """Create a new user."""
        db = self._read_db()

        if username in db["users"]:
            return False  # User already exists

        db["users"][username] = {
            "username": username,
            "level": initial_level,
            # Changed structure to track frequency
            "words_learned": {},  # word -> {'frequency': int}
            "words_mastered": [],
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
        """Get user data."""
        db = self._read_db()
        return db["users"].get(username)

    def update_user_progress(self, username: str, score: int, total_questions: int, correct_words: list,
                             words_tested: List[str], words_mastered: List[str] = None):
        """Update user progress after a session."""
        db = self._read_db()

        if username not in db["users"]:
            return False

        user = db["users"][username]
        user["total_score"] += score
        user["total_questions"] += total_questions
        user["last_active"] = datetime.now().isoformat()

        if words_tested: # This is the list of tested words
            for word in words_tested:
                # Ensure the word has an entry in user["words_learned"]
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
                # Handle potential division by zero
                if (word_data['question_freq'] > 0) and ('perfection' in word_data):
                    new_perfection = word_data['answered_correctly'] / word_data['question_freq']
                    word_data['perfection'] = (word_data['perfection'] + new_perfection) / 2
                    word_data['perfection'] = round(word_data['perfection'], 2)
                else:
                    word_data['perfection'] = 0.0
                if (word not in user["words_mastered"]) and (word_data['question_freq'] >= 5) and (word_data['perfection'] > 0.89):
                    words_mastered = user["words_mastered"].append(word)
                else:
                    continue
        # Add new words to mastered list (avoid duplicates)
        if words_mastered:
            currently_mastered = set(user["words_mastered"])
            currently_mastered.update(words_mastered)
            user["words_mastered"] = list(currently_mastered)
            
        # Inside update_user_progress method, after updating words_learned and words_mastered

        # Calculate Word Mastery Retention Rate
        learned_count = len(user.get("words_learned", {})) 
        mastered_count = len(user.get("words_mastered", [])) 
        # Calculate retention rate, handling division by zero
        if learned_count > 0:
            retention_rate = (mastered_count / learned_count) * 100
            user["retention_rate"] = round(retention_rate, 2) 
        else:
            # Define behavior when no words are learned yet.
            user["retention_rate"] = 0.0 # or 

        # This is essentially your existing 'overall_accuracy' in get_user_stats.
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

    def log_session(self, username: str, score: int, total_questions: int,
                    words_tested: List[str], session_duration: float = 0):
        """Log a quiz session."""
        db = self._read_db()

        session_data = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "score": score,
            "total_questions": total_questions,
            "accuracy": score / total_questions if total_questions > 0 else 0,
            "words_tested": words_tested,
            "session_duration": session_duration
        }

        db["sessions"].append(session_data)
        self._write_db(db)

    def get_user_sessions(self, username: str) -> List[Dict]:
        """Get all sessions for a user."""
        db = self._read_db()
        return [s for s in db["sessions"] if s["username"] == username]

    def get_user_stats(self, username: str) -> Dict:
        """Get comprehensive user statistics."""
        user = self.get_user(username)
        if not user:
            return {}

        sessions = self.get_user_sessions(username)
        # Calculate stats based on the new structure
        words_learned_count = len(user.get("words_learned", {}))
        total_word_encounters = sum(
            word_data.get('frequency', 0) for word_data in user.get("words_learned", {}).values()
        )

        stats = {
            "username": user["username"],
            "current_level": user["level"],
            "words_learned_count": words_learned_count,  # Number of unique words learned
            "total_word_encounters": total_word_encounters,  # Total times any word was encountered
            "words_mastered_count": len(user["words_mastered"]),
            "total_sessions": len(sessions),
            "overall_accuracy": user["total_score"] / user["total_questions"] if user["total_questions"] > 0 else 0,
            "total_questions_answered": user["total_questions"],
            "recent_sessions": sessions[-5:] if sessions else []  # Last 5 sessions
        }

        return stats

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard of top users."""
        db = self._read_db()
        users = []

        for username, user_data in db["users"].items():
            if user_data["total_questions"] > 0:
                accuracy = user_data["total_score"] / user_data["total_questions"]
                users.append({
                    "username": username,
                    "accuracy": accuracy,
                    "total_questions": user_data["total_questions"],
                    "level": user_data["level"]
                })

        # Sort by accuracy (and total questions as tiebreaker)
        users.sort(key=lambda x: (-x["accuracy"], -x["total_questions"]))
        return users[:limit]

    def get_word_encounters(self, username: str, word: str) -> int:
        """Get how many times a user has encountered a word."""
        user = self.get_user(username)
        if not user:
            return 0
        word_data = user.get("words_learned", {}).get(word, {})
        return word_data.get('frequency', 0)

# Global database instance
db = UserDatabase()
