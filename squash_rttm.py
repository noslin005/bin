#!/usr/bin/env python3

# This program takes, on STDIN, 
# RTTM v1.3 (https://catalog.ldc.upenn.edu/docs/LDC2004T12/RTTM-format-v13.pdf)
# data and, if the two utterances of the same speaker are within 0.01 seconds
# of each other, it merges the two records and spits it out. Otherwise it 
# spits out the record unchanged

# e.g. given these three lines:
#
# SPEAKER meeting 1 32.58 0.20000000000000284 <NA> <NA> spkr_2 <NA>
# SPEAKER meeting 1 32.78 0.14000000000000057 <NA> <NA> spkr_2 <NA>
# SPEAKER meeting 1 32.92 0.259999999999998 <NA> <NA> spkr_2 <NA>
#
# it would output
# SPEAKER meeting 1 32.58 0.60 <NA> <NA> spkr_2 <NA>

# Typical invocation:
#
#   squash_rttm.py < /tmp/ibm_ES2008a.rttm > /tmp/ibm_ES2008a_squashed.rttm

# To test
#
#   python3 -m unittest squash_rttm.py < /dev/null

import math
import sys
import unittest


class TestRTTMMethods(unittest.TestCase):
    def test_squash_rttm_empty(self):
        self.assertEqual(squash_rttm([]), "")

    def test_squash_rttm_two_decimals(self):
        pre_squashed = [
            "SPEAKER meeting 1       31.69   0.31000000000000014     <NA>    <NA>    Speaker_3       <NA>",
        ]
        squashed = "SPEAKER\tmeeting\t1\t31.69\t0.31\t<NA>\t<NA>\tSpeaker_3\t<NA>\n"
        self.assertEqual(squash_rttm(pre_squashed), squashed)

    def test_squash_rttm_two_lines(self):
        pre_squashed = [
            "SPEAKER meeting 1       31.69   0.31000000000000014     <NA>    <NA>    Speaker_3       <NA>",
            "SPEAKER meeting 1       32.00   0.59000000000000014     <NA>    <NA>    Speaker_3       <NA>",
        ]
        squashed = "SPEAKER\tmeeting\t1\t31.69\t0.90\t<NA>\t<NA>\tSpeaker_3\t<NA>\n"
        self.assertEqual(squash_rttm(pre_squashed), squashed)

    def test_squash_rttm_two_lines_two_speakers(self):
        pre_squashed = [
            "SPEAKER meeting 1       31.69   0.31000000000000014     <NA>    <NA>    Speaker_2       <NA>",
            "SPEAKER meeting 1       32.00   0.59000000000000014     <NA>    <NA>    Speaker_3       <NA>",
        ]
        squashed = "SPEAKER\tmeeting\t1\t31.69\t0.31\t<NA>\t<NA>\tSpeaker_2\t<NA>\n" + \
                   "SPEAKER\tmeeting\t1\t32.00\t0.59\t<NA>\t<NA>\tSpeaker_3\t<NA>\n"
        self.assertEqual(squash_rttm(pre_squashed), squashed)

    def test_squash_rttm_two_lines_one_pause(self):
        pre_squashed = [
            "SPEAKER meeting 1       31.69   0.29000000000000014     <NA>    <NA>    Speaker_3       <NA>",
            "SPEAKER meeting 1       32.00   0.59000000000000014     <NA>    <NA>    Speaker_3       <NA>",
        ]
        squashed = "SPEAKER\tmeeting\t1\t31.69\t0.29\t<NA>\t<NA>\tSpeaker_3\t<NA>\n" + \
                   "SPEAKER\tmeeting\t1\t32.00\t0.59\t<NA>\t<NA>\tSpeaker_3\t<NA>\n"
        self.assertEqual(squash_rttm(pre_squashed), squashed)


def _format_rttm_line(type, file, chnl, tbeg, tdur, ortho, stype, name, conf):
    return ("{}\t{}\t{}\t{:.2f}\t{:.2f}\t{}\t{}\t{}\t{}\n".format(
        type,
        file,
        chnl,
        tbeg,
        tdur,
        ortho,
        stype,
        name,
        conf
    ))


def squash_rttm(rttm_lines):
    o_tbeg = None  # "original" time beginning
    squashed_rttm = ''

    for line in rttm_lines:
        (type, file, chnl, tbeg, tdur, ortho, stype, name, conf) = line.split()
        tbeg = float(tbeg)
        tdur = float(tdur)
        sys.stderr.write("top: {:.2f}\n".format(tdur))
        if o_tbeg is None:
            o_type = type
            o_file = file
            o_chnl = chnl
            o_tbeg = tbeg
            o_tdur = tdur
            o_ortho = ortho
            o_stype = stype
            o_name = name
            o_conf = conf
            sys.stderr.write("initialization: {:.2f}\n".format(o_tdur))
        else:
            if o_name == name and math.isclose(tbeg, (o_tbeg + o_tdur), abs_tol=0.01):
                # collapse the two
                o_tdur += tdur
                sys.stderr.write("collapse: {:.2f}\n".format(o_tdur))
            else:
                # print the line & move on
                squashed_rttm += _format_rttm_line(o_type, o_file, o_chnl, o_tbeg, o_tdur, o_ortho, o_stype, o_name,
                                                   o_conf)
                sys.stderr.write("emit: {:.2f}\n".format(o_tdur))
                o_type = type
                o_file = file
                o_chnl = chnl
                o_tbeg = tbeg
                o_tdur = tdur
                o_ortho = ortho
                o_stype = stype
                o_name = name
                o_conf = conf
    if not (o_tbeg is None):
        squashed_rttm += _format_rttm_line(o_type, o_file, o_chnl, o_tbeg, o_tdur, o_ortho, o_stype, o_name, o_conf)
        sys.stderr.write("final_emit: {:.2f}\n".format(o_tdur))
    return (squashed_rttm)


print(squash_rttm(sys.stdin.readlines()))