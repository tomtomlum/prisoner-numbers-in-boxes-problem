#!/usr/bin/python
#
# Author: Tom Lum
# Date Created: July 1, 2022
#
# This is a simulation of the '100 prisoners problem'
# https://en.wikipedia.org/wiki/100_prisoners_problem
#
# After watching a youtube video
# https://youtu.be/iSNsgj1OCLA
# from Veritasium channel
# https://www.youtube.com/c/veritasium
# I decide to create a simulation and see if 'the math checks out'
#
# run command
# clear; py .\pnibp.py

import os, sys, getopt
from textwrap import wrap

from math import isqrt, ceil, floor
import random

class suppress_output:
    def __init__(self, suppress_stdout=False, suppress_stderr=False):
        self.suppress_stdout = suppress_stdout
        self.suppress_stderr = suppress_stderr
        self._stdout = None
        self._stderr = None

    def __enter__(self):
        devnull = open(os.devnull, "w")
        if self.suppress_stdout:
            self._stdout = sys.stdout
            sys.stdout = devnull

        if self.suppress_stderr:
            self._stderr = sys.stderr
            sys.stderr = devnull

    def __exit__(self, *args):
        if self.suppress_stdout:
            sys.stdout = self._stdout
        if self.suppress_stderr:
            sys.stderr = self._stderr

def main(argv):
    # default number of prisoners
    n = 100
    # round up max tries if n is odd
    r=False
    # how many rounds of game
    s=1
    # Print out details
    d=False
    # Print out prisoner win loss
    p=False

    # command line
    help='pnibp.py [-n 100<NumOfPrisoners> -r <RoundUpMaxTriesIfOddNumOfBoxes> -s 1<NumOfRounds> -d <PrintOutGameDetails>] -p <PrintOutPrisonerWinLoss>'
    try:
        opts, args = getopt.getopt(argv,'hn:rs:dp',['num='])
    except getopt.GetoptError:
        print(help)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
        elif opt in ('-n', '--num'):
            n=int(arg)
        elif opt in ('-r'):
            r=True
        elif opt in ('-s'):
            s=int(arg)
        elif opt in ('-d'):
            d=True
        elif opt in ('-p'):
            p=True

    print('WELCOME!!! to the 100 prisoners problem simlution!!!')
    print()

    wcnt=0
    lcnt=0
    round=1
    while round <= s:
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(f'Round {round} of {s}, Number of prisoners is {str(n)}')
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

        # let have some boxes matching number of the prisoners
        boxes = random.sample(range(1, n+1), n)

        # show boxes and numbers, show loops
        printboxes(boxes)
        print()

        loops = findloops(boxes)
        printloops(loops)
        print()

        # let's play the game
        prisonerline = random.sample(range(1, n+1), n)
        prisonerwinloss = [None for i in range(n)]

        for p in prisonerline:
            with suppress_output(suppress_stdout=(not d), suppress_stderr=False):
                prisonerwinloss[p-1] = enterboxroom(p,boxes,r)

        wl = [d['result'] for d in prisonerwinloss]
        if not all(wl):
            print(f'Prisoners LOST the game! Ratio is {sum(wl)/n}')
            lcnt += 1
        else:
            print(f'Prisoners WON the game!')
            wcnt += 1

        if p:
            printwinloss([d['result'] for d in prisonerwinloss])

        print('------------------------------------------------------------')
        print(f'W:{wcnt} L:{lcnt} G:{round} W/L Ratio: {wcnt/round:.0%}/{lcnt/round:.0%}')
        print('------------------------------------------------------------')

        round+=1

def printwinloss(wl):
    # figure out the console width and how many col can fit
    n = len(wl)
    numgridcol=min(isqrt(n),floor(os.get_terminal_size().columns/(2*len(str(n))+3)))
    numgridrow=ceil(n/numgridcol)

    # print out each line with the detected screen width
    for r in range(1,numgridrow+1):
        line = ''
        for c in range(1,numgridcol+1):
            try:
                boxnum = (r-1)*numgridcol+c
                line += str(boxnum).rjust(len(str(n))) + (u'\u2705' if wl[boxnum-1] else u'\u274C')
            except IndexError:
                pass
        print(line)

def printautofit(s,n):
    # figure out the console width and how many col can fit
    numgridcol=min(isqrt(n),floor(os.get_terminal_size().columns/(2*len(str(n))+3)))

    # set up the wrapping args
    wrapargs = {'width':numgridcol * (2*len(str(n))+3)}

    print("\n".join(wrap(text=s, **wrapargs)))

def enterboxroom(prisonernumber,boxes,oddmaxtriesroundup=False):
    # keep check of max tries
    n=len(boxes)
    openedboxcount=1
    maxtries=ceil(n/2) if oddmaxtriesroundup else floor(n/2)
    print(f'Prisoner {prisonernumber} entered the room!!! Max tries is {maxtries}')

    # keep track of prisoner game progress
    openboxesandloops=[[]]
    currboxnum = prisonernumber
    while True:
        # DO
        # open box of the same number
        whatisintheopenbox = boxes[currboxnum-1]
        # update progress
        openboxesandloops[-1].append(whatisintheopenbox)

        # INC(i++)
        openedboxcount += 1
        currboxnum=whatisintheopenbox

        # WHILE (NOT)
        # Nice Job!! W
        if whatisintheopenbox == prisonernumber:
            print('W')
            printloops(openboxesandloops,n)
            print()
            return {'result': True,
                    'details': openboxesandloops}

        # is this GAME OVER for this prisoner?
        if openedboxcount > maxtries:
            print('L')
            printloops(openboxesandloops,n)
            print()
            return {'result': False,
                    'details': openboxesandloops}
        # End of a loop and no luck...
        elif whatisintheopenbox == prisonernumber:
            # new loop
            openboxesandloops.append([])

# find all the number loops
def findloops(boxes):
    loops = []
    i=0

    # start
    for b in range(0,len(boxes)):
        # number has not been visited(marked with negative sign)
        if boxes[b] > 0:
            # new loop found
            loops.append([])

            # do...while
            # skipping the frist actual box number(on the box) for the last
            nextboxnum = boxes[b]
            currboxindex = b
            while True:

                # DO
                # push in the next box number(in the box)
                loops[i].append(nextboxnum)
                # marked it as visited by negating the sign
                boxes[currboxindex] *= -1
                
                # INC(i++)
                # go to the next box
                currboxindex=nextboxnum-1
                # open the next box and see what is inside
                nextboxnum=boxes[nextboxnum-1]

                # WHILE (NOT)
                # oh the next is already visted and loop is completed
                if nextboxnum < 0:
                    break

            # shift the last number to the first through list slicing
            loops[i] = loops[i][-1:] + loops[i][:-1]
            # next box in the line
            i+=1

    # revert the negation marks
    boxes[:] = [-i for i in boxes]

    # returns the result
    return loops

# let there be pretty print for boxes and their numbers in the boxes
def printboxes(boxes):
    print('Boxes:')

    # figure out the console width and how many col can fit
    n = len(boxes)
    numgridcol=min(isqrt(n),floor(os.get_terminal_size().columns/(2*len(str(n))+3)))
    numgridrow=ceil(n/numgridcol)
    print(f'mxn= {str(numgridrow)}x{str(numgridcol)}')

    # print out each line with the detected screen width
    for r in range(1,numgridrow+1):
        line = ''
        for c in range(1,numgridcol+1):
            try:
                boxnum = (r-1)*numgridcol+c
                line += str(boxnum).rjust(len(str(n)))+'[' + str(boxes[boxnum-1]).rjust(len(str(n))) + '] '
            except IndexError:
                pass
        print(line)

# let there be pretty print for loops
def printloops(loops,n=None):
    print('Loops:')
    
    # figure out the console width and how many col can fit
    n = n or sum(len(row) for row in loops)
    indpadlen = len(str(n))+3
    numgridcol=min(isqrt(n),floor(os.get_terminal_size().columns/(2*len(str(n))+3)))

    # set up the wrapping args
    wrapargs = {'width':numgridcol * (2*len(str(n))+3),
                'subsequent_indent':''.rjust(indpadlen),
                'initial_indent':''.rjust(indpadlen)}

    # let's print them loops
    for i in range(0,len(loops)):
        # join numbers in the loop with ->
        # then let text wrap handle it once
        lines = wrap(text='->'.join(str(x) for x in loops[i]), **wrapargs)

        # check if the beginning of each line if it starts with ->, if not that means it needs fixing
        if len(lines) > 1:
            lnum = 1
            while lnum < len(lines):
                # bad line...
                if lines[lnum][indpadlen:2] != '->':
                    # rejoin the rest of lines and move the previous line ending back up to the last -> index
                    rejoinedlines = ''.join(x.lstrip() for x in lines[lnum:])
                    rejoinedlines = lines[lnum-1][lines[lnum-1].rindex('->'):len(lines[lnum-1])] + rejoinedlines

                    # remove the previous line's last -> with whatever left of the partial number at the end
                    lines[lnum-1]=lines[lnum-1][:lines[lnum-1].rindex('->')]

                    # retry text wrap
                    relines = wrap(text=rejoinedlines, **wrapargs)
                    # mend the lines back to a list of lines
                    lines = lines[:lnum] + relines
                lnum += 1

        # strip the space of the 1st line for the loop numbers count print out
        lines[0]=lines[0].lstrip()
        print('['+str(len(loops[i])).rjust(len(str(n)))+'] '+'\n'.join(lines))

# main function call
if __name__ == '__main__':
    main(sys.argv[1:])