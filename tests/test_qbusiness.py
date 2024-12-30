# Copyright 2020 Cloud Custodian Authors
# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from pytest_terraform import terraform



@terraform('qbusiness_application')
def test_qbusiness_kms(test, qbusiness_application):
    factory = test.replay_flight_data('test_qbusiness')
    policy = {
        'name': 'test_qbusiness_kmsfilter',
        'resource': 'aws.qbusiness',
        'filters': [
            {'type': 'kms-key', 'key': 'c7n:AliasName', 'value': 'alias/qbusiness'}
        ]
    }
    p = test.load_policy(policy, session_factory=factory)
    resources = p.run()
    test.assertEqual(len(resources), 1)

@terraform('qbusiness_application')
def test_qbusiness_describe(test, qbusiness_application):
    factory = test.replay_flight_data('test_qbusiness')
    p = test.load_policy({
        'name': 'test_qbusiness_application', 'resource': 'aws.qbusiness', 'filters': [
        {'type': 'value', 'key': 'displayName', 'value': 'custodian_q_app'}
    ]},
        session_factory=factory)
    resources = p.run()
    test.assertEqual(len(resources), 1)

# @terraform('qbusiness_application')
# def test_qbusiness_blocked_phrases_filter(test, qbusiness_application):
#     factory = test.replay_flight_data('qbusiness_application')
#     p = test.load_policy({
#         'name': 'test_qbusiness_application', 'resource': 'aws.qbusiness', 'filters': [
#         {'type': 'has-blocked-phrases', 'blocked_phrases': 'displayName', 'value': 'example_q_app', 'op': 'eq'}
#     ]},
#         session_factory=factory)
#     resources = p.run()
#     test.assertEqual(len(resources), 1)
 