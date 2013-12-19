#!/usr/bin/env python

import BaseHTTPServer
import parikstra
import logging
import optparse
import urllib
import urlparse
import traceback
import datetime
import json
import time

logger = logging.getLogger()

class ParikstraRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse arguments
            params = urlparse.urlparse(self.path).query
            params = urlparse.parse_qs(params)

            # Get arguments
            from_ = params["from"][0]
            to = params["to"][0]
            date = params.get("date", [None])[0]
            walk_speed = params.get("walk_speed", [None])[0]
            with_transport = params.get("with_transport", [None])[0]
            without_transport = params.get("without_transport", [None])[0]
            sens = params.get("sens", [None])[0]

            # Deserialize arguments
            if date is not None:
                date = datetime.datetime.fromtimestamp(int(date))

            if with_transport is not None:
                with_transport = with_transport.split(",")
            
            if without_transport is not None:
                without_transport = without_transport.split(",")

            # Calculate points
            from_ = parikstra.Point(from_)
            to = parikstra.Point(to)

            itis = parikstra.Itinerary(
                start = from_,
                end = to,
                date = date,
                walk_speed = walk_speed,
                with_transport = with_transport,
                without_transport = without_transport,
                sens = sens,
            )

            # Generate output
            r = []
            for i, iti in enumerate(itis):
                s = {}
                s["type"] = iti.type
                s["duration"] = iti.duration.seconds
                s["steps"] = []
                for j, step in enumerate(itis[i]):
                    t = {}

                    t["type"] = step.type
                    t["time"] = step.time
                    t["name"] = step.name
                    if isinstance(step, parikstra.WalkStep):
                        t["wait"] = step.wait_duration.seconds if step.wait_duration else None
                        t["walk"] = step.walk_duration.seconds if step.walk_duration else None

                    if isinstance(step, parikstra.TransportStep):
                        t["direction"] = step.direction
                        t["line"] = step.line

                    s["steps"].append(t)

                r.append(s)
            
            r = json.dumps(r)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(r)

        except Exception, e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            self.wfile.write("%s" % (traceback.format_exc(), ))

def main():
    logging.basicConfig()
    parser = optparse.OptionParser()
    parser.add_option("-b", "--bind", default = ":8080", help = "Bind. (default: :80)")
    parser.add_option("-v", "--verbose", default = False, action = "store_true")
    options, args = parser.parse_args()
    
    logging.getLogger().setLevel(logging.DEBUG if options.verbose else logging.INFO)
    
    bind_addr = options.bind

    if ":" in bind_addr:
        bind_addr = bind_addr.split(":")

    else:
        bind_addr = ("", bind_addr)

    bind_addr = (bind_addr[0], int(bind_addr[1]))

    logger.debug("listening on %s:%d." % (bind_addr[0], bind_addr[1], ))
    server = BaseHTTPServer.HTTPServer(bind_addr, ParikstraRequestHandler)

    logger.info("serving")
    server.serve_forever()

if __name__ == "__main__":
    main()

