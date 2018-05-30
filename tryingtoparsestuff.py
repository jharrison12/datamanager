import pandas as pd, os
import numpy as np
import logging
import collections, datetime

logging.basicConfig(level=logging.WARNING)

os.chdir("C:\\Users\\harrisonjd\\code")

dataframe = pd.read_csv("trial.csv")
dataframe.set_index('ID', inplace=True)

indices = list(dataframe.index.unique())




def is_even(number):
    if number % 2 == 0:
        return True
    else:
        return False

"""
The dictionary hack below must be done because Pandas does not load dict to a csv for some
inane reason if the lists are not the same length.  Also you must use an ordered dict
so they do not print to the csv in a different order

https://stackoverflow.com/questions/19736080/creating-dataframe-from-a-dictionary-where-entries-have-different-lengths
"""


def print_to_file(no_initial_interviews_valid, no_initial_iws_but_random, no_reviews_at_all,
                  no_initial_iws_no_valid_iws_and_more_than_one,
                  no_initial_iws_qcvalid_available_but_not_select_and_more_than_one, less_than_two,
                  one_iw_valid_but_not_selected_due_to_seed,
                  one_iw_but_not_valid_but_would_be_selected,no_reviews_and_reason,
                  language):
    my_dict = collections.OrderedDict()
    my_dict["No initial iws valid"] = no_initial_interviews_valid
    my_dict["No initial iws selected but QC has selected non-initial iws for eval"] = no_initial_iws_but_random
    my_dict["No reviews at all"] = no_reviews_at_all
    my_dict[
        "No initial iws selected and no QCVALID iws available AND more than one iws"] = no_initial_iws_no_valid_iws_and_more_than_one
    my_dict[
        "No intial iws selected AND QCVALID iws available but not selected AND more than one iws"] = no_initial_iws_qcvalid_available_but_not_select_and_more_than_one
    my_dict["Only one iws"] = less_than_two
    my_dict["1 iw QCvalid BUT NOT selected due to random seed"] = one_iw_valid_but_not_selected_due_to_seed
    my_dict["1 iw but not QCVALID but would be selected if QCVALID"] = one_iw_but_not_valid_but_would_be_selected

    final_to_csv = pd.DataFrame.from_dict(my_dict, orient='index').transpose()

    final_to_csv.to_csv("parsedata{}{}.csv".format(datetime.datetime.today().strftime('%Y-%m-%d'), language),
                        index=False)

    print("No reviews at all: {}\n\
          Reasons: {}\n\
          Less than two {}\n".format(no_reviews_at_all, no_reviews_and_reason, less_than_two))

    print("No initial but one random {}\n \
            Initial Valid but not chosen due to seed {}\n \
            Initial not valid but would be chosen {}".format(no_initial_iws_but_random,
                                                             one_iw_valid_but_not_selected_due_to_seed,
                                                             one_iw_but_not_valid_but_would_be_selected))


def parse_first_two(all_iws, language):
    if language == 1:
        languagetype = "english"
    elif language == 2:
        languagetype = "spanish"
    else:
        languagetype = "undiscovered language"

    all_one_language = all_iws[all_iws["Language"]==language]
    no_initial_interviews_valid = []
    no_initial_iws_but_random = []
    no_random_interviews = []
    no_initial_iws_no_valid_iws_and_more_than_one = []
    no_problem_interviews = []
    no_reviews_at_all = []
    no_reviews_and_reason = {}
    less_than_two = []
    no_initial_iws_qcvalid_available_but_not_select_and_more_than_one = []
    pass_along_to_initial_interview_check = []
    one_iw_valid_but_not_selected_due_to_seed = []
    one_iw_but_not_valid_but_would_be_selected = []

    indices = list(all_one_language.index.unique())

    for index in indices:
        new_frame = all_one_language.loc[[index]]
        # numpy.isin not working.  however the below works sigh

        first_two_interviews = new_frame.iloc[0:2]
        logging.warning(first_two_interviews)
        first_two_qc_valid = first_two_interviews["QCValidStatus"].values
        first_two_qc_selection = first_two_interviews["QCSelection"].values
        qcselection = new_frame[["QCSelection"]].values
        validnums = new_frame[["QCValidStatus"]].values
        interviewnums = new_frame[["InterviewOrder"]].values
        # if (1 in first_two_qc_valid) and (1 not in first_two_qc_selection):  # Take out length restriction gives you 4
        # pass_along_to_initial_interview_check.append(index)
        if len(first_two_qc_valid) < 2:
            less_than_two.append(index)
        # No Valid interview in first two interviews
        if 1 not in first_two_qc_valid:
            no_initial_interviews_valid.append(index)
        if all([num not in qcselection for num in [1, 2, 5, 9]]) and (1 in validnums) and (len(interviewnums)) > 1:
            no_initial_iws_qcvalid_available_but_not_select_and_more_than_one.append(index)
        if (1 not in qcselection) and (1 not in validnums) and (len(interviewnums)) > 1:
            no_initial_iws_no_valid_iws_and_more_than_one.append(index)
        # No Initial but at least one two or five.
        if (1 not in qcselection) and (
        any([num in qcselection for num in [2, 5, 9, 10]])):  # (2 in qcselection) or (5 in qcselection)):
            no_initial_iws_but_random.append(index)
        # No Reviews at all.  Number of iws does not matter
        if all(num == 0 for num in qcselection):
            no_reviews_at_all.append(index)

        # Different loop for less than two interview categories
    for number in less_than_two:
        new_frame = dataframe.loc[[number]]
        # Random seed.  Return the random seed series, remove dup. and take first value in list
        random_seed = str(new_frame["QCRandomSeed"].unique()[0])
        random_seed_second_digit = int(random_seed[-1])
        is_number_even = is_even(random_seed_second_digit)
        first_two_interviews = new_frame.iloc[0:2]
        first_two_qc_valid = first_two_interviews["QCValidStatus"]
        first_two_qc_selection = first_two_interviews["QCSelection"]
        question_two = first_two_interviews[(first_two_interviews["InterviewOrder"] == 2) &
                                            (first_two_interviews["QCValidStatus"] == 1)]
        question_one = first_two_interviews[(first_two_interviews["InterviewOrder"] == 1) &
                                            (first_two_interviews["QCValidStatus"] == 1)]
        question_one_not_valid = first_two_interviews[(first_two_interviews["InterviewOrder"] == 1) &
                                                      (first_two_interviews["QCValidStatus"] != 1)]
        if is_number_even and not question_two.empty:
            one_iw_valid_but_not_selected_due_to_seed.append(number)
        if is_number_even is False and not question_one.empty:
            one_iw_valid_but_not_selected_due_to_seed.append(number)
        logging.info(is_number_even, question_one_not_valid)
        if is_number_even and not question_one_not_valid.empty:
            one_iw_but_not_valid_but_would_be_selected.append(number)

    for number in no_reviews_at_all:
        new_frame = dataframe.loc[number]
        values = new_frame[["QCInvalidReasonList"]].values
        if len(values) > 1:
            no_reviews_and_reason[number] = values

    print_to_file(no_initial_interviews_valid, no_initial_iws_but_random, no_reviews_at_all,
                  no_initial_iws_no_valid_iws_and_more_than_one,
                  no_initial_iws_qcvalid_available_but_not_select_and_more_than_one, less_than_two,
                  one_iw_valid_but_not_selected_due_to_seed,
                  one_iw_but_not_valid_but_would_be_selected,no_reviews_and_reason, languagetype)

parse_first_two(dataframe,1)

#dataframe = pd.read_csv("trial.csv")
#dataframe.set_index('ID', inplace=True)
#indices = list(dataframe.index.unique())

parse_first_two(dataframe,2)




"""
    for index in indices:
    new_frame = dataframe.loc[[index]]
    logging.debug(new_frame)


    first_two_interviews = new_frame.iloc[0:2]
    logging.warning(first_two_interviews)
    first_two_qc_valid = first_two_interviews["QCValidStatus"].values
    first_two_qc_selection = first_two_interviews["QCSelection"].values
    qcselection = new_frame[["QCSelection"]].values
    validnums = new_frame[["QCValidStatus"]].values
    interviewnums = new_frame[["InterviewOrder"]].values
    #if (1 in first_two_qc_valid) and (1 not in first_two_qc_selection):  # Take out length restriction gives you 4
       # pass_along_to_initial_interview_check.append(index)
    if len(first_two_qc_valid) < 2:
        less_than_two.append(index)
    # No Valid interview in first two interviews
    if 1 not in first_two_qc_valid:
        no_initial_interviews_valid.append(index)
    if all([num not in qcselection for num in [1,2,5,9]]) and (1 in validnums) and (len(interviewnums)) > 1:
        no_initial_iws_qcvalid_available_but_not_select_and_more_than_one.append(index)
    if (1 not in qcselection) and (1 not in validnums) and (len(interviewnums)) > 1:
        no_initial_iws_no_valid_iws_and_more_than_one.append(index)
    # No Initial but at least one two or five.
    if (1 not in qcselection) and (any([num in qcselection for num in [2,5,9,10]])): #(2 in qcselection) or (5 in qcselection)):
        no_initial_iws_but_random.append(index)
    # No Reviews at all.  Number of iws does not matter
    if all(num == 0 for num in qcselection):
        no_reviews_at_all.append(index)


"""


