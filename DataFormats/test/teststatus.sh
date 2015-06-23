#!/bin/bash
# Check the outputs of the Kappa test suite live
# Usage: watch teststatus.sh

if ! $(ls *txt &> /dev/null)
then
  echo "Kappa test not running here"
  exit
fi

checkresult () {
  echo "--------------------------------------------------------------"

  for i in $(ls -rt *txt)
  do
    [[ $i != *"log.txt" ]] && (
    grep "SUCCESS" $i >> /dev/null && echo "+ $i" || echo "- $i"
    )
  done
  echo "--------------------------------------------------------------"
}

if [[ -f result.html ]]
then
  echo "Kappa test done                  $(date)"
  checkresult
else
  echo "Kappa test running               $(date)"
  checkresult
  echo "Latest log output from $(ls -rt1 | tail -1):"
  tail -8 $(ls -rt1 | tail -1)
fi
