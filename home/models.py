from django.db import models


class Slider(models.Model):
    image = models.ImageField(upload_to='services')
    title = models.CharField(max_length=65)
    description = models.TextField(max_length=200)

    class Meta:
        verbose_name = 'اسلاید'
        verbose_name_plural = 'اسلاید ها'


class Service(models.Model):
    image = models.ImageField(upload_to='services')
    title = models.CharField(max_length=65)
    description = models.TextField(max_length=200)

    class Meta:
        verbose_name = 'خدمت'
        verbose_name_plural = 'بخش خدمات'


class About(models.Model):
    image = models.ImageField(upload_to='About')
    title = models.CharField(max_length=65)
    description = models.TextField()

    class Meta:
        verbose_name = 'درباره ما'
        verbose_name_plural = ' بخش درباره ی ما'


class WhyUs(models.Model):
    image = models.ImageField(upload_to='WhyUs')
    title = models.CharField(max_length=65)
    description = models.TextField()

    class Meta:
        verbose_name = 'چرا ما'
        verbose_name_plural = ' بخش چرا ما '


class Team(models.Model):
    image = models.ImageField(upload_to='WhyUs')
    name = models.CharField(max_length=65)
    position = models.CharField(max_length=120)
    facebook = models.CharField(max_length=120, blank=True, null=True)
    instagram = models.CharField(max_length=120, blank=True, null=True)
    x = models.CharField(max_length=120, blank=True, null=True)
    linkedin = models.CharField(max_length=120, blank=True, null=True)
    youtube = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'تیم'
        verbose_name_plural = 'بخش تیم'

