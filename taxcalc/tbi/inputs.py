import msgpack, json

import numpy as np

from taxcalc import Policy, Behavior

def get_defaults(start_year, **kwargs):
    pol = Policy()
    pol.set_year(start_year)
    pol_mdata = pol.metadata()
    behv_mdata = Behavior()._vals

    return {"policy": pol_mdata, "behavior": behv_mdata}


def parse_user_inputs(params, jsonstrs, errors_warnings, data_source,
                      use_full_sample, start_year):
    policy_inputs = params["policy"]
    behavior_inputs = params["behavior"]
    policy_inputs = {"policy": policy_inputs}

    policy_inputs_json = json.dumps(policy_inputs, indent=4)

    assumption_inputs = {
        "behavior": behavior_inputs,
        "growdiff_response": {},
        "consumption": {},
        "growdiff_baseline": {},
        "growmodel": {},
    }

    assumption_inputs_json = json.dumps(assumption_inputs, indent=4)

    policy_dict = taxcalc.Calculator.read_json_param_objects(
        policy_inputs_json, assumption_inputs_json
    )
    # get errors and warnings on parameters that do not cause ValueErrors
    tc_errors_warnings = taxcalc.tbi.reform_warnings_errors(
        policy_dict, data_source
    )
    # errors_warnings contains warnings and errors separated by each
    # project/project module
    for project in tc_errors_warnings:
        errors_warnings[project] = parse_errors_warnings(
            tc_errors_warnings[project]
        )

    # separate reform and assumptions
    reform_dict = policy_dict["policy"]
    assumptions_dict = {
        k: v for k, v in list(policy_dict.items()) if k != "policy"
    }

    params = {"policy": reform_dict, **assumptions_dict}
    jsonstrs = {"policy": policy_inputs, "assumptions": assumption_inputs}

    return (
        params,
        jsonstrs,
        errors_warnings,
    )

def parse_errors_warnings(errors_warnings):
    """
    Parse error messages so that they can be mapped to webapp param ID. This
    allows the messages to be displayed under the field where the value is
    entered.

    returns: dictionary 'parsed' with keys: 'errors' and 'warnings'
        parsed['errors/warnings'] = {year: {tb_param_name: 'error message'}}
    """
    parsed = {"errors": defaultdict(dict), "warnings": defaultdict(dict)}
    for action in errors_warnings:
        msgs = errors_warnings[action]
        if len(msgs) == 0:
            continue
        for msg in msgs.split("\n"):
            if len(msg) == 0:  # new line
                continue
            msg_spl = msg.split()
            msg_action = msg_spl[0]
            year = msg_spl[1]
            curr_id = msg_spl[2]
            msg_parse = msg_spl[2:]
            parsed[action][curr_id][year] = " ".join(
                [msg_action] + msg_parse + ["for", year]
            )
    return parsed

