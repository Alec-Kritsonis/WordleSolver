

import random
import os
from collections import defaultdict

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = os.sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# read curated list of words
def loadWordList(file_name):
    f = open(file_name, 'r')
    return f.read().split('\n')

def removeGuesses(guess_data, possible_guesses):

    # print(guess_data)

    # keep track of how many words we removed and why they were removed
    rcorrect, rwrong, ricorrect, rwfreq = 0,0,0,0

    new_guesses = []

    # traverse all the current words
    for word in possible_guesses:
        add = True
        # print("checking: ", word)
        # traverse each letter
        for i in range(0,5):

            # data on the index
            if i in guess_data:
                for value in guess_data[i]:
                    # remove words that have wrong letters in a pos where we know the correct one
                    if value[1] == 'c' and value[0] != word[i]:
                        # print("REMOVED - word shouldnt have a '{}' in slot {}\n".format(word[i], i))
                        rcorrect += 1
                        add = False
                        break
                    # remove words that are missing an incorrect letter
                    if value[1] == 'i' and value[0] not in word:
                        # print("REMOVED - word is missing a '{}'\n".format(value[1]))
                        ricorrect += 1
                        add = False
                        break
                    # remove words that have correct letters in an incorrect spot
                    if value[1] == 'i' and value[0] == word[i]: 
                        # print("REMOVED - word shouldnt have a '{}' in slot {}\n".format(word[i], i))
                        rcorrect += 1
                        add = False
                        break
            # data on the letter
            if word[i] in guess_data:
                for value in guess_data[word[i]]:
                    # dont get rid of the word if it has a wrong and correct data. (this can happen if 'happy' is inputted, the 'a' is correct,
                    # then 'basal' is inputted and the second 'a' is wrong. meaning theres only 1 'a' in the answer)
                    # NOTE: this might mess up with a word that has 3 same letters like 'error'. im too lazy to think about that tho
                    if len(guess_data[word[i]]) <= 1:
                        # dont add words with wrong letters
                        if value[0] == "Wrong":
                            # print("REMOVED - word contains the wrong letter '{}'\n".format(word[i]))
                            rwrong += 1
                            add = False
                            break
                    else:
                        if word.count(word[i]) > 1:
                            rwfreq += 1
                            add = False
                            break
            if add == False:
                break
        if add:
            new_guesses.append(word)
    
    print("{} words removed for having incorrect letters\n{} words removed for having incorrect letters in a spot where we know the correct letter\n{} words removed for not having a letter out of place\n{} words removed for having too many of some letter".format(rwrong, rcorrect, ricorrect, rwfreq))
    return new_guesses

def inputGuess():

    result_dict = defaultdict(list)
    guess = input("Enter the word you guessed (or 'restart' to start from round 1 again): \n")

    if guess == "restart":
        return "restart", result_dict

    results = input("Enter the results with format: x,x,x,x,x with x being\n- w: wrong letter\n- i: incorrect spot\n- c: correct spot\nexample: 'w,w,c,i,w': \n")
    results = results.split(',')

    # translate user input to how we store the letter info
    for i in range(0,5):
        if results[i] == 'c':
            result_dict[guess[i]].append(("Correct", i))
            result_dict[i].append((guess[i], 'c'))
        elif results[i] == 'i':
            result_dict[guess[i]].append(("I Spot", i))
            result_dict[i].append((guess[i], 'i'))
        elif results[i] == 'w':
            result_dict[guess[i]].append(("Wrong", -1))
    
    return guess, result_dict

def getFrequency(remaining_words):
    freq = {} 
    for word in remaining_words:
        for letter in word:
            if letter not in freq:
                freq[letter] = 0
            else:
                freq[letter] += 1
    return freq

def getScores(freq, remaining_words):

    word_scores = {}
    for word in remaining_words:

        for letter in word:
            if word.count(letter) > 1:
                word_scores[word] = 0
            else:
                if word not in word_scores:
                    word_scores[word] = freq[letter]
                else:
                    word_scores[word] += freq[letter]
    word_list = list(word_scores.items())
    
    word_list.sort(key=lambda x:x[1], reverse=True)
    return word_list

if __name__ == "__main__":

    answer_list = loadWordList(resource_path("answers.txt")) # word list from https://github.com/bnprks/wordle_solver/blob/master/answers.txt

    while True:

        possible_answers = answer_list.copy()
        guess_data = {} 
        guesses = []

        for i in range(0,5):
            print("Round {}:".format(i + 1))
            print("Possible Guesses:", len(possible_answers))

            remaining_letter_freq = getFrequency(possible_answers)
            word_scores = getScores(remaining_letter_freq, possible_answers)
            

            # give the user some good words to guess
            print("Here's some sample words to guess:")
            if len(word_scores) < 15:
                print(word_scores)
                # print(', '.join(weerieord_scores[0]))
            else:
                show_guesses = []
                # show_guesses_list = possible_answers.copy()
                # for i in range(0,15):
                #     r = random.randint(0, len(show_guesses_list) - 1)
                #     show_guesses.append(show_guesses_list[r])
                #     show_guesses_list.remove(show_guesses_list[r])
                for i in range(0,15):
                    show_guesses.append(word_scores[i][0])
                print(', '.join(show_guesses))

            # user inputs the guessed word and the results wordle gave
            guess, result_dict = inputGuess()
            
            if guess == "restart":
                os.system('cls')
                print("Restarting...")
                break

            guesses.append(guess)
            print("Your Guesses:", ' '.join(guesses))

            # update the info on letters
            guess_data.update(result_dict)

            # remove words based off info
            possible_answers = removeGuesses(guess_data, possible_answers)
            print()
