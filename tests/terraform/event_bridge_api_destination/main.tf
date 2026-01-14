

resource "aws_cloudwatch_event_bus" "messenger" {
  name = "chat-messages"
  tags = {
    Env = "Sandbox"
  }
}

resource "aws_cloudwatch_event_connection" "test" {
  name               = "c7n-test-connection"
  description        = "A connection for testing"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "x-api-key"
      value = "secret"
    }
  }
}

resource "aws_cloudwatch_event_api_destination" "api_destination" {
  name                = "c7n-test-api-destination"
  description         = "An API Destination for testing"
  invocation_endpoint = "https://example.com/webhook"
  http_method         = "POST"
  connection_arn      = aws_cloudwatch_event_connection.test.arn
}

resource "aws_iam_role" "event_bridge_role" {
  name = "c7n-eventbridge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_cloudwatch_event_rule" "test_rule" {
  name           = "test-rule"
  description    = "Capture all EC2 events"
  event_bus_name = aws_cloudwatch_event_bus.messenger.name

  event_pattern = jsonencode({
    source = ["aws.ec2"]
  })
}

resource "aws_cloudwatch_event_target" "test_target" {
  rule           = aws_cloudwatch_event_rule.test_rule.name
  event_bus_name = aws_cloudwatch_event_bus.messenger.name
  target_id      = "c7n-test-api-destination"
  arn            = aws_cloudwatch_event_api_destination.api_destination.arn
  role_arn       = aws_iam_role.event_bridge_role.arn
}
