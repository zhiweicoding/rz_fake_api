from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse
from minio import Minio
from minio.error import S3Error
import os

app = FastAPI()

# MinIO客户端配置
minio_client = Minio(
    "172.16.5.122:31900",
    access_key="admin",
    secret_key="Devops2020",
    secure=False  # Set True for https
)


@app.post("/get-image/")
async def get_image(key: str = Form(...)):
    try:
        # 尝试从MinIO获取图片
        response = minio_client.get_object('your-bucket-name', key)
        # 存储图片到临时文件
        temp_file_path = f"temp_{key}"
        with open(temp_file_path, "wb") as file_data:
            for data in response.stream(32 * 1024):
                file_data.write(data)

        # 返回图片文件响应
        return FileResponse(temp_file_path)
    except S3Error as e:
        # 如果在MinIO中找不到图片，返回错误
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

