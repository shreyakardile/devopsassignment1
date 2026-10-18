# Enterprise Student Record & Academic Management Platform
## DevOps Unit 4 — Infrastructure Automation with Terraform and Ansible on AWS

This repository contains a student-project implementation based on the supplied CAREERTIQ Unit 4 assignment brief.

### Architecture
- AWS VPC: `10.1.0.0/16`; public subnet: `10.1.1.0/24`
- Ubuntu 22.04 EC2 instance (default `t2.micro`) with encrypted 20 GiB gp3 root volume
- Security group: SSH (restricted to your IP), HTTP 80, application port 8080
- Private S3 bucket for backup artifacts: public access blocked, AES-256 encryption and versioning enabled
- Terraform provisions AWS infrastructure.
- Ansible configures the EC2 host, installs Docker and Nginx, deploys the Flask container, and validates the service.
- Flask endpoints: `GET /api/health`, `GET /api/students`, `POST /api/marks`, `GET /api/marks`

> Important: This is deployment-ready project code, but no cloud deployment is claimed here. Actual deployment requires your own AWS account/credentials, an EC2 key pair, and running the commands below. Never commit credentials, private keys, Terraform state, or real student data.

## Prerequisites
- Terraform 1.7+
- Ansible 2.16+
- AWS CLI v2
- AWS account permissions for VPC, EC2, and S3
- An EC2 key pair in the target AWS region
- SSH access from your current public IP
- Python 3.10+ and Docker (only for local testing)

## 1. Configure AWS
Configure credentials using `aws configure` or an approved AWS SSO profile. Do not put access keys in source files. Create an EC2 key pair in the same region, then set `key_name` in `terraform/terraform.tfvars`.

## 2. Configure Terraform
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```
Edit `terraform.tfvars`: set `aws_region`, the existing `key_name`, your public IP in `admin_cidr` form (e.g. `203.0.113.10/32` is only an example; replace it), and a unique lowercase `project_name`.

Do not use `0.0.0.0/0` for SSH in a real deployment.

## 3. Provision infrastructure
```bash
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
terraform output
```
Review the plan before approving `terraform apply`. This may create billable AWS resources.

## 4. Configure Ansible
From the project root, install required collections:
```bash
ansible-galaxy collection install -r ansible/requirements.yml
```
Get the public IP:
```bash
cd terraform
terraform output -raw app_server_public_ip
```
Copy it into `ansible/inventory.ini` in place of `REPLACE_WITH_TERRAFORM_OUTPUT`. Replace the SSH private key path with your actual key. Run from the repository root:
```bash
ansible -i ansible/inventory.ini library_servers -m ping
ansible-playbook -i ansible/inventory.ini ansible/site.yml
```
On Windows, run Ansible from WSL2 or a Linux control machine; native Windows is not the supported Ansible control node.

## 5. Validate
Replace `<PUBLIC_IP>` with the Terraform output:
```bash
curl http://<PUBLIC_IP>/api/health
curl http://<PUBLIC_IP>/api/students
curl -X POST http://<PUBLIC_IP>/api/marks -H "Content-Type: application/json" -d '{"student_id":1,"subject":"DevOps","marks":88,"max_marks":100}'
```
Expected health response:
```json
{"status":"UP","service":"student-record-api"}
```

## 6. Cleanup
To avoid ongoing charges, from `terraform/` run:
```bash
terraform destroy
```
Review the destruction plan carefully. S3 deletion can be blocked if it contains objects; only empty it if the contents are disposable.

## Repository layout
```text
.
├── app/                       # Flask API, SQLite model, requirements
├── terraform/                 # AWS VPC, subnet, EC2, SG, S3 and outputs
├── ansible/
│   ├── inventory.ini
│   ├── ansible.cfg
│   ├── site.yml
│   └── roles/                  # common, docker, nginx, library_app
├── report/                    # Technical report
└── .gitignore
```

## Scope and safety notes
- The assignment adaptation specifies VPC `10.1.0.0/16`, ports 22/80/8080, EC2 `t2.micro`, Dockerized Flask application, and API smoke tests.
- The sample app is a teaching/demo implementation. Do not load it with sensitive student data.
- The S3 bucket is provisioned, but automatic copying of SQLite files to S3 is not configured yet.
- Terraform uses local state for a straightforward first run. For team use, configure a remote S3 backend and state locking before collaboration.
- HTTP is used because the brief specifies port 80. Add HTTPS/TLS and stronger identity controls before production use.
