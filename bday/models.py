from django.db import models

class Bday(models.Model):
    bday = models.DateField("Дата", auto_now=False, auto_now_add=False)
    man = models.CharField("Именинник", max_length=50)
    comment = models.CharField("Комментарий", max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.man} ({self.bday})"