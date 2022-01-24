import shutil
from shutil import copy2

import nltk
import string
import os
import math
from nltk.stem import *
import csv

if __name__ == '__main__':

    cwd = os.getcwd()
    ps = PorterStemmer()
    documentDirectory = '/Users/Griffin/Documents/CSE4771/enron1/'
    hamTestLocation = cwd + '/ham/test'
    spamTestLocation = cwd + '/spam/test'

    # calculate probability that given doc is a certain class
    def calculate_probability_for_word(word, dictionary, dictionary_size):
        numerator = dictionary.get(word, 0) + 1
        denominator = dictionary_size + len(dictionary)
        return math.log(numerator / denominator)

    def calculate_dictionary_size(dictionary):
        total_words = 0
        for key in dictionary:
            total_words += dictionary[key]
        return total_words

    def calculate_probability_for_email(path, dictionary, dictionary_size, prior):
        log_probability = math.log(prior)
        file_content = open(path, 'r', encoding='utf8', errors='ignore').read()
        tokens = nltk.word_tokenize(file_content)
        for i in tokens:
            if i.isdigit() or i in string.punctuation:
                continue
            clean_word = ps.stem(i)
            log_probability += calculate_probability_for_word(clean_word, dictionary, dictionary_size)
        return log_probability

    # creates temporary directories for training / testing data, and splits based on passed %
    def split_data(percent_training, data_types):
        for dataType in data_types:

            training_dir_loc = cwd + '/' + dataType + '/training'
            test_dir_loc = cwd + '/' + dataType + '/test'

            # clear directories from previous runs
            if os.path.exists(training_dir_loc):
                shutil.rmtree(training_dir_loc)
            os.makedirs(training_dir_loc)

            if os.path.exists(test_dir_loc):
                shutil.rmtree(test_dir_loc)
            os.makedirs(test_dir_loc)

            # get count of number of documents of this type
            count = 0
            with os.scandir(documentDirectory + dataType) as entries:
                for entry in entries:
                    count += 1

            # create copies of documents in temporary training and testing directories
            with os.scandir(documentDirectory + dataType) as entries:
                curr_index = 0
                for entry in entries:
                    if (curr_index / count) < percent_training:
                        copy2(entry, cwd + '/' + dataType + '/training')
                    else:
                        copy2(entry, cwd + '/' + dataType + '/test')
                    curr_index += 1


    def create_bag_of_words(local_path):
        words_dictionary = dict()
        with os.scandir(local_path) as entries:
            doc_type_count = 0
            for entry in entries:
                doc_type_count += 1
                file_content = open(entry, 'r', encoding='utf8', errors='ignore').read()
                tokens = nltk.word_tokenize(file_content)

                for i in tokens:
                    if i.isdigit() or i in string.punctuation:
                        continue
                    clean_word = ps.stem(i)

                    # add word to dictionary, or update count
                    if clean_word not in words_dictionary:
                        words_dictionary[clean_word] = 0
                    words_dictionary[clean_word] += 1

        return words_dictionary, doc_type_count

    def classify_test_data(
            test_location,
            ham_words_dictionary,
            ham_dict_size,
            ham_prior,
            spam_words_dictionary,
            spam_dict_size,
            spam_prior,
            actual_label
    ):
        local_correct_classification_count = 0
        local_incorrect_classification_count = 0
        with os.scandir(test_location) as entries:
            for file in entries:
                log_ham_probability = calculate_probability_for_email(file, ham_words_dictionary, ham_dict_size,
                                                                      ham_prior)
                log_spam_probability = calculate_probability_for_email(file, spam_words_dictionary, spam_dict_size,
                                                                       spam_prior)

                if actual_label == 'ham':
                    if log_ham_probability > log_spam_probability:
                        local_correct_classification_count += 1
                    else:
                        local_incorrect_classification_count += 1
                if actual_label == 'spam':
                    if log_spam_probability > log_ham_probability:
                        local_correct_classification_count += 1
                    else:
                        local_incorrect_classification_count += 1
        return local_correct_classification_count, local_incorrect_classification_count

    # here is where I ran tests on different data sizes. For the turn in doc, I have set it to just the best value
    # split_size = [.1, .25, .5, .75, .9]
    split_size = [.9]

    for i in split_size:
        # split data
        split_data(i, ['spam', 'ham'])

        # create bag of words
        hamWordsDictionary, hamDocsCount = create_bag_of_words(cwd + '/ham/training')
        spamWordsDictionary, spamDocsCount = create_bag_of_words(cwd + '/spam/training')

        # get priors from # of documents of each type
        hamPrior = hamDocsCount / (hamDocsCount + spamDocsCount)
        spamPrior = 1 - hamPrior

        # get total dictionary size (words * frequency)
        hamDictSize = calculate_dictionary_size(hamWordsDictionary)
        spamDictSize = calculate_dictionary_size(spamWordsDictionary)

        correct_classification_count = 0
        incorrect_classification_count = 0

        # classify test ham data points
        correct_classification_count_ham, incorrect_classification_count_ham = classify_test_data(
            hamTestLocation,
            hamWordsDictionary,
            hamDictSize,
            hamPrior,
            spamWordsDictionary,
            spamDictSize,
            spamPrior,
            'ham'
        )

        # classify spam data points
        correct_classification_count_spam, incorrect_classification_count_spam = classify_test_data(
            spamTestLocation,
            hamWordsDictionary,
            hamDictSize,
            hamPrior,
            spamWordsDictionary,
            spamDictSize,
            spamPrior,
            'spam'
        )

        total_correct = correct_classification_count_ham + correct_classification_count_spam
        total_incorrect = incorrect_classification_count_ham + incorrect_classification_count_spam
        accuracy = total_correct / (total_incorrect + total_correct)
        print(total_correct)
        print(total_incorrect)
        print(total_correct / (total_incorrect + total_correct))

        # Here is where I recorded the outputs of each test run, and ran analysis in Excel
        # with open(cwd + '/bayes_results.csv', mode='a') as output_file:
        #    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #    output_writer.writerow([i,
        #                            correct_classification_count_ham,
        #                            incorrect_classification_count_ham,
        #                            correct_classification_count_spam,
        #                           incorrect_classification_count_spam,
        #                            total_correct, total_incorrect, accuracy])











