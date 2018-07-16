from django.test import TestCase
from django.db.utils import IntegrityError

from people.models import ORMPerson


class ORMPersonModelTestCase(TestCase):

    def test_email_is_unique_but_can_be_multiple_nulls(self):
        ORMPerson.objects.create()
        ORMPerson.objects.create()
        ORMPerson.objects.create()
        ORMPerson.objects.create(email='a')
        ORMPerson.objects.create(email='b')
        try:
            ORMPerson.objects.create(email='a')
            assert False
        except IntegrityError:
            pass
