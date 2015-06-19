#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Kappa test script

This allows to test Kappa (both the data format and the producers) in
all supported versions of CMSSW and with all relevant config files.
Each test case needs a config file with these comments:
# Kappa test: CMSSW X.Y.Z, A.B.C
# Kappa test: scram arch arch1, arch2
# Kappa test: checkout script scriptname.[sh|py]
# Kappa test: output filename.root (auto, Zeile mit kappa)
# Kappa test: compare /path/to/test/filename.root (auto: cfgname: ordner_name.root)

Checks once: make, classes.UP
Checks per case: setup, checkout, scram, python, cmsRun, output, validate output, compare output

usecases:
check single config file
check current working tree
check current branch heads or other commits
options:
stop after precheck? batch mode
Naming:
- test: a small test snippet that each test case must pass
- config: CMSSW config equipped with 'Kappa test' statements
- case: a test case (1 config, 1 CMSSW version, a series of tests)
Hierarchy:
- main: choose application mode
  - run: run on one Kappa directory (or branch)
    - testcases: one case from configs x CMSSW versions
      - tests: single tests
"""

import os
import sys
import glob
import subprocess
import copy
import time
import shutil

groupConfigsToBeChecked = [
    "Skimming/higgsTauTau/kSkimming_cfg.py",
    "Skimming/higgsTauTau/kSkimming_run2_cfg.py",
    "Skimming/zjet/skim_53_2015-05-13_cfg.py",
    "Skimming/zjet/skim_74_2015-05-18_cfg.py",
]
compareFilesPaths = [
    '/storage/6/berger/kappatest/output/',
    '/nfs/dust/cms/user/jberger/kappatest/output/',
]
compareFilesPath = compareFilesPaths[0]
for p in compareFilesPaths:
    if os.path.exists(p):
        compareFilesPath = p
        break

# get Kappa path relative to this script which is in DataFormats/test
kappaPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def main(args):
    global kappaPath
    # minimal argument parser
    opt = {
        'batchMode': ("-b" in args),
        'dryRun': ("-d" in args),
    }
    sendMailOnFail = ("-s" in args)
    for o in ['-b', '-d', '-s']:
        if o in args:
            args.remove(o)
    if "-h" in args:
        print "Usage: /path/to/script/test.py [config|branch names] [-b (batch mode=no questions)]"
        exit(0)

    # check environment before running dangerous things
    if '/Kappa' in os.path.abspath('.'):
        print "This script should not be run within a Kappa folder as it creates new folders here."
        exit(2)
    if len(glob.glob('./*')):
        print "This script should be run in an empty folder!"
        exit(2)

    # select the run mode and execute it
    results = []
    if len(args) == 1:
        print "Test all default configs in working directory"
        results.append(run(kappaPath, **opt))
    elif args[1][-3:] == '.py':
        print "Test these configs:", args[1:]
        results.append(run(kappaPath, configs=args[1:], **opt))
    else:
        print "Test all default configs in these branches:", ", ".join(args[1:])
        for b in args[1:]:
            print "Test branch '%s':" % b
            cmd = ['git', 'clone', '-b', branch, 'https://github.com/KappaAnalysis/Kappa.git', 'Kappa_%s' % branch]
            kappaPath = os.path.abspath('./Kappa_%s' % branch)
            print " ".join(cmd)
            subprocess.Popen(cmd).wait()
            
            results.append(run(kappaPath, branch=b, commit="Kappa", **opt))
    allOK = all([case.result == 100 for branch in results for case in branch])

    # print results as html (stdout?)
    html = writeHTML(results, allOK)
    htmlfile = 'result.html'
    with open(htmlfile, 'w') as f:
        f.write(html)
    if sendMailOnFail and not allOK:
        sendMail(os.path.abspath('.'))
    print "HTML written to %s, Kappa status:%s ok." % (htmlfile, [' not', ''][allOK])
    return not allOK


def run(kappaPath, configs=None, branch=None, commit=None, batchMode=False, dryRun=False):
    """The main test run function for one working directory or branch"""
    print "Collect configs from %s ..." % kappaPath
    configNames = collectConfigs(kappaPath, configs)

    print "\nParse %d configs ..." % len(configNames)
    configs = parseConfigs(configNames)

    print "\nTesting %d configs ..." % len(configs)
    for name in sorted(configs):
        preCheck(name, configs[name])
    # make test cases from the configs (configs x CMSSW versions)
    cases = expandCases(configs)
    cases = sorted(cases, key=lambda k: k.name)
    cases[0].branch = branch or kappaPath
    cases[0].commit = commit

    if not printPreCheck(configs):
        # the program should always run up to here, fatal errors only afterwards
        if (not batchMode and
            (raw_input("Not all test cases can be fully tested. "
            "Do you want to run all possible tests (%d)? "
            "[yes]\n" % len(cases))[:1] or 'y') != 'y'):
            exit()

    print "\nConfigure %d cases:" % len(cases)
    tests = [
        Arch(), Env(), Recipe(), Scram(), Copy(), Compile(),
        Config(), CmsRun(), Output(), Valid(),
    ]
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s ..." % (i+1, len(cases), case.name),
        case.tasks = copy.deepcopy(tests)
        print ['failed', 'successful'][case.configure()]

    print "\nCheck %d cases:" % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s ..." % (i+1, len(cases), case.name),
        print ['failed', 'successful'][case.check()]

    print "\nWrite test script for %d cases:" % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), case.name)
        case.writeScript()

    print "\nRun %d cases:" % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s ..." % (i+1, len(cases), case.name),
        sys.stdout.flush()
        print ['failed', 'successful', 'untested'][case.run(dryRun) * case.retrieve()]

    print "\nRetrieve results for %d cases:" % len(cases)
    result = []
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), case.name)
        result.append(case.getResult())
    return cases



def collectConfigs(basePath, configList=None):
    """Get list of configs to be run for the test"""
    if configList is None:
        configList = glob.glob(basePath + "/Skimming/examples/skim_tutorial*.py")
        configList += [os.path.join(basePath, p) for p in groupConfigsToBeChecked]
    for config in configList:
        if not os.path.exists(config):
            print "- Warning: No such config file:", config, "(skipped!)"
            configList.remove(config)
    return [os.path.abspath(c) for c in configList]

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

    Returns a dictionary for each config containing the # Kappa test
    keys and their values
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
                            if key in ['CMSSW']:  # version list
                                result[name][key] = [v.strip().replace(".", "_") for v in string.split(',')]
                            elif key in ['scram arch', 'checkout script']:  # other lists
                                result[name][key] = [v.strip() for v in string.split(',')]
                            else:  # single strings
                                result[name][key] = string.strip()
                            done = True
                    if not done:
                        print "- Warning: {cfg:30}: Unknown 'Kappa test' line: {line}".format(cfg=name, line=line.strip())
                elif 'outputFile' in line and not result[name].get('output', False):
                    result[name]['output'] = line.split('=', 1)[1].split('root')[0].strip()[1:] + 'root'
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
        result[name]['cfgname'] = name
    return result

def preCheck(name, case):
    """Does a quick check if all information is available to run the tests"""
    if not case['CMSSW'] or not case['scram arch']:
        print "- Warning: {cfg:30}: Missing CMSSW and/or scram arch: config can not be tested at all.".format(cfg=name)
    elif len(case['CMSSW']) != len(case['scram arch']):
        print "- Warning: {cfg:30}: Different number of CMSSW versions ({nV}) and architectures ({nA}) given!".format(
                cfg=name, nV=len(case['CMSSW']), nA=len(case['scram arch']))
    for arch, ver in zip(case['scram arch'], case['CMSSW']):
        if not os.path.exists('/cvmfs/cms.cern.ch/%s/cms/cmssw/CMSSW_%s' % (arch, ver)):
            print "- Warning: {cfg:30}: CMSSW {v} not available for scram arch {arch}!".format(cfg=name, v=niceVersion(ver), arch=arch)
    if case['compare'] is False:
        print "- Warning: {cfg:30}: Given compare file does not exist: no result comparision possible.".format(cfg=name)
    if case['checkout script']:
        for i in range(len(case['checkout script'])):
            path = os.path.join(kappaPath, 'Skimming', case['checkout script'][i])
            if not os.path.exists(path):
                print "- Warning: {cfg:30}: Given checkout script '{script}' does not exist: checkout will fail ({path}).".format(cfg=name, script=case['checkout script'][i], path=path)
                case['checkout script'][i] = False
            else:
                case['checkout script'][i] = path
    if len(case['checkout script']) == 1 and len(case['CMSSW']) > 1:
        config['checkout script'] = case['checkout script'] * len(case['CMSSW'])
    if len(case['checkout script']) != len(case['CMSSW']):
        print "- Warning: {cfg:30}: Different number of CMSSW versions ({nV}) and checkout scripts ({nA}) given!".format(
                cfg=name, nV=len(case['CMSSW']), nA=len(case['checkout script']))


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
    print "   Required CMSSW versions:", ", ".join([niceVersion(v) for v in sorted(versions)])
    print "_"*length
    return success

def expandCases(configs):
    """For all configs, create a test case for each CMSSW version"""
    cases = []
    for config in configs.values():
        for ver, arch, script in zip(config['CMSSW'], config['scram arch'], config['checkout script']):
            case = TestCase(config)
            case.name = config['cfgname'] + '_' + ver
            case.config['name'] = case.name
            case.config['CMSSW'] = ver
            case.config['scram arch'] = arch
            case.config['checkout script'] = script
            cases.append(case)
            #print case.config
    return cases


class Test:
    """Base class of test tasks"""
    #shortDescription = "Test"
    optional = False
    preCheck = False
    script = ""
    def __init__(self):
        self.result = 0  # 0init, 10configure 0error1success, 20check 0error1success, 30run 0error1success 40 retrievenot 0nolog1log, 90 finalfailed 99optional100success 
        self.name = self.__class__.__name__
    def __str__(self):
        return self.name
    def boolResult(self):
        return bool(self.result > 3)
    def configure(self, config):
        self.config = config
        self.result = 11
        return True
    def check(self):
        self.result = 21
        return True
    def getResult(self):
        if os.path.exists(self.log):
            with open(self.log) as f:
                self.result = 90 + 10 * ('KAPPA TEST STEP SUCCESSFUL' in f.read())
        else:
            self.result = 40
        print self.result, self.optional, self.config['checkout script'], self.name, self.config['name']
        # hack to make checkout script optional if not given
        if self.optional and self.config['checkout script'] and type(self.config['checkout script']) == str and self.config['checkout script'][0] == '#':
            self.result = 99
            print "optional", self.result
        self.previous = 100
        return self.result


class TestCase(dict):
    """Class for test cases (config + CMSSW version)"""
    def __init__(self, config, tasks=None):
        self.script = ""
        self.name = ""
        self.log = ""
        self.config = copy.deepcopy(config)
        if tasks:
            self.tasks = copy.deepcopy(tasks)
        else:
            self.tasks = []

    def __str__(self):
        s = "Testcase %s " % self.name
        if type(self.tasks) == list:
            s += "(Tasks: " + ", ".join([str(t) for t in self.tasks]) + ")\n"
        return s + "  config: %s" % self.config
    
    def calculateResult(self, threshold=None):
        minimum = min([t.result for t in self.tasks])
        if threshold is None:
            return minimum
        return minimum >= threshold

    def configure(self):
        """fill and rate missing entries in case dictionary"""
        self.scriptname = self.name + "_testscript.sh"
        self.version = niceVersion(self.config['CMSSW'])
        if not self.config.get('checkout script', False):
            self.config['checkout script'] = '# no checkout script'
        if not self.config.get('output', False):
            self.config['output'] = '# output name unknown'
            self.config['no'] = '# '
        else:
            self.config['no'] = ''
        result = {}
        if self.tasks:
            for task in self.tasks:
                task.configure(self.config)
        self.result = self.calculateResult()
        return self.result >= 11

    def check(self):
        for task in self.tasks:
            task.check()
        self.result = self.calculateResult()
        return self.result >= 21

    def writeScript(self, debug=False):
        self.script = "#!/bin/bash\nshopt -s expand_aliases\ncd {case}\n"
        self.shortscript = "#!/bin/bash\nshopt -s expand_aliases\ncd {case}\n"
        for task in self.tasks:
            task.log = '%s/%s_%s.txt' % (os.path.abspath('./'), self.name, task.name.lower())
            self.script += "\n# {name}\n"\
                "echo \"KAPPA TEST TIME $(date +%s) $(date --rfc-3339=seconds)\" > {log}\n"\
                "{script} >> {log} 2>&1 && echo \"KAPPA TEST STEP SUCCESSFUL\" >> {log}\n"\
                "echo \"KAPPA TEST TIME $(date +%s) $(date --rfc-3339=seconds)\" >> {log}\n".format(
                log=task.log,
                name=task.name,
                script=task.script.replace('\n', ' >> %s 2>&1\n' % task.log))
            self.shortscript += "\n# {name}\n{script}\n".format(
                log=task.log, name=task.name, script=task.script)
        #print self.script
        os.mkdir(self.name)
        with open(self.scriptname, 'w') as f:
            f.write(self.script.format(kappa=kappaPath, case=self.name, **self.config))
        with open(self.scriptname.replace('script', 'shortscript'), 'w') as f:
            f.write(self.shortscript.format(kappa=kappaPath, case=self.name, **self.config))
        if debug:  # print script on output
            with open(self.scriptname) as f:
                for line in f:
                    print "   ", line[:-1] if '\n' in line else line
        self.result = 31
        return self.result >= 31

    def run(self, dryRun=False):
        startTime = time.time()
        if dryRun:
            #os.mkdir(self.name + '/CMSSW_' + self.config['CMSSW'])
            #os.mkdir(self.name + '/CMSSW_' + self.config['CMSSW'] + '/src')
            for task in self.tasks: # if not t.optional]:
                print "Writing to", task.log
                if not task.log:
                    print task.log, "LOG", task.name, self.name
                with open(task.log, 'w') as f:
                    f.write("Test %s\nKAPPA TEST STEP SUCCESSFUL\n" % task.name)
            time.sleep(0)
        else:
            self.scriptreturncode = subprocess.Popen(['bash', self.scriptname]).wait()
        self.runtime = time.time() - startTime
        self.nicetime = "%4d:%02d" % (int(self.runtime/60), int(self.runtime - int(self.runtime/60) * 60))
        return ((min([t.result for t in self.tasks]) > 40) + 2 * dryRun)

    def retrieve(self):
        self.log = self.name + '_log.txt'
        with open(self.log, 'w') as f:
            f.write("Log file for test case '%s'\n" % self.name)
            for task in self.tasks:
                if os.path.exists(task.log):
                    f.write("\nTest: %s\n" % task.name)
                    f.write(open(task.log).read())
                else:
                    print "File not found:", task.log
        return True

    def getResult(self):
        result = []
        for task in self.tasks:
            task.getResult()
            print "  %s: %d" % (task.name, task.result)
            result.append(task.result)
        self.result = min(result)
        if self.result == 99:
            self.result = 100 # optional tests do not count for final result
        print "  Result:", self.result
        return self.result


### Single tests

class Arch(Test):
    """Does the config file specify the scram arch needed for testing (required)"""
    script = "export SCRAM_ARCH={scram arch}\n"\
             "ls -d /cvmfs/cms.cern.ch/{scram arch}/cms/cmssw/CMSSW_{CMSSW}" # for the return code

class Env(Test):
    """Return code of cmsrel and cmsenv"""
    script = "echo \"NAF setup (will fail on EKP machines)\"\n"\
             "module use -a /afs/desy.de/group/cms/modulefiles/\n"\
             "module load cmssw\n"\
             "echo \"EKP setup\"\n"\
             "[[ $(hostname) == \"ekp\"* ]] && source /cvmfs/cms.cern.ch/cmsset_default.sh\n"\
             "cmsrel CMSSW_{CMSSW}\n"\
             "cd CMSSW_{CMSSW}/src\n"\
             "cmsenv\n"\
             "sed -i -e \"s@-fipa-pta@@g\" ../config/toolbox/{scram arch}/tools/selected/gcc-cxxcompiler.xml\n"\
             "test ! -z $CMSSW_BASE"

class Recipe(Test):
    """Return code of the checkout recipe (if provided, light green otherwise)"""
    optional = True
    script = "{checkout script}"

class Scram(Test):
    """The recipe (checkout script, without Kappa) compiles with scram"""
    # Kappa is removed if it was automatically checked out to test the
    # CMSSW packages alone
    # complicated rm path to prevent accidental removal
    script = "rm -rf ../../../{case}/CMSSW_{CMSSW}/src/Kappa\n"\
             "scram b -j8"

class Copy(Test):
    """The Kappa version to be tested is copied to src/"""
    # get your private Kappa to be tested
    script = "rsync -rP --exclude=.git --exclude=lib {kappa} ./"

class Compile(Test):
    """Return code of scram b including Kappa"""
    script = "scram b -j4"

class Config(Test):
    """CMSSW config file is valid (executed with python)"""
    script = "python {config}"

class CmsRun(Test):
    """Return code of CMSSW cmsRun command"""
    script = "cmsRun {config}"

class Output(Test):
    """Does output file exist"""
    script = "ls -l {output}\n"\
             "test -f {output}"

class Valid(Test):
    """Is output file a valid ROOT file"""
    script = "root -q -l {output} 2>&1 | grep -v \"no dictionary for class\"\n"\
             "! root -q -l {output} 2>&1 | grep Error"

class Compare(Test):
    """Whether the output file is identical to the given compare file"""
    script = "compareFiles.py {output} {compare}\n"\
             "echo Not tested"


def writeHTML(branches, allOK):
    # header
    html = """\
<!DOCTYPE html>
<!-- autogenerated by DataFormats/test/test.py -->
<!-- Copyright (c) Joram Berger -->

<html>
<head>
<meta charset="utf-8"/>
<link rel="shortcut icon" type=image/x-icon" href="http://www-ekp.physik.uni-karlsruhe.de/~berger/kappa/img/Kappa.ico"/>
<meta name="description" content="Result overview of the status of the Kappa framework"/>
<title>Kappa test results</title>
<style>
body {
  font-size: 10pt;
  margin: 0px;
    font-family: "Ubuntu";
}
h2 { padding: 20px 0px 0px 0px; }
h3 {
    color: #3D578C;
}
h4 { color: #777 }
div.head {
  margin: 0px;
  padding: 1px 10px;
  width: 100%;
  background-color: #3D578C;
  color: white;
  font-size: 150%;
}
span.commit {
  background-color: #5BC0DE;
  display: inline;
    padding: 0.2em 0.6em 0.3em;
    font-size: 90%;
    font-weight: 700;
    color: #FFF;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25em;
}
div {
    margin: 10px;
}
div.result {
  width: 200px;
  text-align: center;
  display: inline;
    padding: 0.2em 1.0em 0.3em;
    font-size: 150%;
    font-weight: 700;
    color: #FFF;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25em;
}
div.allgood {
  background-color: #449D44;
}
div.allbad {
  background-color: #C9302C;
}

a:focus, a:hover {
    color: #23527C;
    text-decoration: underline;
}
a:active, a:hover {
    outline: 0px none;
}
a {
    color: #337AB7;
    text-decoration: none;
}
table a { color: inherit; text-align: center; display:block;
    text-decoration:none; }
table a:hover { color: LightGray; text-decoration: none; }
span a { color: white }
h3 a { color: #3D578C }


table, th, td {
    border: 0px none;
    padding: 4px;
}

#th { width: 60px; }
tr {
    border: 6px solid white;
	margin: 0px 0px;
	padding: 0px 0px;
}
td {
	border: 0;
	margin: 0px 0px;
}
table.legend, tr.legend, th.legend, td.legend, .legend > tr, .legend > td, .legend > th {
    border: 0px;
    border-collapse: collapse;
}
table#t01 {
    border: 0px;
}
table#t01 tr:nth-child(even) {
    background-color: #eee;
}
table#t01 tr:nth-child(odd) {
    background-color: #fff;
}
table#t01 th { text-align:left;   border: 0px;}
table#t01 td { border: 0px;}

td.fail { background: #C9302C; color: #C9302C; }
td.success { background: #449D44; color: #449D44; }
td.acceptable { background: YellowGreen; color: YellowGreen; }
td.other {background: #CCC; color: #CCC; }
td.untestable { background: #EC971F; color: #EC971F; }
</style>
<script>
function timeAgo(time) {
    var diff = (new Date() - new Date(time*1000)) / 1000;
    diff = Math.floor(diff);
    var sec = Math.floor(diff % 60);
    var min = Math.floor(diff / 60 % 60);
    var std = Math.floor(diff / 3600 % 24);
    var day = Math.floor(diff / 24 / 3600);

    var outstr = " ("
           + (day > 0 ? day + "d " : "")
           + (std > 0 ? std + "h " : "")
           + min + "min ago)";
    if (diff < 60) outstr = " (now)";
    document.getElementById("timeago").innerHTML = outstr;

    if (day > 7)
        document.getElementById("timeago").style.color = "red";
} 
</script>
</head>
"""
    # general info
    runtime = sum([case.runtime for branch in branches for case in branch])
    m, s = divmod(runtime, 60)
    h, m = divmod(m, 60)
    values = {
        'runtime': "%d:%02d:%02d" % (h, m, s),
        'status': ["not ok", "ok"][allOK],
        'cls': ['allbad', 'allgood'][allOK],
        'time': time.time(),
        'date': time.strftime('%Y-%m-%d – %H:%M:%S'),
    }
    repo = "https://github.com/KappaAnalysis/Kappa"
    
    def getStatus(result, previous=100):
        if result == 100:
            return "success"
        if result == 99:
            return "acceptable"
        return "fail"

    html += """
<body onload="timeAgo({time})">
 <div class="head"><h1>Kappa Test Results</h1></div>
 <div>
 <h2>General Information</h2> <p>Date: {date}<span id="timeago"></span>, run time: {runtime}</p>
 <p>This page is a result of the <a href="https://github.com/KappaAnalysis/Kappa/blob/development/DataFormats/test/test.py">test.py</a> script,
 which is run regularly to test <a href="https://github.com/KappaAnalysis/Kappa">Kappa</a>.</p>

 <div class="result {cls}">Kappa is {status}</div>
 
 """.format(**values)
    # branches
    html += "<h2>Test Results in Detail</h2>"
    for branch in branches:
        #  <!-- <tr>    <th colspan="2">Test case</th>    <th colspan="4">Configuration</th>    <th colspan="6">System</th>    <th colspan="2">Run</th>    <th colspan="3">Output</th>    <th></th>    <th></th>  </tr> -->
        if len(branches) == 1 and branch[0].commit is None:  # workdir
            html += " <h3>Working directory: {workdir}</h3>".format(
                workdir=branch[0].branch)
        else:  # real branch
            html += """ <h3>Branch: <a href="{branchref}">{branchname}</a></h3>
  <p><span class="commit"><a href="{commitref}">{commit}</a></span>""".format(
        branchname=branch[0].branch,
        commit=branch[0].commit,
        branchref=repo + "/commits/" + branch[0].branch,
        commitref=repo + "/commits/" + branch[0].commit,
        )
        html += "<table>\n  <tr>\n     <th style=\"text-align:left\">Config file</th> <th>Version</th>"
        for task in branch[0].tasks:
            html += "<th>{taskname}</th>".format(taskname=task.name)
        html += "<th></th><th>Result</th>\n</tr>\n"
        for case in branch:
            html += """<tr>
    <td class="none" title="{path}">{config}</td>
    <td class="none" title="{scram}">{version}</td>""".format(
        config=case.config['cfgname'],
        version=niceVersion(case.config['CMSSW']),
        path=case.config['config'],
        scram=case.config['scram arch'],
    )
            for task in case.tasks:
                html += '<td class="{status}"><a href="{log}">{result}</a></td>'.format(log=os.path.basename(task.log), result=task.result, status=getStatus(task.result, task.previous))
            html += '<td></td><td class="{status}"><a href="{log}">{result}</a></td></tr>\n'.format(log=case.log, result=case.result, status=getStatus(case.result))
    html += "</table>\n"

    # legend
    html += '<hr/>\n<h4>Legend</h4>\n<table class="legend"  id="t01">\n'
    for task in branches[0][0].tasks:
        html += "<tr><th>{name}</th><td>{doc}</td></tr>\n".format(name=task.name, doc=task.__doc__)
    html += "</table>\n"
    # footer
    html += "</div>\n</body>\n</html>\n"
    return html


def sendMail(testPaths):
    import smtplib
    from email.mime.text import MIMEText as Message

    msg = Message("""Dear Kappa developers,

the test script found problems in the current state of the Kappa repository.
Please have a look at: http://www-ekp.physik.uni-karlsruhe.de/~berger/kappa/test/result.html

The test directory is %s

Your friendly test script
""" % testPaths)
    msg['Subject'] = 'Kappa test problems'
    msg['From'] = 'test@kappa' 
    msg['To'] = 'joram.berger@cern.ch'  # artus list?

    s = smtplib.SMTP('smarthost.kit.edu')
    s.sendmail(msg['From'], msg['To'] , msg.as_string())
    s.quit()
    print "Message sent to %s." % msg['To']

if __name__ == "__main__":
    main(sys.argv)

