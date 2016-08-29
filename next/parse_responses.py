import pandas as pd
import json

def format_triplet_response_json(response_dict):
    """
    Return formatted participant logs that are app specific.

    Taken from NEXT-psych gui/base/app_manager/Triplets.py[1]. This script is on
    the GUI frontend for NEXT. It pings the backend to get the same JSON
    (commented out in this function).

    :input response_dict: The raw response data as a JSON object.
    :output: The output as a list of strings, with one string per response.

    >>> x = get_formatted_participant_data(dict)
    >>> x[0:2]
    ['Participant ID,Timestamp,Center,Left,Right,Answer,Alg Label',
 u'oeJq63j...,Lewis_LAlanine.jpg,Lewis_C2H3Cl.png,Lewis_PO43-.png,Lewis_PO43-.png,Test']

    [1]:https://github.com/kgjamieson/NEXT-psych/blob/master/gui/base/app_manager/PoolBasedTripletMDS/PoolBasedTripletMDS.py#L71
    """
    participant_responses = [["Participant ID", "Timestamp","Center", "Left",
        "Right", "Answer", "Alg Label"]]
    for participant_id, response_list in response_dict['participant_responses'].items():
        exp_uid, participant_id = participant_id.split('_')
        for response in response_list:
            line = [participant_id, response['timestamp_query_generated']]
            targets = {}
            target_winner = None
            for index in response['target_indices']:
                targets[index['label']] = index
                # Check for the index winner in this response
                # Shouldn't we check for target_winner?
                if 'target_winner' in list(response.keys()) \
                        and response['target_winner'] == index['target_id']:
                    target_winner = index
            if target_winner:
                # Append the center, left, right targets
                line.extend([targets['center']['target_id'], \
                             targets['left']['target_id'],\
                             targets['right']['target_id']])
                # Append the target winner
                line.append(target_winner['target_id'])
                # Append the alg_label
                line.append(response['alg_label'])
                participant_responses += [line]

    header = participant_responses.pop(0)
    return pd.DataFrame(participant_responses, columns=header)


if __name__ == "__main__":
    dir_ = 'data-save/'
    filenames = {'STE': '2016-08-03-participant1-STE-responses.json',
                 'validation': '2016-08-03-participant1-validation-respones.json'}
    filenames = {'STE': '2016-08-08-participant-3-STE.json',
                 'validation': '2016-08-08-participant-3-ValidationSampling.json'}
    responses = {}
    for alg, filename in filenames.items():
        with open(dir_ + filename) as f:
            response = json.load(f)
        responses[alg] = format_triplet_response_json(response)
    responses = pd.concat(responses)

    out = '2016-08-08-participant3-responses.csv'
    responses.to_csv(out)
