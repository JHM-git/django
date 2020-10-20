import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question

# Create your tests here.

def create_question(q_text, days):
  #creates question with given text and published within days given
  #negative days given for publications in the past
  time = timezone.now() + datetime.timedelta(days=days)
  return Question.objects.create(question_text=q_text, pub_date=time)

class QuestionModelTests(TestCase):

  def test_was_published_recently_with_fut_question(self):
    #was_published_recently should return False if pub_date is in the future
    time = timezone.now() + datetime.timedelta(days=30)
    fut_question = Question(pub_date=time)
    self.assertIs(fut_question.was_published_recently(), False)

  def test_was_published_recently_with_old_question(self):
    #was_published_recently returns False for questions older than 1 day
    time = timezone.now() - datetime.timedelta(days=1, seconds=1)
    old_question = Question(pub_date=time)
    self.assertIs(old_question.was_published_recently(), False)

  def test_was_published_recently_with_recent_question(self):
    #was_published_recently returns True for questions published within a day
    time = timezone.now() - datetime.timedelta(hours=23, minutes=59)
    recent_question = Question(pub_date=time)
    self.assertIs(recent_question.was_published_recently(), True)
  
class QuestionIndexViewTests(TestCase):
  def test_no_questions(self):
    #checks existence of questions
    response = self.client.get(reverse('polls:index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'No polls available.')
    self.assertQuerysetEqual(response.context['latest_questions'], [])

  def test_past_questions(self):
    #checks questions with pub_date in the past are displayed on page
    create_question('Past Question?', -30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(response.context['latest_questions'], ['<Question: Past Question?>'])

  def test_fut_questions(self):
    #checks that questions with future pub_date are not displayed on page
    create_question('Future Question?', 30)
    response = self.client.get(reverse('polls:index'))
    self.assertContains(response, 'No polls available.')
    self.assertQuerysetEqual(response.context['latest_questions'], [])

  def test_past_and_fut_questions(self):
    #only past questions are displayed on page
    create_question('Past Question?', -30)
    create_question('Future Question?', 30)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(response.context['latest_questions'], ['<Question: Past Question?>'])

  def test_two_past_questions(self):
    create_question('Past Question1?', -30)
    create_question('Past Question2?', -5)
    response = self.client.get(reverse('polls:index'))
    self.assertQuerysetEqual(response.context['latest_questions'], ['<Question: Past Question2?>', 
    '<Question: Past Question1?>'])

class QuestionDetailViewTests(TestCase):
  def test_fut_questions(self):
    #detail view of question with pub_date in the future returns a 404
    fut_question = create_question('Future Question', 5)
    url = reverse('polls:detail', args=(fut_question.id,))
    response = self.client.get(url)
    self.assertEqual(response.status_code, 404)

  def test_past_question(self):
    #detail view of a question with past pob_date displayes the question text
    past_question = create_question('Past Question', -5)
    url = reverse('polls:detail', args=(past_question.id,))
    response = self.client.get(url)
    self.assertContains(response, past_question.question_text)
