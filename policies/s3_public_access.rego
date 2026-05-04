package terraform.analysis

# Identify all S3 buckets defined in the plan
buckets := {name | resource := input.resource_changes[_]; resource.type == "aws_s3_bucket"; name := resource.address}

# Identify all public_access_block resources defined
blocks := {name | resource := input.resource_changes[_]; resource.type == "aws_s3_bucket_public_access_block"; name := resource.change.after.bucket}

# Deny if a bucket is present but no corresponding public_access_block is attached
deny[msg] {
    bucket := buckets[_]
    # Check if the bucket has a corresponding block configuration
    not blocks[bucket]
    
    msg := sprintf("Security Violation: S3 bucket '%v' is missing the 'aws_s3_bucket_public_access_block' resource. Public access must be explicitly blocked.", [bucket])
}
