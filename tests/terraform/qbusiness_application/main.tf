# This throws and error sometimes, incase it's not ready yet, 
# login to the AWS console and copy the instance arn from the IAM identity center.
# IAM Identity Center -> Settings -> Instance ARN
# It looks like "arn:aws:sso:::instance/ssoins-78635ec621d04e34"

# data "aws_ssoadmin_instances" "example_sso" {}

resource "awscc_kms_key" "qbusiness_key" {
  key_policy = jsonencode({
    "Version" : "2012-10-17",
    "Id" : "KMS-Key-Policy",
    "Statement" : [
      {
        "Sid" : "EnableRootPermissions",
        "Effect" : "Allow",
        "Principal" : {
          "AWS" : "arn:aws:iam::794038253860:root"
        },
        "Action" : "kms:*",
        "Resource" : "*"
      }
    ]
  })
}


resource "awscc_kms_alias" "qbusiness_key_alias" {
  alias_name    = "alias/qbusiness"
  target_key_id = awscc_kms_key.qbusiness_key.key_id
  depends_on = [awscc_kms_key.qbusiness_key]
}

resource "awscc_qbusiness_application" "example_qbusines" {
  description  = "Custodian QBusiness Application"
  display_name = "custodian_q_app"
  identity_type = "AWS_IAM_IDC"
  identity_center_instance_arn = "arn:aws:sso:::instance/ssoins-72235ec621d04e34" #data.aws_ssoadmin_instances.example_sso.arns[0] # This is the instance arn from the IAM Identity Center
  depends_on = [awscc_kms_key.qbusiness_key, awscc_kms_alias.qbusiness_key_alias]
  attachments_configuration = {
    attachments_control_mode = "ENABLED"
  }
  q_apps_configuration = {
    q_apps_control_mode = "ENABLED"
  }
  encryption_configuration = {
    kms_key_id = awscc_kms_key.qbusiness_key.key_id
  }
  auto_subscription_configuration = {
    auto_subscribe = "ENABLED"
    default_subscription_type = "Q_LITE"
  }
  tags = [{
    key   = "Owner"
    value = "CloudCustodian"
  }]
}
