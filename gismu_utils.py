
# Lojban gismu candidate generation and scoring utilities
# Version 0.5

# Copyright 2014 Riley Martinez-Lynch, except where
# Copyright 2012 Arnt Richard Johansen.
# Distributed under the terms of the GPL v3.

import sys
import re

from functools import reduce
from itertools import chain

C = 'bcdfgjklmnprstvxz'
V = 'aeiou'

CCVCV = [ C, C, V, C, V ]
CVCCV = [ C, V, C, C, V ]

VALID_CC_INITIALS = [
  'bl', 'br',
  'cf', 'ck', 'cl', 'cm', 'cn', 'cp', 'cr', 'ct',
  'dj', 'dr', 'dz',
  'fl', 'fr',
  'gl', 'gr',
  'jb', 'jd', 'jg', 'jm', 'jv',
  'kl', 'kr',
  'ml', 'mr',
  'pl', 'pr',
  'sf', 'sk', 'sl', 'sm', 'sn', 'sp', 'sr', 'st',
  'tc', 'tr', 'ts',
  'vl', 'vr',
  'xl', 'xr',
  'zb', 'zd', 'zg',
  'zm', 'zv'
]

FORBIDDEN_CC  = [ 'cx', 'kx', 'xc', 'xk', 'mz' ]

FORBIDDEN_CCC = [ 'ndj', 'ndz', 'ntc', 'nts' ]

SIBILANT = 'cjsz'
VOICED   = 'bdgjvz'
UNVOICED = 'cfkpstx'

SIMILARITIES = {
  'b':'pv',
  'c':'js',
  'd':'t',
  'f':'pv',
  'g':'kx',
  'j':'cz',
  'k':'gx',
  'l':'r',
  'm':'n',
  'n':'m',
  'p':'bf',
  'r':'l',
  's':'cz',
  't':'d',
  'v':'bf',
  'x':'gk',
  'z':'js'
}

LANGUAGE_WEIGHTS = {

  # Order: Chinese, Hindi, English, Spanish, Russian, Arabic

  '1985'     : (0.360, 0.160, 0.210, 0.110, 0.090, 0.070),
  # http://dag.github.io/cll/4/14

  '1987'     : (0.360, 0.156, 0.208, 0.116, 0.087, 0.073),
  '1994'     : (0.348, 0.194, 0.163, 0.123, 0.088, 0.084),
  # http://www.lojban.org/files/etymology/langstat.94

  '1995'     : (0.347, 0.196, 0.160, 0.123, 0.089, 0.085), # default
  # http://www.lojban.org/files/etymology/langstat.95

  '1999'     : (0.334, 0.195, 0.187, 0.116, 0.081, 0.088)
  # http://www.lojban.org/files/etymology/langstat.99

}

XADD = lambda a,b: [x+y for x in a for y in b]

# LCS implementation adapted from python dynamic programming example at:
#   http://rosettacode.org/wiki/Longest_common_subsequence

def lcs_length(a, b):
    W = len(b)+1
    H = len(a)+1
    matrix = W*H * [0]
    for ix, x in enumerate(a):
        for iy, y in enumerate(b):
            i = ix*W+iy
            matrix[i + W + 1] = matrix[i] + 1 if x == y else max(matrix[i + 1], matrix[i + W])
    return matrix[-1]

class GismuGenerator:

    def __init__(self, c, v, shape_strings):
        self.c = c
        self.v = v
        self.shape_strings = shape_strings

    def iterator(self):
        iterators = [ self.shape_iterator(str) for str in self.shape_strings ]
        return chain(*iterators)

    def shape_iterator(self, shape_string):
        shape = self.shape_for_string(shape_string)
        validator = self.shape_validator(shape_string)
        return filter(validator, reduce(XADD, shape))

    def shape_for_string(self, string):
        shape = []
        for letter in list(string.lower()):
          if letter == 'c':
              shape.append(self.c)
          elif letter == 'v':
              shape.append(self.v)
        return shape

    def shape_validator(self, shape):
        predicates = []
        slen = len(shape)
        for i, c in enumerate(shape[:-1].lower()):
            if c == shape[i+1] == 'c':
                predicates.append(self.validator_for_cc(i))
                if i < slen-2 and shape[i+2] == 'c':
                    predicates.append(self.validator_for_ccc(i))
                if 0 < i < slen-4 and shape[i:i+5] == 'ccvcv':
                    predicates.append(self.invalidator_for_initial_cc(i))
        return self.validator_for_predicates(predicates)

    def validator_for_cc(_, i):
        if i == 0:
            return lambda x: x[:2] in VALID_CC_INITIALS
        else:
            j = i + 1
            return lambda x: x[i] != x[j] and \
              not (x[i] in VOICED   and x[j] in UNVOICED) and \
              not (x[i] in UNVOICED and x[j] in VOICED  ) and \
              not (x[i] in SIBILANT and x[j] in SIBILANT) and \
              x[i:j + 1] not in FORBIDDEN_CC

    def validator_for_ccc(_, i):
        return lambda x: x[i:i+3] not in FORBIDDEN_CCC

    def invalidator_for_initial_cc(_, i):
        return lambda x: x[i:i+2] not in VALID_CC_INITIALS

    def validator_for_predicates(_, predicates):
        return lambda x: all(p(x) for p in predicates)

class GismuScorer:

    def __init__(self, input_words, weights):
        self.input_words = input_words
        self.weights = weights

    def compute_score(self, candidate):
        similarity_scores = self.compute_similarity_scores(candidate)
        weighted_sum = self.calculate_weighted_sum(similarity_scores)
        return weighted_sum, similarity_scores

    def compute_score_with_name(self, candidate):
        ws, ss = self.compute_score(candidate)
        return (ws, candidate, ss)

    def compute_similarity_scores(self, candidate):
      chars = [ x for x in list(candidate) ]
      return [ self.compute_similarity_score(candidate, word) \
               for word in self.input_words ]

    def compute_similarity_score(self, candidate, input_word):
        lcs_len = lcs_length(candidate, input_word)
        if lcs_len < 2:
            score = 0
        elif lcs_len == 2:
            score = self.score_dyad_by_pattern(candidate, input_word)
        else:
            score = lcs_len
        return float(score) / len(input_word)

    def score_dyad_by_pattern(self, candidate, input_word):
        l = len(candidate)
        iw02 = input_word[0::2]
        iw12 = input_word[1::2]
        for i in range(l - 2):
            dyad = candidate[i] + candidate[i + 2]
            if dyad in iw02 or dyad in iw12:
                return 2
        for i in range(l - 1):
            if candidate[i] + candidate[i + 1] in input_word:
                return 2
        return 0

    def calculate_weighted_sum(self, scores):
        # Multiply each score by the given weight, then sum weighted scores
        return sum(map(float.__mul__, scores, self.weights))

class GismuMatcher:

    def __init__(self, gismus, stem_length = 4):
        self.gismus = gismus
        self.stem_length = stem_length

    def find_similar_gismu(self, candidate):
        candidate = candidate.rstrip()
        patterns = map(lambda x:SIMILARITIES.get(x, '.'), candidate)
        # e.g. "rekpa" =~ /l.[gx][bf]./ where . matches NOTHING

        gismu = None
        found_match = False
        for gismu in self.gismus:
            found_match = self.match_gismu(gismu, candidate, patterns)
            if found_match:
                break
        return gismu if found_match else None

    def match_gismu(self, gismu, candidate, structural_patterns):
        return self.match_stem(gismu, candidate) or \
          self.match_structure(gismu, candidate, structural_patterns)

    def match_stem(self, gismu, candidate):
        return candidate[:self.stem_length] == gismu[:self.stem_length]

    # Apply similarity pattern to each position in gismu if others letters equal
    #
    # /PAT/ekpa
    # r/PAT/kpa
    # re/PAT/pa
    # rek/PAT/a
    # rekp/PAT/
    #
    def match_structure(self, gismu, candidate, structural_patterns):
        similar = False
        common_len = min(len(candidate), len(gismu))
        for i in range(common_len):
            if self.strings_match_except(gismu, candidate, i, common_len) and \
              self.match_structural_pattern(gismu[i], structural_patterns[i]):
                similar = True
                break
        return similar

    def strings_match_except(_, x, y, i, j):
      return x[:i] == y[:i] and x[i+1:j] == y[i+1:j]

    def match_structural_pattern(_, letter, pattern):
        if pattern == '.':
            return False
        return letter in pattern

