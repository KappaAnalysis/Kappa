#!/bin/python  
#/usr/bin/env python
# -*- coding: utf8 -*-

""" Kappa test script

This allows to test Kappa (both the data format and the producers) in
all supported versions of CMSSW and with all relevant config files.
Each test case needs a config file with these comments:
# Kappa test: CMSSW X.Y.Z, A.B.C
# Kappa test: scram arch 
# Kappa test: checkout script scriptname.[sh|py]
# Kappa test: output filename.root (auto, Zeile mit kappa)
# Kappa test: compare /path/to/test/filename.root (auto: cfgname: ordner_name.root)

Checks once: make, classes.UP
Checks per case: setup, checkout, scram, python, cmsRun, output, root output, compare output
"""

import os
import sys
import glob
import subprocess
import copy

groupConfigsToBeChecked = [
    "Skimming/zjet/x.py",
    "Skimming/higgsTauTau/kSkimming_cfg.py",
]
compareFilesPath = '/storage/6/berger/kappatest/'

kappaPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def main(args):
    print "Collect configs from %s ..." % kappaPath
    configNames = collectConfigs(kappaPath)
    #print "DEBUG: These configs are read:", configs
    print "\nParse %d configs ..." % len(configNames)
    configs = parseConfigs(configNames)
    print "\nTesting configs ..."
    for name in sorted(configs):
        preCheck(name, configs[name])
    cases = expandCases(configs)

    if not printPreCheck(configs):
        # the program should always run up to here, fatal errors only afterwards
        if (raw_input("Not all test cases can be fully tested. Do you want to run all possible tests (%d)? [yes]\n" % len(cases))[:1] or 'y') != 'y':
            exit()

    print "\nTesting %d cases ..." % len(cases)
    for name, i in zip(sorted(cases), range(len(cases))) :
        print "- Case %d/%d: %s" % (i+1, len(cases), name)
        testCase(cases[name])
    print "Done."


def collectConfigs(basePath, configList=None):
    """Get list of configs to be run for the test"""
    if configList is None:
        configList = glob.glob(basePath + "/Skimming/examples/skim_tutorial*.py")
        configList += [os.path.join(basePath, p) for p in groupConfigsToBeChecked]
    for config in configList:
        if not os.path.exists(config):
            print "- Warning: No such config file:", config, "(skipped!)"
            configList.remove(config)
    return configList

def collectVersions(cases):
    result = set()
    for case in cases.values():
        if 'CMSSW' in case and case['CMSSW']:
            result |= set(case['CMSSW'])
    return result

def niceVersion(version):
    return version.replace('_patch', '-p').replace('_', '.')

def parseConfigs(configs, kappaCommentIdentifier='Kappa test:'):
    """Parse list of configs for CMSSW version, scram arch and checkout script
    
    Returns a dictionary for each config
    """
    result = {}
    for config in configs:
        name = config.split('/')[-1].replace(".py", "")
        result[name] = {'config': config}
        # parse config file
        with open(config) as f:
            for line in f:
                if kappaCommentIdentifier in line:
                    done = False
                    for key in ['CMSSW', 'scram arch', "checkout script", 'output', 'compare']:
                        if key in line:
                            string = line.split(key, 1)[1]
                            if key in ['CMSSW', 'scram arch']:  # lists
                                result[name][key] = [v.strip().replace(".", "_") for v in string.split(',')]
                            else:  # single strings
                                result[name][key] = string.strip()
                            done = True
                    if not done:
                        print "- Warning: {cfg:30}: Unknown 'Kappa test' line: {line}".format(cfg=name, line=line.strip())
                elif 'outputFile' in line:
                    result[name]['output'] = line.split('=', 1)[1].split('root')[0].strip() + 'root'
        # fill missing items to have a complete dictionary
        if 'CMSSW' not in result[name]:
            result[name]['CMSSW'] = []
        if 'scram arch' not in result[name]:
            result[name]['scram arch'] = []
        if 'checkout script' not in result[name]:
            result[name]['checkout script'] = None
        if 'compare' in result[name]:
            if not os.path.exists(result[name]['compare']):
                result[name]['compare'] = False
        else:
            result[name]['compare'] = os.path.join(compareFilesPath,
                "_".join(config.split('/')[-2:]).replace('/', '_').replace('.py', '.root'))
            if not os.path.exists(result[name]['compare']):
                result[name]['compare'] = None
        if 'output' in result[name] and '"' in result[name]['output']:
            result[name]['output'] = False
        result[name]['name'] = name
    return result
    
def preCheck(name, case):
    """Does a quick check if all information is available to run the tests"""
    if not case['CMSSW'] or not case['scram arch']:
        print "- Warning: {cfg:30}: Missing CMSSW and/or scram arch: config can not be tested at all.".format(cfg=name)
    if case['compare'] is False:
        print "- Warning: {cfg:30}: Given compare file does not exist: no result comparision possible.".format(cfg=name)
    if case['checkout script']:
        path = os.path.join(kappaPath, 'Skimming', case['checkout script'])
        if not os.path.exists(path):
            print "- Warning: {cfg:30}: Given checkout script '{script}' does not exist: checkout will fail ({path}).".format(cfg=name, script=case['checkout script'], path=path)
            case['checkout script'] = False
    
def printPreCheck(cases, length=78):
    """Print the results of preCheck in a nice table"""
    success = True
    print "_"*length
    pm = ['\033[91m-\033[0;0m', '\033[92m+\033[0;0m', '\033[92m \033[0;0m']
    print "\033[1mConfig                         OK Arch Checkout Output Compare Versions\033[0;0m"
    for name in sorted(cases):
        case = cases[name]
        ok = (len(case['CMSSW'])
            and len(case['CMSSW']) == len(case['scram arch'])
            and case['checkout script'] is not False
            and bool('output' in case and case['output'])
        )
        print "{name:30} {ok:14} {arch:17} {co:18} {out:18} {comp:15} {ver:3}{vers}".format(name=name, 
            ok=pm[ok],
            arch=pm[(len(case['CMSSW']) == len(case['scram arch']) and len(case['CMSSW']) > 0)],
            ver= '%d:' % len(case['CMSSW']) if len(case['CMSSW'])>0 else '-', 
            vers=", ".join([niceVersion(v) for v in case['CMSSW']]),
            co=pm[bool(case['checkout script']) + 2*bool(case['checkout script'] is None)],
            out=pm[bool('output' in case and case['output'])],
            comp=pm[bool(case['compare'])],
        )
        success = success and ok
    print "=> %s required information available" % ['Not all', 'All'][success]
    versions = collectVersions(cases)
    print "   Required CMSSW versions:", ", ".join([niceVersion(v) for v in versions])
    print "_"*length
    return success

def expandCases(configs):
    cases = {}
    for config in configs.values():
        for i in range(len(config['CMSSW'])):
            name = config['name'] + '_' + config['CMSSW'][i]
            cases[name] = copy.deepcopy(config)
            cases[name]['case'] = name
            cases[name]['CMSSW'] = config['CMSSW'][i]
            cases[name]['scram arch'] = config['scram arch'][i]
    #print "CC", cases
    return cases

def setupCMSSW(version, arch):
    """Setup a given CMSSW version"""
    print "    # setup", version, arch
    print "    cmsrel CMSSW" + version

def testCase(case):
    script = """#!/bin/bash
cd {case}

# setup CMSSW {CMSSW}
{source}
export SCRAM_ARCH={scram arch}
cmsrel CMSSW_{CMSSW} > ../../env.log
cd CMSSW_{CMSSW}/src
cmsenv >> ../../env.log
{checkout script} > ../../recipe.log
scram b -j8 > ../../scram.log

# get your private Kappa to be tested
rm -rf ../../../{case}/CMSSW_{CMSSW}/src/Kappa  # complicated path to prevent accidental removal
rsync -r {kappa} ./ > ../../copy.log
scram b > ../../compile.log

# check and run
python {config} > ../../python.log
cmsRun {config} > ../../cmssw.log

# check output
{no}root -l {output}
{no}compareFiles.py {output} {compare} > compare.log
"""
    filename = case['case'] + "/testscript.sh"
    os.mkdir(case['case'])
    case['source'] = 'ini cmssw' + case['CMSSW'][0]
    case['version'] = niceVersion(case['CMSSW'])
    if not case.get('checkout script', False):
        case['checkout script'] = '# no checkout script'
    if not case.get('output', False):
        case['output'] = '# output name unknown'
        case['no'] = '# '
    else:
        case['no'] = ''

    with open(filename, 'w') as f:
        f.write(script.format(kappa=kappaPath, **case))
    with open(filename) as f:
        for line in f:
            print "   ", line[:-1]
    #subprocess.Popen('testscript.sh')
        
def checkResult():
    result = {
        'env': False, 'scram': False, 'recipe': False, 'compile': False,
        'python'
    }
    for key in result:
        with open('%s.log' % key) as log:
            result[k] = ('successful' in log.read())
        

def printTestResult(result):
    print "Step   Folders  Env  Recipe  Scram  Copy  Compile  Config  cmsRun  Output  Valid  Compare"
    print """Result {names}
    config: {config}
    Version   recipe scram python cmsRun output root compare
    {version} {recipe} {scram} {python} {cmsRun} {
    """

def printResult(case):
    template = """{names}
    config: {config}
    Version   recipe scram python cmsRun output root compare
    {version} {recipe} {scram} {python} {cmsRun} {
    """
    return template.format(**case)

def bash(command):
    print "    bash:", " ".join(command)

if __name__ == "__main__":
    main(sys.argv)  

