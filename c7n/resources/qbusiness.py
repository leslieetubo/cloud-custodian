# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0
from email.mime import application
from botocore.exceptions import ClientError


from c7n.filters.core import Filter
from c7n.filters.kms import KmsRelatedFilter
from c7n.manager import resources
from c7n.utils import local_session
from c7n.query import ConfigSource, DescribeSource, QueryResourceManager, TypeInfo
from c7n.actions import BaseAction


class ConfigQBusiness(ConfigSource):

    def load_resource(self, item):
        # TODO: return a list of applications
        return item


class DescribeQBusiness(DescribeSource):

    def resources(self, query):
        client = local_session(self.manager.session_factory).client('qbusiness')
        try:
            paginator = client.get_paginator('list_applications')
            resources = []
            for page in paginator.paginate():
                for app in page.get('applications', []):
                    app_id = app.get('applicationId', '')
                    if app_id:
                        app['applicationId'] = app_id
                        resources.append(app)
            return resources
        except ClientError as e:
            self.manager.log.error(f"Error retrieving QBusiness applications: {e}")
            return []


@resources.register('qbusiness')
class QBusiness(QueryResourceManager):
    class resource_type(TypeInfo):
        service = 'qbusiness'
        arn_type = ""
        enum_spec = ('list_applications', 'applications', None)
        detail_spec = ("get_application", "applicationId", "applicationId", None)
        cfn_type = config_type = 'AWS::QBusiness::Application'
        id = 'applicationId'
        arn = "applicationArn"
        name = 'displayName'
        date = 'createdAt'
        dimension = 'ChatMessages'
        universal_taggable = object()
        global_resource = False
        permissions_augment = ("qbusiness:ListTagsOfResource",)

    source_mapping = {
        'describe': DescribeQBusiness,
        'config': ConfigQBusiness
    }


@QBusiness.filter_registry.register('kms-key')
class KmsFilter(KmsRelatedFilter):
    RelatedIdsExpression = 'encryptionConfiguration.kmsKeyId'


@QBusiness.filter_registry.register('has-blocked-phrases')
class HasBlockedPhrases(Filter):
    """Filters QBusiness applications that have blocked phrases

    :example:

    .. code-block:: yaml

        policies:
          - name: qbusiness-has-blocked-phrases
            resource: qbusiness
            filters:
              - type: has-blocked-phrases
                blocked_phrases: ["restricted term", "forbidden phrase"]
    """
    permissions = ("qbusiness:GetApplication",)
    schema = {
        'type': 'object',
        'properties': {
            'type': {'enum': ['has-blocked-phrases']},
            'blocked_phrases': {'type': 'array', 'items': {'type': 'string'}}
        },
        'required': ['blocked_phrases']
    }

    def process(self, resources, event=None):
        blocked_phrases = self.data.get('blocked_phrases', [])
        results = []
        for resource in resources:
            if any(phrase in resource.get('blockedPhrases', []) for phrase in blocked_phrases):
                results.append(resource)
        return results


# TODO: Create actions here
@QBusiness.action_registry.register('tag')
class TagQBusinessApplication(BaseAction):
    """Action to tag QBusiness applications

    Just used of Qbusiness and Qapps
    Sources:
      - elb (Access Log)
      - s3 (Access Log)
      - cfn (Template writes)
      - cloudtrail

    :example:

    .. code-block:: yaml

        policies:
          - name: tag-qbusiness-app
            resource: qbusiness
            actions:
              - type: tag
                key: Environment
                value: Production
    """
    permissions = ("qbusiness:TagResource",)
    schema = {
        'type': 'object',
        'properties': {
            'type': {'enum': ['tag']},
            'key': {'type': 'string'},
            'value': {'type': 'string'}
        },
        'required': ['key', 'value']
    }

    def process(self, resources):
        client = local_session(self.manager.session_factory).client('qbusiness')
        for resource in resources:
            client.tag_resource(
                ResourceArn=resource['arn'],
                Tags=[{'Key': self.data['key'], 'Value': self.data['value']}]
            )
