# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from pytest_terraform import terraform

from .common import BaseTest
from c7n.utils import local_session


@terraform("quicksight_group")
def test_quicksight_group_query(test, quicksight_group):
    factory = test.replay_flight_data("test_quicksight_group_query")

    policy = test.load_policy({
      "name": "test-aws-quicksight-group",
      "resource": "aws.quicksight-group"
    }, session_factory=factory, config={'account_id': '490065885863'})

    resources = policy.run()
    assert len(resources) > 0
    assert resources[0]['GroupName'] == 'tf-example'


class TestQuicksight(BaseTest):

    def test_quicksight_account_query(self):
        factory = self.replay_flight_data("test_quicksight_account_query")

        policy = self.load_policy({
            "name": "test-aws-quicksight-account",
            "resource": "aws.quicksight-account",
            "filters": [{"PublicSharingEnabled": False}]
        }, session_factory=factory)

        resources = policy.run()
        self.assertEqual(len(resources), 1)

    def test_quicksight_account_get_account_not_found(self):
        factory = self.replay_flight_data("test_quicksight_account_not_found")

        policy = self.load_policy({
            "name": "test-aws-quicksight-account",
            "resource": "aws.quicksight-account"
        }, session_factory=factory)

        resources = policy.run()
        self.assertEqual(resources, [])

    def test_quicksight_account_from_non_identity_region(self):
        factory = self.replay_flight_data("test_quicksight_account_from_non_identity_region")

        policy = self.load_policy({
            "name": "test-aws-quicksight-account",
            "resource": "aws.quicksight-account"
        }, session_factory=factory, config={'region': 'us-west-2'})

        resources = policy.run()
        self.assertEqual(len(resources), 0)

    def test_quicksight_account_standard_edition(self):
        factory = self.replay_flight_data("test_quicksight_account_standard_edition")

        policy = self.load_policy({
            "name": "test-aws-quicksight-account",
            "resource": "aws.quicksight-account",
        }, session_factory=factory)

        resources = policy.run()
        self.assertEqual(resources, [])

    def test_quicksight_user_query(self):
        factory = self.replay_flight_data("test_quicksight_user_query")

        policy = self.load_policy({
            "name": "test-aws-quicksight-user",
            "resource": "aws.quicksight-user"
        }, session_factory=factory)

        resources = policy.run()
        self.assertGreater(len(resources), 0)
        self.assertIn('UserName', resources[0])

    def test_quicksight_user_delete(self):
        factory = self.replay_flight_data("test_quicksight_user_delete")

        policy = self.load_policy({
            "name": "test-aws-quicksight-user-delete",
            "resource": "aws.quicksight-user",
            "actions": [{"type": "delete"}]
        }, session_factory=factory)

        resources = policy.run()
        self.assertGreater(len(resources), 0)
        self.assertIn('UserName', resources[0])

        client = local_session(factory).client('quicksight')
        users = client.list_users(
            AwsAccountId=self.account_id,
            Namespace='default'
        )["UserList"]
        self.assertEqual(len(users), 0)
