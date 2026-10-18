output "app_server_public_ip" {
  description = "Public IPv4 address used by Ansible and HTTP tests."
  value       = aws_instance.app.public_ip
}
output "app_server_public_dns" {
  description = "Public DNS name of the EC2 server."
  value       = aws_instance.app.public_dns
}
output "backup_bucket_name" {
  description = "Private encrypted, versioned S3 bucket name."
  value       = aws_s3_bucket.backup.bucket
}
output "vpc_id" {
  value = aws_vpc.main.id
}
