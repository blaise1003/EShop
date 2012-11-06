# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext_lazy as _, ungettext


class HumanizeTimes(object):
    
    def humanizeTimeDiff(self, timeDiff = None):
        """
        Returns a humanized string representing time difference
        between now() and the input timestamp.
    
        Output:
        4 days 5 hours returns '4 days and 5 hours'
        0 days 4 hours 3 minutes returns '4 hours and 3 minutes', etc...
        """

        days = timeDiff.days
        hours = timeDiff.seconds / 3600
        minutes = timeDiff.seconds % (3600 / 60)

        one_minute = datetime.timedelta(0, 60, 0)
        if timeDiff < one_minute:
            return _(u"just now")

        typed_diff = []
        if days > 0:
            typed_diff.append(ungettext(
                "%(days)s day",
                "%(days)s days",
                days
            ) % {'days': days})
        if hours > 0:
            typed_diff.append(ungettext(
                "%(hours)s hour",
                "%(hours)s hours",
                hours
            ) % {'hours': hours})
        if minutes > 0:
            typed_diff.append(ungettext(
                "%(minutes)s minute",
                "%(minutes)s minutes",
                minutes
            ) % {'minutes': minutes})

        # create date string
        td_string = ''
        if len(typed_diff) > 1:
            td_string = _(u"%(heads)s and %(tail)s") % {
                'heads': u", ".join(typed_diff[:-1]), 'tail': typed_diff[-1] }
        else:
            td_string = typed_diff[0]
        return td_string
    
    def now(self, timestamp):
        if isinstance(timestamp, datetime.datetime):
            now = datetime.datetime.utcnow()
        elif isinstance(timestamp, datetime.date):
            now = datetime.datetime.utcnow().date()
        return now
        
    def humanizeTimeDiffAgo(self, timestamp = None):
        now = self.now(timestamp)
        timeDiff = now - timestamp
        td_string = self.humanizeTimeDiff(timeDiff)
        return _(u"%(diff)s ago") % {'diff': td_string}

    def humanizeTimeDiffLeft(self, timestamp = None):
        now = self.now(timestamp)
        timeDiff = timestamp - now
        td_string = self.humanizeTimeDiff(timeDiff)
        return _(u"%(diff)s left") % {'diff': td_string}