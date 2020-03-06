from django.contrib.auth.models import User
from django.test import TestCase
from website.ride_utils import send_message


class MessageTestCase(TestCase):
  def setUp(self):
    self.valid = User.objects.create_user(username='valid', password='hellopie')
    self.valid.profile.user_type = "V"
    self.valid.profile.phone = "7148831948"
    self.valid.profile.user.email = "email@email.com"
    self.valid.save()

    self.no_phone = User.objects.create_user(username='no_phone', password='hellopie')
    self.no_phone.profile.user_type = "V"
    self.no_phone.profile.phone = ""
    self.no_phone.profile.user.email = "email@email.com"
    self.no_phone.save()

    self.no_email = User.objects.create_user(username='no_email', password='hellopie')
    self.no_email.profile.user_type = "V"
    self.no_email.profile.phone = "7148831948"
    self.no_email.profile.user.email = ""
    self.no_email.save()

  def test_success(self):
    res = send_message("test message", self.valid.profile)
    
    self.assertIsNotNone(res[0])
    self.assertIsNotNone(res[1])

  def test_no_phone(self):
    res = send_message("test message", self.no_phone.profile)
    
    self.assertIsNone(res[0])
    self.assertIsNotNone(res[1])

  def test_no_email(self):
    res = send_message("test message", self.no_email.profile)
    
    self.assertIsNotNone(res[0])
    self.assertIsNone(res[1])

  def test_none(self):
    res = send_message("test message", None)
    
    self.assertIsNone(res[0])
    self.assertIsNone(res[1])
