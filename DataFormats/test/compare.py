#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Kappa file check

This is a very specialized version of compareFiles that checks a Kappa
file for errors and inconsistencies:
- Trees: Events, Lumis
- Lumis: Provenance, Metadata, 
- Events
- Beide:
  - Classes like defined
  
"""

import ROOT
import sys

ROOT.gSystem.Load('libKappa')

def p(s):
    print "D", s

def main():
    global opt_all
    if len(sys.argv) < 2:
        print "Usage:", sys.argv[0], "file1.root file2.root"
        print "2 files are required!"
        exit(2)
    inputFile1 = ROOT.TFile(sys.argv[1])
    #inputFile2 = ROOT.TFile(sys.argv[2])
    p(inputFile1.GetName())
    printContent(inputFile1)
    #opt_all = (len(sys.argv) > 3 and sys.argv[3] == "-a")
    exit()
    if compareDir(inputFile1, inputFile2):
        print "The files", inputFile1.GetName(), "and", inputFile2.GetName(), "are"
        print "identical."
        exit(0)
    else:
        print "The files", inputFile1.GetName(), "and", inputFile2.GetName(), "are"
        print "NOT identical."
        exit(1)

def printContent(file):
    classes = {}
    trees = file.GetListOfKeys()
    print "\n{0:=<70}".format("Trees (%d, Tree::Branch (Class))  " % len([t.GetName() for t in trees]))
    for key in trees:
        
        tree = file.Get(key.GetName())
        print "\n{0:-<70}".format(key.GetName() + " ")
        branches = sorted([b.GetName() for b in tree.GetListOfBranches()])
        #print "Branches (Class):"
        for b in branches:
            branch = tree.GetBranch(b)
            branchClass = branch.GetClassName()
            if "vector" in branchClass:
                if branchClass not in classes:
                    classes[branchClass[7:-1]] = branch
                branchClass = branchClass[7:-1].replace("Vertex", "Vertice") + "s"
                print "  %s::%s (%s = %s) " % (tree.GetName(), branch.GetName(), branchClass, branch.GetClassName())
            else:
                if branchClass not in classes:
                    classes[branchClass] = branch
                print "  %s::%s (%s) " % (tree.GetName(), branch.GetName(), branchClass)
        
    print "\n{0:=<70}".format("Classes ")
    for cls, branch in classes.items():
        print "\n{0:_<70}".format("_ " + cls + " ")
        
        for b in branch.GetListOfBranches():
            if 'K' == b.GetName()[0]:
                print b.GetName()
            print "{0: <45}".format("  " + cls + " " + b.GetName().replace(branch.GetName()+".", "")) #, 0, "+-", 0
        

def compareDir(directory1, directory2):
    result = True
    for i in directory2.GetListOfKeys():
        obj = directory1.Get(i.GetName())
        obj2 = directory2.Get(i.GetName())
        p(i.GetName())
        if not obj:
            print "Object %s of type %s in %s is not available in first file" % (i.GetName(), obj2.IsA().GetName(), directory2.GetPath().split(":")[1])
            if not opt_all:
                return False
            result = False
    for i in directory1.GetListOfKeys():
        obj = directory1.Get(i.GetName())
        obj2 = directory2.Get(i.GetName())
        if not obj2:
            print "Object %s of type %s in %s is not available in second file" % (i.GetName(), obj.IsA().GetName(), directory1.GetPath().split(":")[1])
            if not opt_all:
                return False
            result = False
            continue
        identified = False
        if obj.IsA().GetName() == "TDirectoryFile":
            identified = True
            if not compareDir(directory1.Get(i.GetName()), directory2.Get(i.GetName())):
                if not opt_all:
                    return False
                result = False
        if obj.IsA().GetName() == "TTree":
            identified = True
            if not compareNtuple(directory1, directory2, i.GetName()):
                if not opt_all:
                    return False
                result = False
        if not identified:
            print "WARNING: %s of type %s in %s has not been checked" % (i.GetName(), obj.IsA().GetName(), directory1.GetPath().split(":")[1])
    return result


def compareNtuple(directory1, directory2, ntupleID):
    result = True
    ntuple1 = directory1.Get(ntupleID)
    ntuple2 = directory2.Get(ntupleID)
    ntuple1.GetEntry(2)
    ntuple2.GetEntry(2)
    leaves1 = ntuple1.GetListOfLeaves()
    leaves2 = ntuple2.GetListOfLeaves()
    nleaves1 = leaves1.GetEntriesFast()
    nleaves2 = leaves2.GetEntriesFast()
    nevts1 = ntuple1.GetEntries()
    nevts2 = ntuple1.GetEntries()
    branches = [b.GetName() for b in leaves1]
    print branches
    exit()
    if nleaves1 != nleaves2:
        print "different number of leaves!"
        print "A", ntuple1.GetName(), nleaves1, leaves1
        print "B", ntuple2.GetName(), nleaves2, leaves2
        for l in leaves1:
            print "  ", l.GetName()
        if not opt_all:
            return False
        result = False
    return False

    for i in range(nleaves1):
        if leaves1.UncheckedAt(i).GetName() != leaves2.UncheckedAt(i).GetName():
            print "different leaf name:", leaves1.UncheckedAt(i).GetName(), leaves2.UncheckedAt(i).GetName()
            if not opt_all:
                return False
            result = False
    if nevts1 != nevts2:
        print "different number of events"
        if not opt_all:
            return False
        result = False
    nevts = min(nevts1, nevts2)
    for n in range(nevts):
        if n % 1000 == 0:
            print "\rEvent %d/%d (%1.1f%%)" % (n, nevts, n * 100. / nevts),
        ntuple1.GetEntry(n)
        ntuple2.GetEntry(n)
        for i in range(nleaves1):
            if leaves1.UncheckedAt(i).GetValue() != leaves2.UncheckedAt(i).GetValue():
                print "different leaf value:", leaves1.UncheckedAt(i).GetValue(), leaves2.UncheckedAt(i).GetValue(),
                print "for name", leaves1.UncheckedAt(i).GetName()
                if not opt_all:
                    return False
                result = False
    return result

if __name__ == "__main__":
    main()
