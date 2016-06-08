"""
Usage:
    launch_lucid_brain.py launch
    launch_lucid_brain.py scp <exp_uid1> <exp_uid2>
    launch_lucid_brain.py scp
"""
from __future__ import print_function
import numpy
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
HOSTNAME = os.environ.get('NEXT_BACKEND_GLOBAL_HOST', 'localhost')
host_file = os.environ.get('KEY_FILE')

def run_all(assert_200):

  num_objects = 5
  desired_dimension = 2
  x = numpy.linspace(0,1,num_objects)
  X_true = numpy.vstack([x,x]).transpose()
  total_pulls_per_client = 20
  num_experiments = 1
  # clients run in simultaneous fashion using multiprocessing library
  num_clients = 5

  pool = Pool(processes=num_clients)
  # input test parameters
  delta = 0.01
  supported_alg_ids = ['RandomSampling','RandomSampling','UncertaintySampling','CrowdKernel', 'STE']

  alg_list = []
  for idx,alg_id in enumerate(supported_alg_ids):
    alg_item = {}
    alg_item['alg_id'] = alg_id
    if idx==0:
      alg_item['alg_label'] = 'Test'
    else:
      alg_item['alg_label'] = alg_id
    alg_item['test_alg_label'] = 'Test'
    alg_list.append(alg_item)
  params = []
  for algorithm in alg_list:
    params.append(  { 'alg_label': algorithm['alg_label'] , 'proportion':1./len(alg_list) }  )
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
  initExp_args_dict['args']['targets']['n'] = num_objects

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
      run_all(False)

  if args['scp']:
      if args['<exp_uid1>'] != None and args['<exp_uid2>'] != None:
          with open('query_page_choose.html', 'r+') as f:
              new_file = []
              for line in f.readlines():
                  if 'exp1' in line:
                      line = ' '*6*4 + '"' + args['<exp_uid1>'] + '", // exp1\n'
                  if 'exp2' in line:
                      line = ' '*6*4 + '"' + args['<exp_uid1>'] + '" // exp2\n'
                  new_file += [line[:-1]]
          with open('query_page_choose_out.html', 'w') as f:
              print("\n".join(new_file), file=f)

          os.system('scp -i "{}" query_page_choose_out.html ubuntu@{}:'.format(host_file, HOSTNAME) +
                  '/usr/local/next-discovery/next/query_page/templates/query_page_choose.html')
      # to undo this scp, rsync from the main next folder
      os.system('scp -i "{}" getQuery_widget_delay.html ubuntu@{}:'.format(host_file, HOSTNAME) +
              '/usr/local/next-discovery/next/apps/Apps/PoolBasedTripletMDS/widgets/getQuery_widget.html')
