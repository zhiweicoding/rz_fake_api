from fastapi import FastAPI, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse
from minio import Minio
from minio.error import S3Error
import os
import tempfile

app = FastAPI()

# MinIO客户端配置
minio_client = Minio(
    "172.16.5.122:31900",
    access_key="admin",
    secret_key="Devops2020",
    secure=False  # Set True for https
)


def remove_file(path: str):
    try:
        os.unlink(path)
    except Exception as e:
        print(f"Failed to delete temporary file {path}: {str(e)}")


@app.post("/receice_data/getPicPath")
async def get_image(background_tasks: BackgroundTasks, id: str = Form(...)):
    # 使用tempfile安全地创建临时文件
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(id)[1])
    try:
        print(f"id:{id}")
        # 尝试从MinIO获取图片
        response = minio_client.get_object('sdk', f'/rz/abnormal/{id}')

        with open(temp_file.name, "wb") as file_data:
            for data in response.stream(32 * 1024):
                file_data.write(data)

        temp_file_path = temp_file.name
        # Add file removal to background task
        background_tasks.add_task(remove_file, temp_file_path)
        # 返回图片文件响应
        return FileResponse(temp_file.name, filename=os.path.basename(id), media_type='application/octet-stream')
    except S3Error as e:
        # 如果在MinIO中找不到图片，返回错误
        raise HTTPException(status_code=404, detail=str(e))
