'''main.py manages the app. 
It validates the user inputs, links to the database and brings out results based on the input'''

import file_manager
import vocabulary
from quiz import DefinitionGenerator, QuizEngine, SynonymGenerator, FillBlankGenerator
from sentence_map import sentence_map
import random
from database import db
import re
import sys


def get_username():
    # Define allowed characters: letters (a-z, A-Z), digits (0-9), underscore (_), hyphen (-), space ( )
    allowed_pattern = re.compile(r"^[a-zA-Z0-9_\- ]+$")
    try:
        # Get input from the user
        username = input('Enter your username: ').strip()
        # Check for empty input
        if not username:
            print('Error: Username cannot be blank. Please enter a valid username.')
        # Check for minimum length
        elif len(username) < 3:
            print('Error: Username must be at least 3 characters long. Please try again.')
        # Check for maximum length (optional, but good practice)
        elif len(username) > 50: # Example max length
            print('Error: Username is too long (maximum 50 characters). Please try again.')
        # Check for allowed characters using the regex pattern
        elif not allowed_pattern.match(username):
            invalid_chars = set(char for char in username if not allowed_pattern.match(char))
            print(f"Error: Username contains invalid characters: {', '.join(sorted(invalid_chars))}.")
            print("       Only letters (a-z, A-Z), numbers (0-9), spaces, underscores (_), and hyphens (-) are allowed.")
        else:
            return username
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nOperation cancelled by user.")
        sys.exit()
    except EOFError:
        # Handle Ctrl+D (or end of input stream)
        print("\nNo input received. Exiting.")
        sys.exit()
    except Exception as e:
        # Catch any other unexpected errors during input
        print(f"An unexpected error occurred while reading input: {e}")
        return get_username()
    return get_username()

username = get_username()    
#loads the username from database
if not db.get_user(username):
    print(f'Welcome, {username}!\n\n')
else:
    user_data = db.get_user(username)
    print(f'Welcome back, {username}!\n\n')
    
working_dir = file_manager.file_dir()
print(f"Current directory: {working_dir}")

vocab = file_manager.vocab_data()
level = vocabulary.estimate_user_level(vocab)
if not db.get_user(username):
    db.create_user(username, level)
print(f"\nEstimated user level: {level}")
    
#loads the questions from quiz.py
def run_questions():
    gens = [
            DefinitionGenerator(),
            SynonymGenerator(),
            FillBlankGenerator(sentence_map)  # Pass the sentence_map, not category_templates
        ]
    
    
    engine = QuizEngine(gens)
    extracted_words = engine.extract_words(vocab, level)
    if extracted_words:
        question_builder = engine.build_questions(extracted_words)
        round_score = engine.run(question_builder)
        score = round_score[0]  
        total_questions = round_score[1]
        correct_words = round_score[2]
    
        db.update_user_progress(username, score, total_questions, correct_words, extracted_words)
    else:
        print('Empty document?\nContent not read')

run_questions()
    
def user_stat(username: str):
    """
    Displays user statistics in a formatted table, provides encouragement,
    and offers basic study recommendations.
    """
    stat = db.get_user_stats(username)
    if not stat:
        print(f"User '{username}' not found.")
        return


    words_learned_count = stat.get('words_learned_count', 0)
    words_mastered_count = stat.get('words_mastered_count', 0)
    words_mastered_list = stat.get('words_mastered', [])
    difficult_words_list = stat.get('difficult_words', [])
    # Calculate retention rate dynamically if not stored
    retention_rate = None
    if words_learned_count > 0:
        retention_rate = stat.get('retention_rate')
    overall_accuracy = stat.get('overall_accuracy', 0)
    
    total_questions_answered = stat.get('total_questions', 0)

    #Encouragement Logic
    encouragement = ""
    if overall_accuracy >= 80:
        encouragement = "Outstanding! That's a superb performance!"
    elif overall_accuracy >= 60:
        encouragement = "Great job! You're doing well and improving!"
    elif overall_accuracy >= 40:
        encouragement = "Keep going! You're on the right track!"
    else:
        encouragement = "Don't give up! Practice makes progress!"

    #Study Recommendation Logic
    # Different versions of recommendation
    recommendations_v1 = {
        "low_acc": [
            "• Spend more time reviewing words you've seen before. Consistent review strengthens memory!",
            "• Practice the same words using different quiz types (definitions, synonyms, fill-in-the-blank)."
        ],
        "med_acc": [
            "• Concentrate on solidifying the words you're familiar with. Regular review of 'Mastered Words' is beneficial.",
            "• Push your boundaries a bit by including vocabulary from the next difficulty level."
        ],
        "low_ret": [
            "• Focus your efforts on turning 'learned' words into truly 'mastered' ones. Accuracy with familiar words is key."
        ],
        "low_vol": [
            "• Aim for more frequent study sessions. Building a habit improves long-term learning."
        ],
        "high_gen": [
            "• Keep up the fantastic effort! Explore more complex vocabulary or assist others in their learning.",
            "• Periodically revisit your mastered words to keep them fresh in your memory."
        ]
    }
    recommendations_v2 = {
        "low_acc": [
            "• Prioritize revisiting previously encountered vocabulary. Repetition is crucial for retention!",
            "• Mix up your study methods for known words (try synonyms, definitions, example sentences)."
        ],
        "med_acc": [
            "• Strengthen your grasp on current vocabulary. Regularly check your mastered list for review.",
            "• Introduce a few words from the next level to keep challenging yourself."
        ],
        "low_ret": [
            "• Put effort into mastering the words you recognize. Aiming for accuracy on familiar terms boosts overall retention."
        ],
        "low_vol": [
            "• Increase your study frequency. Consistent practice is vital for moving words into long-term memory."
        ],
        "high_gen": [
            "• Sustain your great progress! Dive into more advanced topics or share your knowledge.",
            "• Don't forget to cycle back to mastered words occasionally to reinforce them."
        ]
    }
    recommendations_v3 = {
        "low_acc": [
            "• Double down on reviewing the vocabulary you've already covered. Frequent exposure helps!",
            "• Vary your question formats for existing words (definitions, synonyms, context-based)."
        ],
        "med_acc": [
            "• Work on fully mastering words you already know. Make your 'Mastered Words' list a review priority.",
            "• Slightly increase the difficulty by practicing some words from the level above."
        ],
        "low_ret": [
            "• Shift focus towards mastering words you've learned. Getting them right consistently is the goal."
        ],
        "low_vol": [
            "• Try to fit in more study sessions. Regularity is a key factor in effective learning."
        ],
        "high_gen": [
            "• Your progress is excellent! Look into advanced material or consider mentoring.",
            "• Reassess your mastered vocabulary from time to time to keep it strong."
        ]
    }

    # Select a random version
    all_versions = [recommendations_v1, recommendations_v2, recommendations_v3]
    selected_version = random.choice(all_versions)

    # Build recommendations using the selected version
    recommendations = []

    if overall_accuracy < 50:
        recommendations.extend(selected_version["low_acc"])
    elif overall_accuracy < 70:
        recommendations.extend(selected_version["med_acc"])

    if retention_rate is not None and retention_rate < 50:
        recommendations.extend(selected_version["low_ret"])

    if total_questions_answered < 50: # Adjusted threshold for example
        recommendations.extend(selected_version["low_vol"])

    # Add general encouragement if no specific issues were flagged
    if not recommendations:
        recommendations.extend(selected_version["high_gen"])

    #Display Formatted Output
    print('\nLoading User Stats from database ......\n')
    print("\n" + "="*50)
    print(f"{encouragement:^50}") # Center the encouragement message
    print("="*50)
    # 2. Statistics Table
    print(f"\n{'User Statistics for:':<25} {username}")
    print("-" * 35)
    print(f"{'Current Level:':<25} {level}")
    print(f"{"Total Questions Answered:":<25} {total_questions_answered}")
    print(f"{'Words Encountered:':<25} {words_learned_count}")
    print(f"{'Words Mastered:':<25} {words_mastered_count}")
    if retention_rate is not None:
        print(f"{'Word Mastery Rate:':<25} {retention_rate:.1f}%") 
    print(f"{'Overall Accuracy:':<25} {overall_accuracy:.1f}%") 
    print("-" * 35)

    # 3. Mastered Words List (if any)
    if words_mastered_list:
        print(f"\nWords You've Mastered ({words_mastered_count}):")
        mastered_str = ", ".join(words_mastered_list)
        # Format the mastered words properly
        if len(mastered_str) > 60:
             # Splits into two lines if too long
             mid = len(mastered_str) // 2
             # Finds a comma near the midpoint to split
             split_point = mastered_str.rfind(',', 0, mid + 10)
             if split_point == -1: split_point = mid 
             print(f"   {mastered_str[:split_point + 1]}")
             print(f"   {mastered_str[split_point + 2:]}")
        else:
            print(f"   {mastered_str}")
    else:
        print("\nWords Mastered: You haven't mastered any word yet. Keep practicing!")

    # 4. Study Recommendations
    print(f"\nStudy Recommendations:")
    if difficult_words_list:
        print(f'   • Study more on the words you find challenging like: {', '.join(difficult_words_list)}')
    if recommendations:
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("   Keep up the good work!")

    print("\n" + "="*50 + "\n")

#Determine if the user want another round
def new_round():
    while True:
        rerun = input('\n\nWould you like another round? [yes/no]\n').strip().lower()
        if rerun in ['y', 'ye', 'yes', 'yeah']:
            run_questions()
        elif rerun in ['n', 'no', 'na']:
            return user_stat(username)
            
        else:
            print('Invalid input. Enter either yes or no')
            return new_round()
new_round()

