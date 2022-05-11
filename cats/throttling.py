import datetime

from rest_framework import throttling


# кастомный тротлинг-класс, который разрешает работу
# с трёх до пяти утра
class WorkingHoursRateThrottle(throttling.BaseThrottle):

    def allow_request(self, request, view):
        now = datetime.datetime.now().hour
        if now >= 3 and now <= 5:
            return False
        return True
