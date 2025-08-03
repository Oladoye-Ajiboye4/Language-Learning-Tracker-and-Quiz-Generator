'''
Handles file operations and validation
'''
import os
import re

print('\nLanguage Learning Tracker app\n')
print('Loading...\n\n')

# Gets the file directory
def file_dir():
    user_dir = input('Press enter if the file is in the same directory as this Python script,\nor enter your file path (e.g. C:\\Users\\YourName\\Documents):\n').strip()
    
    if user_dir:
        try:
            os.chdir(user_dir)
            return os.getcwd()
        except Exception as e:
            print(f"\nThe specified path '{user_dir}' was not found or is invalid.\n{e}\nPlease try again.\n")
            return file_dir()
    else:
        return os.getcwd()

# Validate file name
def file_input():
    file_name = input('Enter the file name (e.g. vocab.txt or vocab):\n').strip()
    if (not file_name.lower().endswith('.txt')) and ('.' in file_name):
        file_name = file_name[:file_name.index('.')]
        file_name += '.txt'
    elif not file_name.lower().endswith('.txt'):
        file_name = file_name + '.txt'
    
    if not os.path.exists(file_name):
        if file_name == '':
            print("\nNo filename entered. Please include the extension (e.g. .txt)\n")
        else:
            print(f"\nFile '{file_name}' not found. Please check the name and try again.\n")
        return file_input()
    
    print(f"\n\nOpening '{file_name}'...\n")
    return file_name

def vocab_data():
    # Reads a text file (article, word list, etc.) and extracts a list of unique words.
    vocab_file = file_input()
    
    try:
        with open(vocab_file, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File '{vocab_file}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file '{vocab_file}': {e}")
        return []

    if not content.strip():
        print("Warning: File is empty or contains only whitespace.")
        return []
        
    # Replace various whitespace characters with a single space
    content = re.sub(r'\s+', ' ', content)
    
    # This regex finds sequences of letters, numbers, and apostrophes.
    potential_words = re.findall(r"[a-zA-Z0-9']+", content)

    # Clean and Filter Words 
    cleaned_words = []
    for word in potential_words:
        # Strip leading/trailing apostrophes
        cleaned_word = word.strip("'")

        # Check if the cleaned word is not empty and contains at least one letter
        if cleaned_word and any(char.isalpha() for char in cleaned_word):
            # Convert to lowercase for consistency
            cleaned_words.append(cleaned_word.lower())

    # Remove Duplicates
    unique_words = list(set(cleaned_words)) 
    unique_words.sort()

    print(f"Extracted {len(unique_words)} unique words from '{vocab_file}'.")
    return unique_words

        



