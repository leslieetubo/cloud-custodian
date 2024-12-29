# Copyright 2020 Cloud Custodian Authors
# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from pytest_terraform import terraform



@terraform('qbusiness_application')
def test_qbusiness_describe(test, qbusiness_application):
    factory = test.replay_flight_data('qbusiness_application')
    p = test.load_policy({
        'name': 'test_qbusiness_application', 'resource': 'aws.qbusiness', 'filters': [
        {'type': 'value', 'key': 'displayName', 'value': 'example_q_app', 'op': 'eq'}
    ]},
        session_factory=factory)
    resources = p.run()
    test.assertEqual(len(resources), 1)
