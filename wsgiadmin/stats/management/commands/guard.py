import datetime
import logging

from constance import config
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from wsgiadmin.stats.tools import add_credit

from wsgiadmin.apps.backend import typed_object
from wsgiadmin.old.apacheconf.tools import restart_master
from wsgiadmin.emails.models import Message


info = logging.info

class Command(BaseCommand):
    help = "Credit guardian"

    def get_users(self):
        """Get users close to 0 or under"""
        users = []
        for user in User.objects.all():
            if ( float(user.parms.pay_total_day()) == 0 and user.parms.credit < 0 ) or\
               ( user.parms.pay_total_day() > 0 and float(user.parms.credit) / float(user.parms.pay_total_day()) < 14 ) or\
               ( not user.parms.enable and user.parms.credit >= 0):
                users.append(user)
        return users

    def disable_apps(self, user):
        for app in user.app_set.all():
            app = typed_object(app)
            app.disable()
            app.commit()
            logging.info("%s (%d) disabled" % (app.name, app.id))
            print "%s (%d) disabled" % (app.name, app.id)

    def enable_apps(self, user):
        for app in user.app_set.all():
            app = typed_object(app)
            app.enable()
            app.commit()
            logging.info("%s (%d) enabled" % (app.name, app.id))
            print "%s (%d) enabled" % (app.name, app.id)

    def process(self, user):
        parms = user.parms
        apache_reload = False
        data = {}
        tmpl = ""

        if config.auto_disable:
            if parms.credit <= config.credit_threshold and parms.enable:
                parms.enable = False
                parms.save()
                apache_reload = True
                message = Message.objects.filter(purpose="webs_disabled")
                if message:
                    message[0].send(user.email, {})
                self.disable_apps(user)
                print "\t* %s disabled" % user.username
                return apache_reload
            elif parms.credit >= 0 and not parms.enable:
                parms.enable = True
                parms.save()
                apache_reload = True
                self.enable_apps(user)
                message = Message.objects.filter(purpose="webs_enabled")
                if message:
                    message[0].send(user.email, {"username": user.username})
                print "\t* %s enabled" % user.username
                return apache_reload

        correction = 0.0
        if parms.credit < 0:
            correction += abs(parms.credit)

        if parms.low_level_credits == "send_email":
            tmpl = "low_credit"
            data = {"credit": parms.credit, "days": parms.days_left}
        elif parms.low_level_credits == "buy_month":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 30 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_three_months":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 90 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_six_months":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 180 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"
        elif parms.low_level_credits == "buy_year":
            data = {"credit": parms.credit, "days": parms.days_left}
            credits = parms.pay_total_day() * 360 + correction
            add_credit(user, credits)
            tmpl = "autobuy_credit"

        if tmpl and data:
            message = Message.objects.filter(purpose=tmpl)
            if message:
                message[0].send(user.email, data)
                #message[0].send(config.email, data)
                print "\t* E-mail sent"
            parms.last_notification = datetime.date.today()
            parms.save()

        return apache_reload

    def handle(self, *args, **options):
        total_credit = 0.0
        apache_reload = False
        guarding = []
        print "Username".ljust(40),
        print "Credit".ljust(15),
        print "cr./day".ljust(10),
        print "Days left".ljust(10),
        print "Low level act.".ljust(15),
        print "Last notif.".ljust(15)

        for user in self.get_users():
            parms = user.parms
            print user.username.ljust(40),
            print ("%.2f cr." % parms.credit).ljust(15),
            print ("%.2f cr." % parms.pay_total_day()).ljust(10),
            print ("%.2f" % parms.days_left).ljust(10),
            print (parms.low_level_credits).ljust(15),
            print (parms.last_notification.strftime("%d.%m.%Y")).ljust(15) if parms.last_notification else "--".ljust(15),
            if not parms.guard_enable: print "Guarding disabled",
            if parms.credit < 0:
                total_credit += parms.credit
            if not parms.last_notification or (parms.last_notification and (datetime.date.today() - parms.last_notification).days >= 3):
                if parms.guard_enable and parms.credit < config.credit_threshold and parms.enable:
                    guarding.append(user)
                    print "Be disabled!!!",
                elif not parms.enable:
                    print "is disabled",
                elif parms.guard_enable:
                    guarding.append(user)
                    print "Be guarded",
            if not parms.enable and parms.credit >= 0:
                guarding.append(user)
                print "will be enabled",
            print
        print "Total: %.2f" % total_credit

        if raw_input("Do you agree? (yes/NO) ") == "yes":
            for user in guarding:
                with transaction.commit_on_success():
                    apache_reload = self.process(user)
            if apache_reload:
                restart_master(config.mode, user)
                print "Apache restarted"
