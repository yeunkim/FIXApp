#!/usr/bin/python

from __future__ import print_function
import argparse
# from bids.grabbids import BIDSLayout
from functools import partial
from collections import OrderedDict
import os
from subprocess import Popen, PIPE, check_output
import subprocess
import time
import logging
import datetime


def run(command, cwd=None, stage='', filename=''):
    merged_env = os.environ
    # merged_env.update(env)
    merged_env.pop("DEBUG", None)
    logfn = stage + filename + '.log'
    logpath = os.path.join(str(cwd),'logs', logfn)
    logfile = open(logpath, 'w')
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT,
                    shell=True, env=merged_env, cwd=cwd)

    for line in process.stdout:
        logfile.write(line)

    while True:
        line = process.stdout.readline()
        line = str(line)[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

def feature_extraction(**args):
    print(args)
    args.update(os.environ)
    cmd = '/fix1.06a/fix ' + \
        '-f ' + \
        '{melodicICA}'
    cmd = cmd.format(**args)
    t = time.time()
    logging.info(" {0} : Extracting features for the subjects for {1} ... ".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"), args["Training"]))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='featureExtraction', filename="_{0}".format(args["Training"]))
    elapsed = time.time() - t
    elapsed = elapsed /60
    logging.info("Finished extracting features. Time duration: {0} minutes".format(str(elapsed)))


def train_data_fix(**args):
    print(args)
    args.update(os.environ)
    cmd = '/fix1.06a/fix ' + \
        '-t {Training} ' + \
        '-l ' + \
        '{melodicICA}'
    cmd = cmd.format(**args)
    t = time.time()
    logging.info(" {0} : Training classifiers (creating the trained-weights "
                 "file {1}.RData ...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"), args["Training"]))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='training', filename="_{0}".format(args["Training"]))
    elapsed = time.time() - t
    elapsed = elapsed /60
    logging.info("Finished training classifiers. Time duration: {0} minutes".format(str(elapsed)))

def classify_ica_components(**args):
    print(args)
    args.update(os.environ)
    cmd = '/fix1.06a/fix ' + \
          '-c {melodicOutput} ' + \
          '{TrainingRData} ' + \
          '{thresh}'
    cmd = cmd.format(**args)
    t = time.time()
    logging.info(" {0} : Classifying ICA components ...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"),
                                             args["TrainingRData"].split('.')[0]))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='classifying', filename="_{0}".format(os.path.basename(args["TrainingRData"]).split('.')[0]))
    elapsed = time.time() - t
    elapsed = elapsed / 60
    logging.info("Finished classifying ICA components. Time duration: {0} minutes".format(str(elapsed)))

def clean(**args):
    print(args)
    args.update(os.environ)
    cmd = '/fix1.06a/fix ' + \
          '-a ' + \
          '{thrTXT} ' + \
          '-m -h {hp} ' + \
          '{A}'
    cmd = cmd.format(**args)
    print(cmd)
    t = time.time()
    logging.info(
        " {0} : Cleaning artefacts ... ".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='cleaning', filename='_{0}'.format(args["subj"]))
    elapsed = time.time() - t
    elapsed = elapsed / 60
    logging.info("Finished cleaning artefacts. Time duration: {0} minutes".format(str(elapsed)))

def accuracy_testing(**args):
    print(args)
    args.update(os.environ)
    cmd = '/fix1.06a/fix ' + \
          '-C {TrainingRData} ' + \
          '{output} ' + \
          '{melodicICA}'
    cmd = cmd.format(**args)
    t = time.time()
    logging.info(
        " {0} : Testing the accuracy of an existing training dataset...".format(datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y"),
                                                       args["TrainingRData"].split('.')[0]))
    logging.info(cmd)
    run(cmd, cwd=args["path"], stage='testing', filename="_{0}".format(os.path.basename(args["TrainingRData"]).split('.')[0]))
    elapsed = time.time() - t
    elapsed = elapsed / 60
    logging.info("Finished testing accuracy of existing training dataset. Time duration: {0} minutes".format(str(elapsed)))

parser = argparse.ArgumentParser(description='Generates training dataset. Extension to the HCPPipeline BIDS App (yeunkim)')
parser.add_argument('Training', help='For training and classifying: the name of training dataset to be generated (i.e. HCP_hp2000).\n'
                                     'Output from training and classifying will be saved in a folder within the parent directory\n.'
                                     'For accuracy testing: the name of existing training dataset file (*.RData)')
parser.add_argument('pdir', help='Path to parent directory of the subject folders')
parser.add_argument('-i', dest='input', help='List of subjects (text file with each subject ID at each new line', required=True)
parser.add_argument('-fn', dest='fn', help='Melodic ICA folder name of subjects. If both directions are going to be used,'
                                           'list both folders names delimited by commas (no space). Make sure both melodic'
                                           'folders are located in each subject folder.'
                                           'i.e. -fn task-rest_acq-AP_run-01,task-rest_acq-PA_run-01', required=True)
parser.add_argument('-o', dest='output', help='Output path to contain the results from testing stage', required=False)
parser.add_argument('--stages', help='Which stages to run. Space separated list.',nargs='+',
                    choices= ['extract', 'train', 'classify', 'clean', 'test'], default=['classify', 'clean'])
parser.add_argument('--thresh', help="Threshold value for classifying. Range 0-100 (typically 5-20). Default = 10.",default=10,
                    type=int)
parser.add_argument('--aggressive', help="Apply aggressive (full variance) cleaning for FIX", action='store_true',
                    required=False)
parser.add_argument('--hp', help="High pass filter: temporal highpass full-width (2*sigma) in seconds. Default=2000"
                                 "For detrending-like behavior, set highpass to 2000.", default=2000, type=int, required=False)
args = parser.parse_args()

starttime = time.time()

## check arguments supplied
if 'test' in args.stages and args.output is None:
    parser.error('testing stage requires -i, -fn, and -o arguments')
if 'test' in args.stages and not os.path.exists(args.output):
    os.makedirs(args.output)
if 'test' in args.stages and not os.path.exists(args.Training):
    raise IOError("Training dataset file {0} does not exist.".format(args.Training))

if not os.path.exists(os.path.join(args.pdir, 'logs')):
    os.makedirs(os.path.join(args.pdir, 'logs'))
logging.basicConfig(filename=os.path.join(args.pdir, 'logs', '{0}_TrainForFIX.log'.format(args.Training)),
                    level=logging.DEBUG, format='%(levelname)s:%(message)s', filemode='w')

### check if parent directory exists
if not os.path.exists(args.pdir):
    raise IOError('Path to {0} does not exist'.format(args.pdir))

## do work
subjICAs= []
subjs=[]
ICAfolders=args.fn.split(',')
with open(args.input, 'r') as f:
    for line in f:
        subjID = line.rstrip('\n')
        subjs.append(subjID)
        #pos=args.fn.rfind("hp")
        #fn = args.fn[0:(pos-1)]
        for ICAfolder in ICAfolders:
            pos=ICAfolder.rfind("hp")
            fn = ICAfolder[0:(pos-1)]
            icaPath = os.path.join(args.pdir, subjID, '{0}_output'.format(subjID), 'sub-%s'%subjID, 'MNINonLinear',
                                   'Results', fn, ICAfolder)
            subjICAs.append(icaPath)
subjICAstr = ' '.join(subjICAs)

if 'extract' in args.stages:
    trainingFolder = os.path.join(args.pdir, 'train_' + args.Training)
    if not os.path.exists(trainingFolder):
        os.mkdir(trainingFolder)
    if not os.path.exists(os.path.join(trainingFolder, 'logs')):
        os.makedirs(os.path.join(trainingFolder, 'logs'))

    extract_stages_dict = OrderedDict([('extract', partial(feature_extraction,
                                                       path=trainingFolder,
                                                       Training=args.Training,
                                                       melodicICA=subjICAstr)
                                    )])
    for stage, stage_func in extract_stages_dict.iteritems():
        stage_func()

if 'train' in args.stages:
    trainingFolder = os.path.join(args.pdir, 'train_' + args.Training)
    if not os.path.exists(trainingFolder):
        os.mkdir(trainingFolder)
    if not os.path.exists(os.path.join(trainingFolder, 'logs')):
        os.makedirs(os.path.join(trainingFolder, 'logs'))

    train_stages_dict = OrderedDict([('train', partial(train_data_fix,
                                                       path=trainingFolder,
                                                       Training=args.Training,
                                                       melodicICA=subjICAstr)
                                    )])
    for stage, stage_func in train_stages_dict.iteritems():
        stage_func()


if "classify" in args.stages:
    pathToTrain = os.path.join(args.pdir, 'train_'+args.Training, "{0}.RData".format(args.Training))
    for subjICA in subjICAs:
        classify_stages_dict = OrderedDict([('classify', partial(classify_ica_components,
                                                                 path=args.pdir,
                                                                 melodicOutput=subjICA,
                                                                 TrainingRData=pathToTrain,
                                                                 thresh=args.thresh
                                                             ))])
        for stage, stage_func in classify_stages_dict.iteritems():
            stage_func()

if "clean" in args.stages:
    if args.aggressive:
        A="-A"
    else:
        A=""
    for i, subj in enumerate(subjICAs):
        thrTXT = os.path.join(subj, 'fix4melview_{0}_thr{1}.txt'.format(args.Training, str(args.thresh)))
        clean_stages_dict = OrderedDict([('clean', partial(clean,
                                                           path=args.pdir,
                                                           subj=subjs[i],
                                                           thrTXT=thrTXT,
                                                           hp=args.hp,
                                                           A=A
                                                           ))])
        for stage, stage_func in clean_stages_dict.iteritems():
            stage_func()


if "test" in args.stages:
    # pathToTrain = os.path.join(args.pdir, 'train_' + args.Training, "{0}.RData".format(args.Training))
    test_stages_dict = OrderedDict([('test', partial(accuracy_testing,
                                                     path=args.pdir,
                                                     melodicICA=subjICAstr,
                                                     output=args.output,
                                                     TrainingRData=args.Training
                                                     ))])
    for stage, stage_func in test_stages_dict.iteritems():
        stage_func()
