from django.core.management.base import BaseCommand
from ...utils import add_question

class Command(BaseCommand) :
    help = '''
        To add new questions from the README file into the database
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'limit',
            type = int,
            help = "The number of questions you want in db"
        )

    def handle(self, *args, **kwargs) :
        # print(kwargs)
        add_question.add_question(kwargs['limit'])