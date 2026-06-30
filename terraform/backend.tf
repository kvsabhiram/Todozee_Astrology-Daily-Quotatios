# Remote state backend — reuses the existing todozee state bucket + lock table
# (already created for the classifier). Only the key differs, so this project's
# state lives side-by-side without a separate bootstrap.
terraform {
  backend "s3" {
    bucket         = "todozee-tfstate-637560253183"
    key            = "todozee/astrology.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "todozee-tf-locks"
    encrypt        = true
  }
}
