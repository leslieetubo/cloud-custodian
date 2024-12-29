# This throws and error sometimes, incase it's not ready yet, 
# login to the AWS console and copy the instance arn from the IAM identity center.
# IAM Identity Center -> Settings -> Instance ARN
# It looks like "arn:aws:sso:::instance/ssoins-78635ec621d04e34"

data "aws_ssoadmin_instances" "example_sso" {}

resource "awscc_qbusiness_application" "example_qbusines" {
  description  = "Example QBusiness Application"
  display_name = "example_q_app"
  identity_center_instance_arn = data.aws_ssoadmin_instances.example_sso.arns[0] # This is the instance arn from the IAM Identity Center
  attachments_configuration = {
    attachments_control_mode = "ENABLED"
  }
  tags = [{
    key   = "Owner"
    value = "CloudCustodian"
  }]
}
