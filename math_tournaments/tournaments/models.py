import uuid, re
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy, reverse

from math_tournaments.settings import AUTH_USER_MODEL


def task_image_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return ('uploads/images/task/%s' % filename)

class Task(models.Model):
    round = models.ForeignKey('Round',
                              verbose_name='Раунд турнира',
                              on_delete=models.CASCADE)
    image = models.ImageField(upload_to=task_image_directory_path,
                              verbose_name='Задание')
    right_answer = models.CharField(max_length=25,
                                    verbose_name='Верный ответ')
    score = models.PositiveSmallIntegerField(verbose_name='Балл',
                                             default=1)
    #Regex for find commas in numbers
    regex = re.compile(r'(?<=\d)(,)(?=\d)')
    user_answer = models.ManyToManyField(AUTH_USER_MODEL,
                                         through='Answer')


    def check_answer(self, user_answer):
        user_answer = self.regex.sub('.', user_answer)
        right_answer = self.regex.sub('.', self.right_answer)
        return user_answer.casefold() == right_answer.casefold()
    
    def get_absolute_url(self):
        return reverse('task-list', kwargs={'owner': self.round.pk })

class Answer(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    task = models.ForeignKey(Task,
                             on_delete=models.CASCADE)
    correctness = models.BooleanField(verbose_name='Корректность')

class Round(models.Model):
    FINAL = 'F'
    DEFAULT = 'D'
    TYPE_CHOICES = (
            (FINAL, 'Финальный'),
            (DEFAULT, 'Стандартный'),
        )
    start_at = models.DateTimeField(verbose_name='Начинается в')
    duration = models.DurationField(verbose_name='Длительность')
    tournament = models.ForeignKey('Tournament',
                                   verbose_name='Турнир',
                                   on_delete=models.CASCADE)
    typization = models.CharField(max_length=1,
                                  choices=TYPE_CHOICES,
                                  default=DEFAULT,
                                  verbose_name='Тип')
    subscribers = models.ManyToManyField(AUTH_USER_MODEL,
                                         verbose_name='Подписчики')


    def get_fields(self):
        exclude = ('id','tournament', 'subscribers',)
        return [
            (field.name, field.verbose_name, self._get_FIELD_display(field))
            for field in self.__class__._meta.fields
            if field.name not in exclude
            ]
    
    def get_absolute_url(self):
        return reverse('round-list', kwargs={'owner': self.tournament.pk})

    @property
    def max_score(self):
        score = self.task_set.aggregate(Sum('score'))['score__sum']
        if not score:
            return 0
        return score
        
    @property
    def subscribe_available(self):
        return timezone.now() <= self.start_at
    
    @property
    def in_progress(self):
        end_at = self.start_at + self.duration
        return self.start_at < timezone.now() <= end_at
    
    @property
    def finished(self):
        end_at = self.start_at + self.duration
        return timezone.now() > end_at

class Tournament(models.Model):
    name = models.CharField(max_length=30,
                            verbose_name='Название')
    owner = models.ForeignKey(AUTH_USER_MODEL,
                       verbose_name='Создатель',
                       on_delete=models.CASCADE)
    top_N_to_final = models.PositiveIntegerField(verbose_name='Количество допущенных в финал')
    top_N_winners = models.PositiveIntegerField(verbose_name='Количество победителей')


    def get_absolute_url(self):
        return reverse('tour-detail', kwargs={'pk': self.pk})

    def get_fields(self):
        exclude = ('id', 'owner')
        return [
            (field.name, field.verbose_name, self._get_FIELD_display(field))
            for field in self.__class__._meta.fields
            if field.name not in exclude
        ]
    
    
    def top_in_final(self):
        return Answer.objects.filter(task__round__tournament=self.pk, correctness=True) \
                     .values('user__id', 'user__email', 'user__first_name', 'user__last_name') \
                      .annotate(score_sum=Sum('task__score')) \
                      .order_by('score_sum')[:self.top_N_to_final]
       
    
    @property
    def final_round(self):
        return self.round_set.get(typization=Round.FINAL)
        
