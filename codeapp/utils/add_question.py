import random, logging, os
from ..models import Cards
from Code_Cards_Server.settings import BASE_DIR

logging.basicConfig(level=logging.DEBUG)

def add_to_db(data, qno) :
    logger = logging.getLogger(__name__)

    card = Cards()

    card.question = data['question']
    card.hint = "To be added..."
    card.company = data['company']
    card.solution_link = data['solution_link']

    try :
        card.save()
        logger.info(f"Question {qno} succesfully added!")
    except :
        logger.error(f"Question {qno} resulted in an error while adding")

def add_question(number_of_questions) :
    Cards.objects.all().delete()

    db = list()

    floc = os.path.join(BASE_DIR, 'codeapp', 'utils', 'questions.md')
    f = open(floc, 'r+')
    problems = f.read()
    problems = problems.split('---')


    for problem in problems :

        if number_of_questions == 0 :
            break
        number_of_questions -= 1

        data_to_db = dict()
        problem = problem.split('\n')

        for problem_line in range(len(problem)):
            if problem[problem_line].startswith('```') :
                problem[problem_line] = '\n' + problem[problem_line] + '\n'

            if problem[problem_line].startswith('#') :
                problem[problem_line] = problem[problem_line][13:]

        data = problem[2:-2]

        question = ""
        for line in data[2:-2] :
            if line.startswith("This problem was asked by ") :
                data_to_db['company'] = line[26:-1]
                continue
            else :
                data_to_db['company'] = ''
            
            if line.startswith(" ") or line.endswith(" ") :
                line = '\n' + line

            if line == '' :
                line = '\n'
            question += line
        
        data_to_db['id'] = data[0]
        data_to_db['question'] = question
        data_to_db['solution_link'] = 'https://github.com/vineetjohn/daily-coding-problem/blob/master/' + data[-1][11:-1]
        db.append(data_to_db)

    random.shuffle(db)
    for d in db :
        add_to_db(d, db.index(d) + 1)

    f.close()

if __name__ == '__main__' :
    number_of_questions = int(input("Enter the number of questions to be stored in data = "))
    add_question(number_of_questions)