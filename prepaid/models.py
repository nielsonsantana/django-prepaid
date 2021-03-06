import datetime

from django.conf import settings
from django.contrib import auth
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ValidUnitPackManager(models.Manager):

    def get_query_set(self):
        return super(ValidUnitPackManager, self).get_query_set().filter(
            expires__gt=datetime.date.today(), quantity__gt=0)


def _default_expires():
    if hasattr(settings, 'PREPAID_DEFAULT_EXPIRY_PERIOD'):
        return datetime.date.today() + datetime.timedelta(
            settings.PREPAID_DEFAULT_EXPIRY_PERIOD)


class UnitPack(models.Model):
    # Normally we only deal with not expired and not empty unit packs,
    # but sometimes we need to peek into expired.
    all_objects = models.Manager()
    objects = models.Manager()

    user = models.ForeignKey(auth.models.User)
    quantity = models.IntegerField(_('quantity'), db_index=True)
    expires = models.DateField(
        _('expire'), default=_default_expires, db_index=True)

    # field used to associate one determined operation/task with the consum
    # reference_code = models.CharField(max_length=40, null=True, blank=True,
    #                                   unique=True, db_index=True)

    # bookkeeping
    timestamp = models.DateTimeField(
        _('created'), auto_now_add=True, db_index=True, blank=True)
    initial_quantity = models.IntegerField(db_index=True, blank=True)

    class Meta:
        ordering = ('expires',)

    def is_valid(self):
        return self.quantity > 0 and self.expires > datetime.date.today()
    is_valid.boolean = True

    @classmethod
    def get_user_packs(cls, user):
        return cls.objects.filter(user=user)

    @classmethod
    def get_user_credits(cls, user):
        credits = sum(up.quantity for up in cls.get_user_packs(user))
        return credits

    @classmethod
    def consume(cls, user, quantity=1):
        ups = cls.get_user_packs(user)
        if sum(up.quantity for up in ups) < quantity:
            raise ValueError("User does not have enough units.")

        newup = UnitPack()
        newup.quantity = -quantity
        newup.initial_quantity = 0
        newup.user = user
        newup.timestamp = datetime.datetime.now()
        newup.save()


# provide default value for initial_quantity
def _handle_pre_save(sender, instance=None, **kwargs):
    assert instance is not None
    if instance.pk is None and instance.initial_quantity is None:
        instance.initial_quantity = instance.quantity


models.signals.pre_save.connect(_handle_pre_save, sender=UnitPack)
