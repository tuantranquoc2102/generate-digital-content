import boto3, os, uuid
from urllib.parse import quote_plus

S3_ENDPOINT=os.getenv("S3_ENDPOINT","http://localhost:9000")
S3_REGION=os.getenv("S3_REGION","us-east-1")
S3_ACCESS_KEY=os.getenv("S3_ACCESS_KEY","minio")
S3_SECRET_KEY=os.getenv("S3_SECRET_KEY","minio123")
S3_BUCKET=os.getenv("S3_BUCKET","uploads")

# Public endpoint cho frontend (có thể khác với internal endpoint)
S3_PUBLIC_ENDPOINT=os.getenv("S3_PUBLIC_ENDPOINT","http://localhost:9000")

def s3_client():
  return boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
  )

def ensure_bucket_exists():
  """Ensure S3 bucket exists, create if not"""
  try:
    client = s3_client()
    # Try to create bucket directly - MinIO won't error if it exists
    client.create_bucket(Bucket=S3_BUCKET)
    print(f"Ensured bucket exists: {S3_BUCKET}")
  except client.exceptions.BucketAlreadyExists:
    # Bucket already exists, which is fine
    pass
  except client.exceptions.BucketAlreadyOwnedByYou:
    # Bucket already owned by us, which is fine
    pass
  except Exception as e:
    print(f"Warning: Could not ensure bucket {S3_BUCKET} exists: {e}")
    # Continue anyway - bucket might exist or be accessible

def gen_file_key(filename:str)->str:
  ext = filename.split(".")[-1] if "." in filename else "bin"
  return f"audios/{uuid.uuid4()}.{ext}"

def presign_put(file_name:str, content_type:str):
  # Ensure bucket exists before creating presigned URL
  ensure_bucket_exists()
  
  key = gen_file_key(file_name)
  client = s3_client()
  url = client.generate_presigned_url(
    ClientMethod="put_object",
    Params={"Bucket": S3_BUCKET, "Key": key, "ContentType": content_type},
    ExpiresIn=3600
  )
  
  # Replace internal endpoint with public endpoint for frontend
  if S3_ENDPOINT != S3_PUBLIC_ENDPOINT:
    url = url.replace(S3_ENDPOINT, S3_PUBLIC_ENDPOINT)
  
  return url, key