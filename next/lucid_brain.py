"""
Usage:
    launch_lucid_brain.py launch
    launch_lucid_brain.py scp
"""
from __future__ import print_function
import numpy
import numpy as np
import numpy.random
import random
import json
import time
from datetime import datetime
import requests
from scipy.linalg import norm
import time
from multiprocessing import Pool
from docopt import docopt
import sys
import os

def make_targetset():
    return [{'target_id': str(i),
             'primary_type': 'text',
             'primary_description': str(i + 1),
             'alt_type': 'text',
             'alt_description': str(i + 1)} for i in range(12)]


HOSTNAME = os.environ.get('NEXT_BACKEND_GLOBAL_HOST', 'localhost')
host_file = os.environ.get('KEY_FILE')

def run_all(assert_200, alg):
    # num_objects = 5
    desired_dimension = 2
    # x = numpy.linspace(0,1,num_objects)
    # X_true = numpy.vstack([x,x]).transpose()
    # total_pulls_per_client = 20
    num_experiments = 1
    # clients run in simultaneous fashion using multiprocessing library
    num_clients = 1

    pool = Pool(processes=num_clients)
    # input test parameters
    delta = 0.01
    # supported_alg_ids = ['RandomSampling','RandomSampling','UncertaintySampling','CrowdKernel', 'STE']
    supported_alg_ids = [alg]

    alg_list = []
    for idx,alg_id in enumerate(supported_alg_ids):
        alg_item = {}
        alg_item['alg_id'] = alg_id
        if alg_id == 'ValidationSampling':
            alg_item['alg_label'] = 'Test'
            alg_item['params'] = {'query_list': [
                [q1, q2, q3] for q1 in [0, 1, 2]
                             for q2 in [0, 1, 2]
                             for q3 in [0, 1, 2]
                                             ]}
        else:
            alg_item['alg_label'] = alg_id
        alg_item['test_alg_label'] = 'Test'
        alg_list.append(alg_item)
    params = []
    for algorithm in alg_list:
        params.append({'alg_label': algorithm['alg_label'],
                       'proportion': 1})
    algorithm_management_settings = {}
    algorithm_management_settings['mode'] = 'fixed_proportions'
    algorithm_management_settings['params'] = params

    #################################################
    # Test POST Experiment
    #################################################
    print('\n'*2 + 'Testing POST initExp...')
    initExp_args_dict = {}
    initExp_args_dict['app_id'] = 'PoolBasedTripletMDS'
    initExp_args_dict['args'] = {}
    initExp_args_dict['args']['d'] = desired_dimension
    initExp_args_dict['args']['failure_probability'] = delta
    initExp_args_dict['args']['participant_to_algorithm_management'] = 'one_to_many' # 'one_to_one'  #optional field
    initExp_args_dict['args']['algorithm_management_settings'] = algorithm_management_settings #optional field
    initExp_args_dict['args']['alg_list'] = alg_list #optional field
    initExp_args_dict['args']['instructions'] = 'You want instructions, here are your test instructions'
    initExp_args_dict['args']['debrief'] = 'You want a debrief, here is your test debrief'
    initExp_args_dict['args']['targets'] = {}
    initExp_args_dict['args']['targets']['targetset'] = make_targetset()

    exp_info = []
    for ell in range(num_experiments):
      url = "http://"+HOSTNAME+":8000/api/experiment"
      response = requests.post(url, json.dumps(initExp_args_dict), headers={'content-type':'application/json'})
      print("POST initExp response =",response.text, response.status_code)
      if assert_200: assert response.status_code is 200
      initExp_response_dict = json.loads(response.text)

      exp_uid = initExp_response_dict['exp_uid']

      exp_info.append( {'exp_uid':exp_uid,} )

      #################################################
      # Test GET Experiment
      #################################################
      print('\n'*2 + 'Testing GET initExp...')
      url = "http://"+HOSTNAME+":8000/api/experiment/"+exp_uid
      response = requests.get(url)
      print("GET experiment response =",response.text, response.status_code)
      if assert_200: assert response.status_code is 200
      initExp_response_dict = json.loads(response.text)

      print('\nQuery URL available at http://{}:8000/query/query_page/query_page/{}\n'.format(HOSTNAME, exp_uid))
      return exp_uid



def timeit(f):
  """ 
  Utility used to time the duration of code execution. This script can be composed with any other script.

  Usage::\n
    def f(n): 
      return n**n  

    def g(n): 
      return n,n**n 

    answer0,dt = timeit(f)(3)
    answer1,answer2,dt = timeit(g)(3)
  """
  def timed(*args, **kw):
    ts = time.time()
    result = f(*args, **kw)
    te = time.time()
    if type(result)==tuple:
      return result + ((te-ts),)
    else:
      return result,(te-ts)
  return timed

if __name__ == '__main__':
  print(HOSTNAME)
  args = docopt(__doc__, version='NEXT')
  if args['launch']:
      exp_uids = {}
      for alg in ['CrowdKernel', 'ValidationSampling']:
          exp_uid = run_all(True, alg)
          exp_uids[alg] = exp_uid
      print(exp_uids)

  if args['scp']:
      os.system('scp -i "{}" query_page_choose.html ubuntu@{}:'.format(host_file, HOSTNAME) +
              '/usr/local/next-discovery/next/query_page/templates/query_page_choose.html')
      # to undo this scp, rsync from the main next folder
      os.system('scp -i "{}" getQuery_widget_delay.html ubuntu@{}:'.format(host_file, HOSTNAME) +
              '/usr/local/next-discovery/next/apps/Apps/PoolBasedTripletMDS/widgets/getQuery_widget.html')
