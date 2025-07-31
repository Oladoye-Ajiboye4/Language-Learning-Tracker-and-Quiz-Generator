import os

print('\nLanguage Learning Tracker app\n')
print('Loading...\n\n')

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
    vocab_file = file_input()
    with open(vocab_file, encoding='utf-8') as file:
        content = file.read().strip()
        
        if ',' in content:
            parts = content.split(',')
        else:
            parts = content.split()
        
        # Clean up whitespace and drop empties
        words = [w.strip() for w in parts if w.strip()]
        
      
    return words
  
        



