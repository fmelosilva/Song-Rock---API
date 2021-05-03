from minio import Minio
from minio.error import S3Error
import ntpath

BUCKET = 'musics'

# Create a client with the MinIO server playground, its access key
# and secret key.
client = Minio(
    "play.min.io",
    access_key="Q3AM3UQ867SPQQA43P2F",
    secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
)

if not client.bucket_exists(BUCKET):
    client.make_bucket(BUCKET)
else:
    print(f"Bucket '{BUCKET}' already exists")


def upload(file_path: str) -> str:
    filename = ntpath.basename(file_path)
    client.fput_object(BUCKET, filename, file_path)
    url = client.presigned_get_object(
        BUCKET, filename)

    return url
