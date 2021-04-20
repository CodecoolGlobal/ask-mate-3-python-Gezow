import os

QUESTION_FILE_PATH = os.getenv('QUESTION_FILE_PATH') if 'QUESTION_FILE_PATH' in os.environ else 'sample_data/question.csv'
QUESTION_HEADER = ['id','submission_time','view_number','vote_number','title','message','image']
ANSWER_FILE_PATH = os.getenv('ANSWER_FILE_PATH') if 'ANSWER_FILE_PATH' in os.environ else 'sample_data/answer.csv'
ANSWER_HEADER = ['id','submission_time','vote_number','question_id','message','image']
