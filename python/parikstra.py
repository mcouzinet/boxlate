#!/usr/bin/env python

__author__ = "Gawen Arab"
__copyright__ = "Copyright 2012, Gawen Arab"
__credits__ = ["Gawen Arab"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Gawen Arab"
__email__ = "g@wenarab.com"
__status__ = "Production"

import bs4
import requests
import json
import urlparse
import urllib
import datetime
import time
import functools
import sys

def listify(f):
    @functools.wraps(f)
    def wrapper(*kargs, **kwargs):
        return list(f(*kargs, **kwargs))
    return wrapper

def dictify(f):
    @functools.wraps(f)
    def wrapper(*kargs, **kwargs):
        return dict(f(*kargs, **kwargs))
    return wrapper

class Point(object):
    class NoResult(Exception):  pass
    class MoreThanOneResult(Exception): pass

    def __new__(cls, o):
        if isinstance(o, cls):
            return o

        if isinstance(o, basestring):
            ret = cls.search(o)

            if len(ret) == 0:
                raise cls.NoResult()

            return ret[0]

        o = o if o is not None else {}

        self = super(Point, cls).__new__(cls)

        o.pop("search", None)
        for k, v in o.iteritems():
            setattr(self, k, v)

        return self

    def __repr__(self):
        return "<Point %r (%s)>" % (self.name, self.externalCode, )

    @classmethod
    def search(self, word):
        url = "searchPoints/" + urllib.quote(word)
        req = API._rest_req(url)
        req = json.loads(req.text)

        ret = [Point(i) for i in req["list"]]
        return ret

    def _to_rest(self, prefix = None):
        fields = (
            "name",
            "type",
            "city",
            "coordX",
            "coordY",
            "externalCode",
            "cityCode",
            "typeLabel",
        )

        @dictify
        def iterate():
            for k in fields:
                yield (k, getattr(self, k, ""))
       
        ret = iterate()

        if prefix:
            ret[""] = ret.pop("name")

            @dictify
            def transform():
                for k, v in ret.iteritems():
                    k = prefix + (k[0].upper() + k[1:] if k else "")

                    yield (k, v)

            ret = transform()

        return ret

    def to(self, end, *kargs, **kwargs):
        return Itinerary(
            start = self,
            end = end,

            *kargs,
            **kwargs
        )

    def from_(self, start, *kargs, **kwargs):
        return Itinerary(
            start = start,
            end = self,

            *kargs,
            **kwargs
        )

class Itinerary(object):
    TRANSPORTS = (
        "train",
        "rer",
        "metro",
        "bus",
        "tram",
    )

    WALK_SPEEDS = {
        "bad": 0,
        "normal": 1,
        "good": 2,
    }

    def __new__(cls, start, end = None, date = None, via = None, walk_speed = None, with_transport = None, without_transport = None,sens = None):

        if isinstance(start, cls):
            return start

        def datetime_now_floor_5min():
            now = datetime.datetime.now()
            now -= datetime.timedelta(
                minutes = now.minute % 5,
                seconds = now.second,
                microseconds = now.microsecond,
            )
            now += datetime.timedelta(minutes = 5)
            return now

        date = date if date is not None else datetime_now_floor_5min()
        walk_speed = walk_speed if walk_speed is not None else "normal"
        sens = sens if sens is not None else -1
        
        assert walk_speed in cls.WALK_SPEEDS

        if with_transport:
            transports = set(with_transport)

        else:
            transports = set(cls.TRANSPORTS)
        
        if without_transport:
            for i in without_transport:
                transports.remove(i)
        
        for transport in transports:
            assert transport in cls.TRANSPORTS

        data = {}
        
        data["id"] = ""

        # Points
        data.update(Point(start)._to_rest(prefix = "departure"))
        data.update(Point(end)._to_rest(prefix = "arrival"))
        data.update(Point(via)._to_rest(prefix = "via"))

        # Date
        data["dateFormat"] = "dd/MM/yyyy"
        data["date"] = date.strftime("%d/%m/%Y")
        data["hour"] = str(date.hour)
        data["min"] = str(date.minute)

        # Transports
        for transport in cls.TRANSPORTS:
            enabled = transport in transports
            data[transport] = "on" if enabled else "off"
            data["_" + transport] = "true" if enabled else "false"

        # Walk speed
        data["walk_speed"] = cls.WALK_SPEEDS[walk_speed]
        
        # misc TODO
        data["sens"] = str(sens)
        data["moreCriterions"] = "false"
        data["spcar"] = "\xc3\xa2"
        data["hpx"] = "1"
        data["hat"] = "1"
        data["L"] = "0"
        data["submitSearchItinerary"] = ""
        data["ajid"] = "14_"    # XXX TODO
        data["_"] = int(time.time() * 1000)

        req = API._rest_req("/stif_web_carto/comp/itinerary/search.html", params = data)
        req = req.text

        ret = []

        # BS Parse
        req = bs4.BeautifulSoup(req)
        req = req.find(id = "itinerariesResult")
 
        for result in req.find_all("table"):
            self = super(Itinerary, cls).__new__(cls)

            self.type = result.find_all("td")[0].find("a").text.strip()
            self.duration = API._parse_duration(result.find_all("td")[1].text.split(":", 1)[1].strip())

            # Departure - Arrival
            dep_arr = result.find("tr", attrs = {"class": "hourDeparture"})
            dep_arr = dep_arr.find_all("td")[0]
            dep_arr = dep_arr.text.split(">", 1)
            
            @listify
            def iterate():
                now = datetime.datetime.now()

                for i in dep_arr:
                    i = i.split(":", 1)[1].strip()
                    i = datetime.datetime.strptime(i, "%H:%M")
                    i = i.replace(
                        year = now.year,
                        month = now.month,
                        day = now.day,
                    )

                    yield i

            dep_arr = iterate()

            self.departure = dep_arr[0]
            self.arrival = dep_arr[1]

            # Zone
            zone = result.find("tr", attrs = {"class": "hourDeparture"})
            zone = zone.find_all("td")[1]
            zone = zone.find("strong")
            zone = zone.text.split("-")
            zone = [int(i.strip()) for i in zone]

            self.zone = zone

            # Journey URL
            journey_url = result.find("a")["href"]
            journey_url = "/stif_web_carto/comp/itinerary/search.html" + journey_url
            self.journey_url = journey_url

            ret.append(self)

        return ret

    def __iter__(self):
        return iter(self.steps)

    @property
    def steps(self):
        req = API._rest_req(self.journey_url)
        req = req.text

        req = bs4.BeautifulSoup(req)

        req = req.find(id="scrollResultTable")
        req = req.find("table")
        req = req.find_all("tr", recursive = False)

        def iterate_steps(steps):
            it = iter(steps)

            while True:
                head = it.next()
                try:
                    details = it.next()

                except StopIteration:
                    details = None

                yield (head, details)

                if not details:
                    break

        # Parse
        steps = []
        for step, detail in iterate_steps(req):
            hour = step.find_all("td")[0]
            hour = hour.text.strip()

            step_name = step.find_all("td")[2]
            step_name = step_name.find("strong")
            step_name = step_name.text.strip()

            # Depart
            if step_name[0] == "D" and step_name[2:6] == "part":
                step_type = "departure"
                step_name = step_name.split(":", 1)[1].strip()

            # Arrivee
            elif step_name.startswith(u"Arriv"):
                step_type = "arrival"
                step_name = step_name.split(":", 1)[1].strip()

            else:
                step_type = "step"

            # Details
            line = None
            line_info = None
            direction = None
            walk_duration = None
            wait_duration = None

            if detail:
                detail = detail.find_all("td")[2]
                detail_table = detail.find("table")

                if detail_table:
                    line = detail_table.find("td")
                    line1 = [i["alt"] for i in line.find_all("img", recursive = False)]
                    line2 = [i.text.strip() for i in line.find_all("div")]
                    line = line1 + line2
                    
                    line_detail = detail_table.find_all("td")[1]
                    line_detail = line_detail.find("p")
                    line_detail = line_detail.text.strip()
                    line_detail = line_detail.split("\n")

                    line_info = " ".join([i.strip() for i in line_detail[:-1]])
                    
                    if line_detail[-1].strip().startswith("Direction"):
                        direction = line_detail[-1].strip()[len("Direction"):].strip()

                else:
                    alts = ("Marche", "Attente", )

                    durations = ((alt, detail.find("img", alt = alt)) for alt in alts)
                    durations = ((alt, API._parse_duration(dur.next_sibling.next_sibling.text.strip())) for alt, dur in durations if dur)

                    durations = dict(durations)

                    walk_duration = durations.get("Marche", None)
                    wait_duration = durations.get("Attente", None)

            step = Step.build(
                time = hour,
                type = step_type,
                name = step_name,
                line = line,
                line_info = line_info,
                direction = direction,
                walk_duration = walk_duration,
                wait_duration = wait_duration,
            )

            steps.append(step)

        # Set previous and next step

        def iterate_step():
            previous = None
            next = None
            it = iter(steps)

            try:
                step = it.next()

            except StopIteration:
                step = None

            while step:
                try:
                    next = it.next()

                except StopIteration:
                    next = None

                yield (previous, step, next)

                previous = step
                step = next

        for previous, step, next in iterate_step():
            step.previous = previous
            step.next = next

        return Steps(steps)

    def __repr__(self):
        return "<Itinerary %r (%s)>" % (self.type, self.duration, )

class Steps(list):
    def __init__(self, steps):
        super(Steps, self).__init__(steps)

class Step(object):
    @classmethod
    def build(cls, **kwargs):
        walk_step = kwargs.get("walk_duration", None) or kwargs.get("wait_duration", None)

        step_cls = WalkStep if walk_step else TransportStep

        self = step_cls()

        self.previous = None
        self.next = None

        for k, v in kwargs.iteritems():
            setattr(self, "_" + k, v)

        return self

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def time(self):
        return self._time

class TransportStep(Step):
    @property
    def line(self):
        return self._line

    @property
    def direction(self):
        return self._direction

    def __repr__(self):
        return "<TransportStep %r direction %r @ %s>" % (self.name, self.direction, self.time, )

class WalkStep(Step):
    @property
    def walk_duration(self):
        return self._walk_duration

    @property
    def wait_duration(self):
        return self._wait_duration

    def __repr__(self):
        return "<WalkStep in %r (walk: %s, wait: %s) @ %s>" % (self.name, self.walk_duration, self.wait_duration, self.time, )

class API(object):
    verbose = False

    def __init__(self):
        super(API, self).__init__()

    @classmethod
    def _rest_req(cls, path, **kwargs):
        if cls.verbose:
            kwargs["config"] = {
                "verbose": sys.stderr,
            }

        return requests.get(urlparse.urljoin("http://www.vianavigo.com/stif_web_carto/rest/", path), **kwargs)

    @staticmethod
    def _parse_duration(d):
        assert d.endswith("min")

        d = d.replace(" min", "")

        d = d.split("h")
        if len(d) == 1:
            ret = datetime.timedelta(minutes = int(d[0]))

        else:
            ret = datetime.timedelta(hours = int(d[0]), minutes = int(d[1]))

        return ret


def main():
    import optparse

    parser = optparse.OptionParser()
    parser.add_option("-d", "--departure", default = None, help = "Departure")
    parser.add_option("-a", "--arrival", default = None, help = "Arrival")
    parser.add_option("-v", "--verbose", default = False, action = "store_true", help = "Verbosify")

    (options, args) = parser.parse_args()

    departure = options.departure
    arrival = options.arrival

    assert departure is not None, "Please set a departure."
    assert arrival is not None, "Please set an arrival."

    API.verbose = options.verbose

    itineraries = Point(departure).to(arrival)

    for i, itinerary in enumerate(itineraries):
        print "*** Itinerary #%d (%s => %s)" % (i + 1, itinerary.departure, itinerary.arrival, )
        print " - Type: %s" % (itinerary.type, )
        print " - Duration: %s" % (itinerary.duration, )
        print " - Zones: %s" % (itinerary.zone, )
        print

    itinerary = None
    while not itinerary:
        i = raw_input("Which one (1-%s) ? " % (len(itineraries), ))
        i = int(i) - 1

        try:
            if i < 0:
                raise IndexError()

            itinerary = itineraries[i]

        except IndexError:
            print "ERROR: bad index value"
            print

    print "*" * 80
    print "*** Itinerary %s" % (itinerary.type, )

    for i, step in enumerate(itinerary):
        print "%d." % (i + 1),
        
        if step.type == "departure":
            print "At %s, from %s" % (step.time, step.name, )

        elif step.type == "arrival":
            print "Here you go: %s" % (step.name, )
            continue

        else:
            print "At %s (%s)" % (step.name, step.time, )

        if isinstance(step, WalkStep):
            if step.walk_duration:
                print "Walk to %s for %s" % ("%s (%s)" % (step.next._line_info, step.next.name, ) if step.next._line_info else step.next.name, step.walk_duration, )

            if step.wait_duration:
                print "Wait for %s" % (step.wait_duration, )

        else:
            print "Take %s, direction %s" % (step._line_info, step.direction, )

            if step.next:
                print "Stop at %s" % (step.next.name, )

        print

if __name__ == "__main__":
    main()

