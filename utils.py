SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
=======
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BUCKET_NAME = "Mundiclass"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
>>>>>>> REPLACE
=======
async def upload_image_to_supabase(file: UploadFile, bucket_name: str = "Mundiclass") -> str:
    """
    Uploads an image file to the Supabase storage bucket and returns the public URL.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL or Key not configured in environment variables")

    file_extension = file.filename.split(".")[-1]
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Read file content
    file_content = await file.read()

    # Upload file to Supabase bucket
    response = supabase.storage.from_(bucket_name).upload(unique_filename, file_content)

    if response.get("error"):
        raise RuntimeError(f"Error uploading file to Supabase: {response['error']['message']}")

    # Get public URL
    public_url_response = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
    public_url = public_url_response.get("publicUrl")
    if not public_url:
        raise RuntimeError("Failed to get public URL after upload")

    return public_url
=======

async def upload_image_to_supabase(file: UploadFile) -> str:
    """
    Uploads an image file to the Supabase storage bucket and returns the public URL.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL or Key not configured in environment variables")

    file_extension = file.filename.split(".")[-1]
    # Generate unique filename using UUID
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Read file content
    file_content = await file.read()

    # Upload file to Supabase bucket
    response = supabase.storage.from_(BUCKET_NAME).upload(unique_filename, file_content)

    if response.get("error"):
        raise RuntimeError(f"Error uploading file to Supabase: {response['error']['message']}")

    # Get public URL
    public_url_response = supabase.storage.from_(BUCKET_NAME).get_public_url(unique_filename)
    public_url = public_url_response.get("publicUrl")
    if not public_url:
        raise RuntimeError("Failed to get public URL after upload")

    return public_url
