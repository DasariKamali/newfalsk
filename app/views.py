import os
from flask import Blueprint, request, Response
from .azure_blob import get_blob_client

forecasting_bp = Blueprint('forecasting_bp', __name__)

def stream_blob(blob_client, chunk_size=1024*1024):
    """Generator function to stream the blob in chunks."""
    blob_size = blob_client.get_blob_properties().size
    start = 0

    while start < blob_size:
        end = min(start + chunk_size, blob_size)
        download_stream = blob_client.download_blob(offset=start, length=chunk_size)
        chunk = download_stream.readall()
        yield chunk
        start = end

@forecasting_bp.route("/api/download/", methods=["GET"])
def download():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    
    report = request.args.get("report")
    config_id = request.args.get("config_id")
    extension = request.args.get("extension", ".csv")
    filename = f"{report}{config_id}{extension}"
    blobpath = f"{config_id}/{filename}"

    blob_client = get_blob_client(connection_string, container_name)
    blob_client = blob_client.get_blob_client(blob=blobpath)

    response = Response(
        stream_blob(blob_client, chunk_size=1024*1024),
        content_type='application/octet-stream',
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

    return response
