import pandas as pd
import json
pd.options.mode.chained_assignment = None  # default='warn'


### Supress Pandas warnings
class SupressSettingWithCopyWarning:
    def __enter__(self):
        pd.options.mode.chained_assignment = None

    def __exit__(self, *args):
        pd.options.mode.chained_assignment = 'warn'

### Load data as dataframe ###
# NB: Run clean_data.py first
path = "data/"
filename = path + "clean.csv"
df = pd.read_csv(filename, on_bad_lines="skip", delimiter=";", encoding="utf8")

#### Compare with rubric ####
# Index of which question and onwards are programming questions to be graded
programming_question_index = 32

# Drop all non programming question columns
drop_columns = list(range(0, programming_question_index))
prog_df = df.drop(df.columns[drop_columns], axis=1)

# Get rubric
rubric = json.load(open("rubric.json", encoding="utf8"))

# Maximum score
max_score = 0
for key in rubric.keys():
    topic = rubric[key]
    for question in topic["answers"]:
        max_score += topic["score"]

print("Max score:", max_score)

# Create dataframe for results
result_df = df.copy()
result_df["Total"] = None

# Add topic and point columns
for key in rubric.keys():
    result_df[str(key)] = None
    topic = rubric[key]
    for question in topic["answers"]:
        question_points_column = question + "_points"
        result_df[question_points_column] = None

print("Submissions to be graded: " + str(len(prog_df.index)))
with SupressSettingWithCopyWarning():
    for i in range(len(prog_df.index)):
        sum = 0
        for key in rubric.keys():
            topic = rubric[key]
            topic_sum = 0
            task_points = topic["score"]
            for question in topic["answers"]:
                question_points_column = question + "_points"
                try:
                    correct_answer = str(topic["answers"][question]).lower()
                    student_answer = prog_df[question][i]
                    if not isinstance(student_answer, str) and not isinstance(student_answer, bool) and student_answer % 1 == 0:
                        student_answer = int(student_answer)
                    # Cast the answer in the correct datatype
                    student_answer = str(type(correct_answer)(student_answer)).lower()
                    #print(f"student{i}: {student_answer}, correct: {correct_answer}")

                    if correct_answer == student_answer:
                        points = task_points
                        topic_sum += points
                        sum += task_points
                    else:
                        points = 0

                    result_df[question_points_column][i] = points
                except KeyError:
                    continue
                except ValueError:
                    # Cast error. Set score as zero
                    result_df[question_points_column][i] = 0
                    continue
            result_df[str(key)][i] = topic_sum
            
        result_df["Total"][i] = sum

print("Submissions graded.")
result_df.to_csv(path + 'results.csv', sep=";")