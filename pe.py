#!/usr/bin/env python2

# Problem extractor
#
# copyright (C) 2011-2013 Julian Wergieluk  <julian@wergieluk.com>
# License: GPL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

def printUsage():
    print "Problem extractor (c) Julian Wergieluk 2012-2013."
    print "usage: %s [key file] [problem file 1] [.. [problem file n]] " % sys.argv[0]


import math, sys, os, calendar, re, numpy
from collections import OrderedDict

def readLines(fileName):
    try:
        with open(fileName, "r") as h:
            lines = h.readlines()
        return lines
    except IOError as e:
        print >> sys.stderr, "ERROR: Cannot read the file %s" % (fileName)
        raise SystemExit(1)

def printFile(fileName):
    lines = readLines(fileName)
    for line in lines:
        sys.stdout.write(line)



PROBLEM_LINE=r'\s*^(\\problem{)(.*)(\s*})(.*)'     # TODO: Take only the first } encoutered 
SOLUTION_LINE=r'\s*^\\solution(.*)'

class Problems: 
    def __init__(self):
       self.problems=OrderedDict()
       self.keys=[]
       self.cmds=[]
       self.ids=[]
       self.tags=[]
       self.fmt_problem_begin = "\\problem{%s} "
       self.fmt_problem_end = ""
       self.fmt_solution_begin = "\\solution "
       self.fmt_solution_end = ""

    def processCommands(self, keyList):
        for k in keyList:
            k=k.strip()
            cmd=k.split(" ")[0].lower()
            if len(cmd)==0: 
                continue
            if cmd[0]=="#":
                continue
            args=" ".join(k.split(" ")[1:])
            if len(cmd)>0:
                self.cmds.append(cmd)
                self.keys.append(args)

    def processTex(self, tex):
        lines=readLines(tex)
        probName=""
        probBody=""
        probSolution=""
        probId=""
        probTags=[]
        probImported=0

        for line in lines: 
            line=line.strip()

            if re.search(r'\\chapter', line, re.UNICODE)!=None:
                continue

            if re.search(r'\\section', line, re.UNICODE)!=None:
                continue

            if re.search(r'\\subsection', line, re.UNICODE)!=None:
                continue

            if re.search(r'^%', line, re.UNICODE)!=None:
                continue

            match = re.search(PROBLEM_LINE, line, re.UNICODE)
            if match != None: 
                if match.group(2) != probName and probName!="":
                    if probName in self.problems.keys():
                        print >> sys.stderr, "WARNING: The key \"%s\" already in the database!" % (probName)
                    self.problems[probName] = [probBody, probSolution]
                    probImported=probImported+1

                probName=match.group(2).strip()     # WARNING: removed .lower()
                probBody=match.group(4)             # line # TODO   encoded name of the problem
                probSolution=""
                continue

            match = re.search(SOLUTION_LINE, line, re.UNICODE)
            if match != None: 
                if len(match.group(1))>0:
                    probSolution = match.group(1)       # line
                else:
                    probSolution = "\n"
                continue

            if len(probSolution) == 0:
                probBody = '\n'.join([probBody, line])
            else:
                probSolution = '\n'.join([probSolution, line])

        if probName!="":
            if probName in self.problems.keys():
                print >> sys.stderr, "WARNING: The key \"%s\" already in the database!" % (probName)
            self.problems[probName] = [probBody, probSolution]
            probImported=probImported+1
	sys.stderr.write("%% INFO: %d problems imported from %s.\n" % (probImported, tex))

    def printProblems(self):
        for i in range(len(self.cmds)):
            cmd=self.cmds[i]
            key=self.keys[i]
            if cmd=="fpb":
                self.fmt_problem_begin = key.strip()
            if cmd=="fpe":
                self.fmt_problem_end = key.strip()
            if cmd=="fsb":
                self.fmt_solution_begin = key.strip()
            if cmd=="fse":
                self.fmt_solution_end = key.strip()
            if cmd=="sse":
                print "\\section*{%s}" % (key)
            if cmd=="sss":
                print "\\subsection*{%s}" % (key)
            if cmd=="tex":
                print key
            if cmd=="input":
                printFile(key)
            if cmd=="random":
                rng = numpy.random.RandomState()
                random_key = rng.choice(self.problems.keys())
                while len( self.problems[random_key][1])>0:
                    random_key = rng.choice(self.problems.keys())
                print self.fmt_problem_begin % (random_key)
                print self.problems[random_key][0]
                print self.fmt_problem_end
                print self.fmt_solution_begin
                print self.problems[random_key][1]
                print self.fmt_solution_end
            if cmd=="p" or cmd=="s":
#                key=key.lower()
                if not key in self.problems.keys():
                    print self.fmt_problem_begin % ( key+" NOT FOUND!!"  )
                    print self.fmt_problem_end
                    sys.stderr.write("%% ERROR: Problem not found: %s\n" % (key))
                    continue
                if cmd=="p":
                    sys.stdout.write( self.fmt_problem_begin % (key) )      # does not print \n at the end of line
                    print self.problems[key][0]
                    print self.fmt_problem_end
                if cmd=="s":
                    sys.stdout.write( self.fmt_problem_begin % (key) )
                    print self.problems[key][0]
                    print self.fmt_problem_end
                    print self.fmt_solution_begin
                    print self.problems[key][1]
                    print self.fmt_solution_end
            if cmd=="info":
                self.printSummary()

            
    def printSummary(self):
        sys.stderr.write("%% INFO: %d Problems in the datebase.\n" % (len(self.problems.keys())) )
        for i in range(len(self.problems.keys())):
            sys.stderr.write("%% %d. %s\n" % (i, self.problems.keys()[i]))



if __name__ == "__main__":

    db=Problems()
    
    if len(sys.argv)<3:
        printUsage()
        sys.exit()

    db.processCommands(readLines(sys.argv[1]))

    for f in sys.argv[2:]:
        db.processTex(f)
        
    db.printProblems()

