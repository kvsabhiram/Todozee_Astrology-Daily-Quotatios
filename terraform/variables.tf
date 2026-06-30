variable "aws_region" {
  description = "AWS region (Mumbai)."
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Name prefix for resources."
  type        = string
  default     = "todozee-astrology"
}

variable "ecr_repo_name" {
  description = "ECR repository name (must match the GitHub workflow's ECR_REPO)."
  type        = string
  default     = "todozee-astrology"
}

variable "instance_type" {
  description = "GPU instance type. g6.xlarge = NVIDIA L4 24GB, native bf16, cu128-capable."
  type        = string
  default     = "g6.xlarge"
}

variable "root_volume_gb" {
  description = "Root EBS size. Image bakes in the Gemma model + cu128 torch, so keep this generous."
  type        = number
  default     = 150
}

variable "ami_id" {
  description = "Optional AMI override. Empty = latest Ubuntu 22.04 (driver installed by ec2_bootstrap.sh)."
  type        = string
  default     = ""
}

variable "app_port" {
  description = "Port the FastAPI service listens on."
  type        = number
  default     = 7005
}

variable "allowed_cidr" {
  description = "CIDR allowed to reach the app port (and SSH if key set). Use your IP/32 to lock down."
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_key_name" {
  description = "Optional EC2 key pair name for SSH. Empty = no SSH (use SSM Session Manager)."
  type        = string
  default     = ""
}

variable "github_repo" {
  description = "owner/repo that GitHub Actions OIDC is scoped to."
  type        = string
  default     = "kvsabhiram/Todozee_Astrology-Daily-Quotatios"
}

variable "github_oidc_branch" {
  description = "Branch ref the OIDC role trusts for deploys."
  type        = string
  default     = "main"
}

variable "create_github_oidc_provider" {
  description = <<-EOT
    Create the GitHub OIDC provider. FALSE here because the account already has an
    IAM OIDC provider for token.actions.githubusercontent.com (created by the
    classifier stack) — only one is allowed per account.
  EOT
  type        = bool
  default     = false
}
