FROM python:3.7

MAINTAINER 1207032539@qq.com

COPY . /root/work

WORKDIR /root/work
# 安装系统依赖
RUN apt-get update -y  \
    && apt install -y libgl1-mesa-glx  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# 安装依赖
RUN pip install -r requirements.txt && rm -rf ~/.cache/pip

# 运行一次 pipeline 以提前下载模型
RUN python -c "import os.path;import towhee;resnet50 = towhee.pipeline('towhee/image-embedding-resnet50');vector = resnet50('/root/work/test.jpg');print(vector)"

EXPOSE 5000

CMD gunicorn -w ${WORKERS:-1} --threads ${THREADS:-2} -b 0.0.0.0:5000 app:app --preload
