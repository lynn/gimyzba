#!/usr/bin/env python

# Lojban gismu candidate score evaluation script
# Version 0.5

# Copyright 2014 Riley Martinez-Lynch, except where
# Copyright 2012 Arnt Richard Johansen.
# Distributed under the terms of the GPL v3.

# Usage:
#
#   python gismu_score.py -o scores.data uan rakan ekspekt esper predpologa mulud
#   python gismu_best.py < scores.data
#

import platform
import sys

from marshal import load

from gismu_utils import GismuMatcher

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main(scores, gismus):

    log("Sorting scores...")
    scores.sort(lambda x,y:cmp(y[0], x[0]))

    log("")
    log("10 first gismu candidates are:")
    log("")
    for record in scores[:10]:
        log(record)

    log("")
    log("Excluding candidates similar to existing gismu...")
    matcher = GismuMatcher(gismus)
    for (score, candidate, _) in scores:
        gismu = matcher.find_similar_gismu(candidate)
        if gismu == None:
            log("The winner is....\n")
            print(candidate.upper())
            log("")
            break
        else:
            log("Candidate '%s' too much like gismu '%s'." % (candidate, gismu))
    else:
        log("No suitable candidates in top 10 scores.")

if __name__ == '__main__':

    gismu_path = 'gismu-list.txt'
    log("Reading list of gismu... ")
    gismus = [line.strip() for line in file(gismu_path)]

    log("Loading scores... ",)
    scores = load(sys.stdin)
    log("%d scores loaded." % len(scores))

    main(scores, gismus)

