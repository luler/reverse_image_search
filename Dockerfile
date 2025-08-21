# 使用更轻量的基础镜像
FROM python:3.7-slim

MAINTAINER 1207032539@qq.com

# 设置工作目录
WORKDIR /root/work

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .

# 一次性安装系统依赖和 Python 依赖，减少镜像层数
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# 复制应用代码
COPY . .

# 运行一次 pipeline 以提前下载模型，然后清理缓存
RUN python -c "import os.path;import towhee;resnet50 = towhee.pipeline('towhee/image-embedding-resnet50');vector = resnet50('/root/work/test.jpg');print(vector)" \
    && find /root/.cache -type f -delete 2>/dev/null || true \
    && find /tmp -type f -delete 2>/dev/null || true

EXPOSE 5000

CMD ["sh", "-c", "gunicorn -w ${WORKERS:-1} --threads ${THREADS:-2} -b 0.0.0.0:5000 app:app --preload"]
