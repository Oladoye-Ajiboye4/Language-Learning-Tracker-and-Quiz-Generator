import dependencies
import file_manager
import vocabulary
from quiz import DefinitionGenerator, QuizEngine, SynonymGenerator, FillBlankGenerator
from sentence_map import sentence_map
import random
from database import db

dependencies.install_packages()

def get_username():
    username = input('Username: ').strip()
    if username == '':
        print('Enter your name')
        return get_username()

    return username

username = get_username()    
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
# Start execution
