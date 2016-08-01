"""
Usage:
    launch_lucid_brain.py launch
    launch_lucid_brain.py scp
"""
from __future__ import print_function
import json
import time
import requests
from multiprocessing import Pool
from docopt import docopt
import os
import pickle
import numpy as np
np.random.seed(42)


def make_targetset():
    return [{'target_id': str(i),
             'primary_type': 'text',
             'primary_description': str(i + 1),
             'alt_type': 'text',
             'alt_description': str(i + 1)} for i in range(12)]


def generate_query(list_):
    q = np.random.randint(12, size=(3,))
    while (q.tolist() in list_ or q[0] == q[1] or q[1] == q[2] or
           q[0] == q[-1]):
        q = np.random.randint(12, size=(3,))
    return q.tolist()


def generate_query_list(n):
    query_list = []
    for n in range(n):
        query_list += [generate_query(query_list)]
    return query_list


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
    supported_alg_ids = [alg]

    alg_list = []
    for idx,alg_id in enumerate(supported_alg_ids):
        alg_item = {}
        alg_item['alg_id'] = alg_id
        if alg_id == 'ValidationSampling':
            alg_item['alg_label'] = 'Test'
            alg_item['params'] = {'query_list': generate_query_list(12)}
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
    initExp_args_dict['args']['num_tries'] = 200
    initExp_args_dict['args']['targets'] = {}
    initExp_args_dict['args']['targets']['targetset'] = make_targetset()

    exp_info = []
    for ell in range(num_experiments):
        url = "http://"+HOSTNAME+":8000/api/experiment"
        response = requests.post(url,
                                 json.dumps(initExp_args_dict),
                                            headers={'content-type': 'application/json'})
        print("POST initExp response =", response.text, response.status_code)
        if assert_200:
            assert response.status_code is 200
        initExp_response_dict = json.loads(response.text)

        exp_uid = initExp_response_dict['exp_uid']

        exp_info.append({'exp_uid': exp_uid})

        #################################################
        # Test GET Experiment
        #################################################
        print('\n'*2 + 'Testing GET initExp...')
        url = "http://"+HOSTNAME+":8000/api/experiment/"+exp_uid
        response = requests.get(url)
        print("GET experiment response =", response.text, response.status_code)
        if assert_200:
            assert response.status_code is 200
        initExp_response_dict = json.loads(response.text)

        print('\nQuery URL available at '
              'http://{}:8000/query/query_page/'.format(HOSTNAME) +
              'query_page/{}\n'.format(exp_uid))
        return exp_uid



def timeit(f):
  """ 

  Utility used to time the duration of code execution. This script can be
  composed with any other script.

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

def put_exp_uids_in(name, exp_uids):
    out_file = open(name + '_out.html', 'wb')
    with open(name + '.html', 'rb') as f:
        for line in f.readlines():
            process = False
            if '# random list' in line:
                random_list = np.random.randint(4, 190, size=(20,))
                random_list = np.sort(random_list).tolist()
                line = """ 
          var validation_queries = {};
""".format(random_list)
            if 'ValidationSampling' in line:
                exp_uid = '{}'.format(exp_uids['ValidationSampling'])
                process = True
            if 'STE' in line:
                exp_uid = '{}'.format(exp_uids['STE'])
                process = True
            if process:
                line = ' '*15 + 'exp_uid = "{}";\n'.format(exp_uid)
                del exp_uid
            print(line, file=out_file, end='')

if __name__ == '__main__':
    HOSTNAME = os.environ.get('NEXT_BACKEND_GLOBAL_HOST', 'localhost')
    host_file = os.environ.get('KEY_FILE')
    print(HOSTNAME)
    args = docopt(__doc__, version='NEXT')
    exp_uid_filename = 'exp_uids.pkl'
    if args['launch']:
        exp_uids = {}
        for alg in ['STE', 'ValidationSampling']:
            exp_uid = run_all(True, alg)
            exp_uids[alg] = exp_uid
        print(exp_uids)
        pickle.dump(exp_uids, open(exp_uid_filename, 'wb'))

    if args['scp']:
        exp_uids = pickle.load(open(exp_uid_filename, 'rb'))
        put_exp_uids_in('query_page_choose', exp_uids)

        # to undo this scp, rsync from the main next folder
        os.system('scp -i "{}" getQuery_widget_delay.html ubuntu@{}:'.format(host_file, HOSTNAME) +
                '/usr/local/next-discovery/next/apps/Apps/PoolBasedTripletMDS/widgets/getQuery_widget.html')

        os.system('scp -i "{}" query_page_choose_out.html ubuntu@{}:'.format(
                  host_file, HOSTNAME) +
                  '/usr/local/next-discovery/next/query_page/templates/query_page_choose.html')

        print('\nQuery URL:\nhttp://{}:8000/query/query_page/query_page_choose/{}'
              .format(HOSTNAME, exp_uids['STE']))
