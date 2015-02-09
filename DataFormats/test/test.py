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
Checks per case: setup, checkout, scram, python, cmsRun, output, root output, compare output

usecases:
check single config file
check current working tree
check current branch heads
options:
stop after precheck? batch mode
Naming:
- test: a small test snippet that each test case must pass
- config: CMSSW config equipped with 'Kappa test' statements
- case: a test case (1 config, 1 CMSSW version, a series of tests)
Hierarchy:
main: choose application mode
  run: run on one Kappa directory
    testcases from configs



"""

import os
import sys
import glob
import subprocess
import copy
import time

groupConfigsToBeChecked = [
    "Skimming/zjet/x.py", # does not exist, just testing error handling here
    "Skimming/higgsTauTau/kSkimming_cfg.py",
    "Skimming/higgsTauTau/kSkimming_run2_cfg.py",
    "Skimming/zjet/2014-04-03_skim_53x_emu.py",
]
compareFilesPath = '/storage/6/berger/kappatest/'

kappaPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


def main(args):
    # minimal argument parser
    batchMode = ("-b" in args)
    if "-b" in args:
        args.remove("-b")
    if "-h" in args:
        print "Usage: /path/to/script/test.py [config|branch names] [-b (batch mode=no questions)]"
        exit()
    #for i, a in zip(range(len(args)), args):
    #    print "DEBUG: %4d: %s" % (i, a)
    # run the tests
    results = []
    if len(args) == 1:
        print "Test all default configs in working directory"
        results.append(run(kappaPath, batchMode=batchMode))
    elif args[1][-3:] == '.py':
        print "Test these configs:", args[1:]
        results.append(run(kappaPath, configs=args[1:], batchMode=batchMode))
    else:
        print "Test all default configs in these branches:", ", ".join(args[1:])
        for b in args[1:]:
            print "Test branch '%s':" % b
            #git clone -b {branch} Kappa
            results.append(run(kappaPath, branch=b, batchMode=batchMode))
    # print results (stdout + html)
    for r in results:
        print r
    return
    #printresult(duration=duration)
    #NEW
    # read configs
    # create cases (branches * configs * versions)



    writeHTML(cases)
    finalResult = {}
    finalResult['result'] = sum([case.result < 4 for case in cases])
    if not finalResult['result']:
        sendMail()

def run(kappaPath, configs=None, branch=None, batchMode=False):
    print "Collect configs from %s ..." % kappaPath
    configNames = collectConfigs(kappaPath, configs)

    print "\nParse %d configs ..." % len(configNames)
    configs = parseConfigs(configNames)

    print "\nTesting configs ..."
    for name in sorted(configs):
        preCheck(name, configs[name])
    # make test cases from the configs (configs x CMSSW versions)
    cases = expandCases(configs)
    cases = sorted(cases, key=lambda k: k.name)

    if not printPreCheck(configs):
        # the program should always run up to here, fatal errors only afterwards
        if (not batchMode and
            (raw_input("Not all test cases can be fully tested. "
            "Do you want to run all possible tests (%d)? "
            "[yes]\n" % len(cases))[:1] or 'y') != 'y'):
            exit()

    print "\nConfigure %d cases ..." % len(cases)
    tests = [
        Arch(config), Env(config), Recipe(config), Scram(config),
        Copy(config)
    ]
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), name)

        case.configure()

    print "\nCheck %d cases ..." % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), name)
        case.preCheck()

    print "\nWrite test script for %d cases ..." % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), name)
        case.writeScript()

    print "\nRun %d cases ..." % len(cases)
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), name)
        case.run()

    print "\nRetrieve results for %d cases ..." % len(cases)
    result = []
    for case, i in zip(sorted(cases), range(len(cases))):
        print "- Case %d/%d: %s" % (i+1, len(cases), name)
        result.append(case.getResult())
        #result[name] = testCase(cases[name])
    print "Done."
    return result



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
        result[name]['cfgname'] = name
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
    """For all configs, create a test case for each CMSSW version"""
    cases = []
    for config in configs.values():
        for i in range(len(config['CMSSW'])):
            case = TestCase(config)
            case.name = config['cfgname'] + '_' + config['CMSSW'][i]
            case.config['CMSSW'] = config['CMSSW'][i]
            case.config['scram arch'] = config['scram arch'][i]
            cases.append(case)
            print case.config
    print "CC", cases
    return cases


class Test:
    """Base class of test tasks"""
    #shortDescription = "Test"
    preCheck = False
    script = ""
    def __init__(self):
        self.result = 0  # not run, failed, could not test due to requirements, can pass (not yet tested), optional (not selected), successful
    def boolResult(self):
        return bool(self.result > 3)
    def configure(self):
        return True
    def run(self):
        return 5
    def preCheck(self):
        return True
    def check(self):
        name = self.__class__.__name__
        print name
        with open('%s.log' % name) as f:
            result = 'KAPPA TEST SUCCESSFUL' in f.read()


class TestCase(dict):
    """Class for test cases (config + CMSSW version)"""
    def __init__(self, config, tasks=None):
        self.script = ""
        self.name = ""
        self.config = copy.deepcopy(config)
        if tasks:
            self.tasks = copy.deepcopy(tasks)
        else:
            self.tasks = []

    def __str__(self):
        s = "Testcase %s " % self.name
        if type(self.tasks) == list:
            s += "(Tasks: " + ", ".join(self.tasks) + ")\n"
        return s + "  config: %s" % self.config

    def configure(self):
        result = True
        if self.tasks:
            for task in self.tasks:
                task.configure(self.config)
    def preCheck(self):
        for task in self.tasks:
            task.check()
    def writeScript(self):
        print "DEBUG: CASE", case
        self.script = "#!/bin/bash\ncd {case}\n"
        for task in self.tasks:
            self.script += "# {name}\n( {script} ) &> {name}.log".format(
                name=task.__name__, script=task.script)
        print self.script
        with open(self.scriptame, 'w') as f:
            f.write(script.format(kappa=kappaPath, **case))
        with open(filename) as f:
            for line in f:
                print "   ", line[:-1]
    def run(self):
        print "running ...",
        startTime = time.time()
        #subprocess.Popen(self.script)
        time.sleep(1)
        self.runtime = time.time() - startTime
        self.nicetime = "Time: %4d:%02d" % (int(duration/60), int(duration - int(duration/60) * 60))
        print "done."
    def getResult(self):
        for task in self.tasks:
            result = min(result, task.run() + 10 * task.relevant)
        self.result = result
        return result
        result = {
            'env': False, 'scram': False, 'recipe': False, 'compile': False,
            'python': False
        }
        for key in result:
            with open('%s.log' % key) as log:
                result[k] = ('successful' in log.read())



def configureCase(case):
    """fill and rate missing entries in case dictionary"""
    print "DEBUG: CASE", case
    case['testscript'] = case['case'] + "/testscript.sh"
    #return {}
    script = ""
    case['version'] = niceVersion(case['CMSSW'])
    if not case.get('checkout script', False):
        case['checkout script'] = '# no checkout script'
    if not case.get('output', False):
        case['output'] = '# output name unknown'
        case['no'] = '# '
    else:
        case['no'] = ''
    return case

def scriptCase(case):
    """create directory and test script from case dictionary"""
    for test in case['tests']:
        pass #script = script.replace("> {}".format(test),
    #        ' &> ../../{}.log && echo "--- LOG: {} ---\nKAPPA TEST STEP SUCCESSFUL" &>> ../../{}.log'.format(log).replace('&>','asdf'))

    os.mkdir(case['case'])
    # write script





class Arch(Test):
    """Does the config file specify the scram arch needed for testing (required)"""
    script = "export SCRAM_ARCH={scram arch}"\
             "ls /cvmfs/cms.cern.ch/{scram arch}/cms/cmssw/CMSSW_{CMSSW}"

class Env(Test):
    """Return code of cmsrel and cmsenv"""
    script = "source /cvmfs/cms.cern.ch/cmsset_default.sh &&"\
             "cmsrel CMSSW_{CMSSW} &&"\
             "cd CMSSW_{CMSSW}/src &&"\
             "cmsenv"

class Recipe(Test):
    """Return code of the checkout recipe (if provided)"""
    # complicated rm path to prevent accidental removal
    script = "{checkout script}\nrm -rf ../../../{case}/CMSSW_{CMSSW}/src/Kappa"

class Scram(Test):
    """The recipe (checkout script) compiles with scram)"""
    script = "scram b -j8"

class Copy(Test):
    """The Kappa version to be tested is copied to src/"""
    # get your private Kappa to be tested
    script = "rsync -r {kappa} ./"

class Compile(Test):
    """Return code of scram b including Kappa"""
    script = "scram b -j 4"

class Python(Test):
    """CMSSW config file is valid (executed with python)"""
    script = "python {config}"


class CmsRun(Test):
    """Return code of CMSSW"""
    script = "cmsRun {config}"

class Compare(Test):
    """Whether the output file is identical to the given compare file"""
    script = "compareFiles.py {output} {compare}"

def writeHTML(branches):
    # header
    html = """\
<!DOCTYPE html>
<!-- autogenerated by DataFormats/test/test.py -->
<!-- Copyright (c) Joram Berger -->

<html>
<head>
<meta http-equiv="Content-Type" content="text/xhtml;charset=UTF-8"/>
<style>
body {
  margin: 0px;
    font-family: "Ubuntu"
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
  background-color: #449D44;
  padding: 8px
  display: inline;
    padding: 0.2em 0.6em 0.3em;
    font-size: 150%;
    font-weight: 700;
    color: #FFF;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25em;
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
span a { color: white }
h3 a { color: #3D578C }


table, th, td {
    border: 0px none;
    #border-collapse: collapse;
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
	#padding: 3px 0px;
}
table.legend, tr.legend, th.legend, td.legend, .legend > tr, .legend > td, .legend > th {
    border: 0px;
    border-collapse: collapse;
}
table#t01 {
    font-size: small;
    border: 0px;
}
table#t01 tr:nth-child(even) {
    background-color: #eee;
}
table#t01 tr:nth-child(odd) {
    background-color: #fff;
}
table#t01 th {  text-align:left;   border: 0px;}
table#t01 td {    border: 0px;}
#table#t01 th {
#    color: white;
#    background-color: black;
#}
td.fail { background: #C9302C; }
td.success { background: #449D44; }
td.acceptable { background: YellowGreen; }
td.other {background: #CCC; }
td.untestable { background: #EC971F; }
</style>
</head>

<body>
 <div class="head"><h1>Kappa Test Results</h1></div>
 <div>
 <h2>General Information</h2>
 Date: 2015-01-06 - 12:00:12
 <p>Test run time: 20 min</p>
 <p>This page is a result of the <a href="https://github.com/KappaAnalysis/Kappa/blob/master/DataFormats/test/test.py">test.py</a> script,
 which is run daily to test <a href="https://github.com/KappaAnalysis/Kappa">Kappa</a>.</p>

 <div class="result">Kappa is ok</div>

 <h2>Tested Branches in Detail</h2>
 """
    # general info
    # branches
    html += "<h2>Tested Branches in Detail</h2>"
    for branch in branches:
        html += """ <h3>Branch: dictchanges</h3>
  <p><span class="commit">Kappa_2_0_1-1-gbf126cb</span>
 <table>
  <tr>
    <th colspan="2">Test case</th>
    <th colspan="4">Configuration</th>
    <th colspan="6">System</th>
    <th colspan="2">Run</th>
    <th colspan="3">Output</th>
    <th></th>
    <th></th>
  </tr>
  <tr>
    <th style="text-align:left">Config file</th> <th>Version</th>"""
        for task in branch[0]:
            html += "<th>{taskname}</th>"
        html += "\n</tr>\n"
        for case in b:
            html += """<tr>
    <td class="none">{config}</td>
    <td class="none">{CMSSW}</td>"""
            for task in case:
                html += '<td class="{result}"></td>'
            html += "</tr>\n"

    # legend
    html = '<hr/>\n<h4>Legend</h4>\n<table class="legend"  id="t01">\n'
    for task in cases[0].tasks:
        html += "<tr><th>{name}</th><td>{doc}</td></tr>\n".format(task)
    html += "</table>\n"
    # footer
    html += "</div>\n</body>\n</html>\n"
    return html


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

def sendMail():
    import smtplib
    from email.mime.text import MIMEText as Message

    msg = Message("""Kappa test results

the test script found issues in
problems: http://www-ekp.physik.uni-karlsruhe.de/~berger/kappa/
""")
    msg['Subject'] = 'Kappa test problems'
    msg['From'] = 'joram.berger@cern.ch'
    msg['To'] = 'joram.berger@cern.ch'

    s = smtplib.SMTP('smarthost.kit.edu')
    #s.sendmail(msg['From'], msg['To'] , msg.as_string())
    s.quit()
    print "Message sent to", msg['To']

if __name__ == "__main__":
    main(sys.argv)

