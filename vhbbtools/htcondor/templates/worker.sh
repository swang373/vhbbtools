#!/usr/bin/env bash

# Automatically generated on {{ timestamp }}

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
  # Change back to the worker node's scratch directory.
  cd "$_CONDOR_SCRATCH_DIR"
}

deploy_python() {
  # Create a Python virtual environment using the Python interpreter
  # distributed with the job's CMSSW release.
  virtualenv -p "$(which python)" venv
  # Activate the virtual environment.
  source venv/bin/activate
  # Install any dependencies.
  pip install vhbbtools
}

main() {
  echo "$(date) - $CONDOR_EXEC - INFO - Deploying $JOB_CMSSW_VERSION"
  deploy_cmssw
  echo "$(date) - $CONDOR_EXEC - INFO - Deploying Python virtual environment and installing dependencies"
  deploy_python
  echo "$(date) - $CONDOR_EXEC - INFO - Running the job"
  python run.py "$JOB"
}
main

