#!/usr/bin/env bash

# Automatically generated on {{ timestamp.strftime('%a %b %d %H:%M:%S %Z %Y') }}

# The SCRAM architecture and CMSSW version used to create the jobs.
readonly JOB_SCRAM_ARCH="{{ environ['SCRAM_ARCH'] }}"
readonly JOB_CMSSW_VERSION="{{ environ['CMSSW_VERSION'] }}"

# Capture the executable name and job file from the command line.
readonly CONDOR_EXEC="$(basename $0)"
readonly JOB="$1"

deploy_cmssw() {
  # Setup the CMS software environment.
  export SCRAM_ARCH="$JOB_SCRAM_ARCH"
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  # Checkout the CMSSW release and set the runtime environment. These
  # commands are often invoked by their aliases "cmsrel" and "cmsenv".
  scramv1 project CMSSW "$JOB_CMSSW_VERSION"
  cd "$JOB_CMSSW_VERSION/src"
  eval "$(scramv1 runtime -sh)"
  # Create a Python virtual environment and install any dependencies.
  virtualenv venv
  source venv/bin/activate
  pip install vhbbtools
  # Change back to the scratch directory of the worker node.
  cd "$_CONDOR_SCRATCH_DIR"
}

main() {
  echo "$(date) - $CONDOR_EXEC - INFO - Deploying $JOB_CMSSW_VERSION and installing dependencies"
  deploy_cmssw
  echo "$(date) - $CONDOR_EXEC - INFO - Running the job"
  python run.py "$JOB"
}
main

