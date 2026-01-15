from django.test import TestCase
from django.contrib.auth.models import User
from .models import Teacher, Review

class ReviewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a user
        testuser1 = User.objects.create_user(username='testuser1', password='password123')
        testuser1.save()

        # Create a teacher
        test_teacher = Teacher.objects.create(name='John Doe')
        test_teacher.save()

        # Create a review
        testreview = Review.objects.create(
            user=testuser1,
            teacher=test_teacher,
            punctuality=4,
            clarity=5,
            justice=4,
            support=5,
            flexibility=4,
            knowledge=5,
            methodology=4,
            comment="The best test teacher ever!"
        )

        testreview.save()

    def test_review_content(self):
        review = Review.objects.get(id=1)
        user = f"{review.user}"
        teacher = f"{review.teacher}"
        punctuality = review.punctuality
        clarity = review.clarity
        justice = review.justice
        support = review.support
        flexibility = review.flexibility
        knowledge = review.knowledge
        methodology = review.methodology
        comment = f"{review.comment}"
        self.assertEqual(user, 'testuser1')
        self.assertEqual(teacher, 'John Doe')
        self.assertEqual(punctuality, 4)
        self.assertEqual(clarity, 5)
        self.assertEqual(justice, 4)
        self.assertEqual(support, 5)
        self.assertEqual(flexibility, 4)
        self.assertEqual(knowledge, 5)
        self.assertEqual(methodology, 4)
        self.assertEqual(comment, "The best test teacher ever!")
