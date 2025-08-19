# 上传图片
import datetime
import hashlib
import json
import os
import re
import uuid

import towhee
from flask import request, current_app
from pymilvus import connections, FieldSchema, DataType, CollectionSchema, Collection

import setting
from tool import common
from tool.validate import validate


def __get_milvus_collection():
    if not hasattr(current_app, 'collection'):
        connections.connect(host=setting.MILVUS.get('host'), port=setting.MILVUS.get('port'))

        collection_name = setting.MILVUS.get('collection_name')
        dim = 2048
        default_fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True, description='自增id'),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim, description='特征向量'),
        ]
        default_schema = CollectionSchema(fields=default_fields, description="图片搜索引擎")

        collection = Collection(name=collection_name, schema=default_schema)

        #
        # Create IVF_SQ8 index to the  collection
        default_index = {"index_type": "IVF_SQ8", "params": {"nlist": dim}, "metric_type": "L2"}
        collection.create_index(field_name="vector", index_params=default_index)
        collection.load()
        current_app.collection = collection

    return current_app.collection


def __get_resnet50(filename):
    if not hasattr(current_app, 'resnet50'):
        current_app.resnet50 = towhee.pipeline('towhee/image-embedding-resnet50')
    return current_app.resnet50(os.path.abspath(filename))


def upload():
    files = request.files.getlist('files')
    if len(files) == 0:
        raise Exception('图片文件不能为空')

    dir = 'static/images/' + datetime.datetime.now().strftime('%Y-%m-%d')
    if not os.path.exists(dir):
        os.mkdir(dir)
    res = []
    for f in files:
        ext = re.search(".([a-z|A-Z]*?)$", f.filename).group(1).lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            raise Exception('不支持文件后缀名:' + f.filename)
        filename = dir + '/' + str(uuid.uuid1()) + '.' + ext
        content = f.read()
        md5 = hashlib.md5(content).hexdigest()
        image = common.get_db().table('image').where('md5', md5).first()
        if image is not None:
            res.append({'md5': md5, 'milvus_id': image['milvus_id']})
            continue
        # 新增文件
        with open(filename, 'ab') as save_file:
            save_file.write(content)
        try:
            # 获取特征向量
            vector = __get_resnet50(filename)
            # 插入milvus数据库
            info = __get_milvus_collection().insert([[vector]])
            milvus_id = info.primary_keys[0]
            common.get_db().table('image').insert({
                'milvus_id': milvus_id,
                'image_path': filename,
                'md5': md5,
                'size': os.path.getsize(filename),
            })
            res.append({'md5': md5, 'milvus_id': milvus_id})
        except Exception as e:
            # 数据信息保存不完整则删除保存的文件
            os.remove(filename)
            raise Exception(str(e))

    return common.json_return('上传成功', res)


# 搜索图片
def search():
    field = ['limit', 'nprobe']
    param = common.get_request_param(field)
    file = request.files.get('file')
    if file is None:
        raise Exception('搜索图片不能为空:')
    ext = re.search(".([a-z|A-Z]*?)$", file.filename).group(1).lower()
    if ext not in ['jpg', 'jpeg', 'png']:
        raise Exception('不支持文件后缀名:' + file.filename)
    path = 'static/search/' + str(uuid.uuid1()) + '.' + ext
    file.save(path)
    try:
        # 获取特征向量
        search_vector = __get_resnet50(path)
    except:
        pass
    finally:
        os.remove(path)
    search_params = {"metric_type": "L2", "params": {"nprobe": int(param.get('nprobe', 32))}}
    results = __get_milvus_collection().search(
        data=[search_vector],
        anns_field='vector',
        param=search_params,
        limit=int(param.get('limit', 10)),
        expr=None
    )

    ids = results[0].ids
    distances = results[0].distances
    distances = dict(zip(ids, distances))
    images = common.get_db() \
        .table('image') \
        .where_in('milvus_id', [i for i in ids]) \
        .select('md5', 'milvus_id', 'image_path') \
        .get() \
        .serialize()
    for image in images:
        image['image_path'] = '/' + image['image_path']
        image['distance'] = distances[image['milvus_id']]

    images = sorted(images, key=lambda x: x['distance'])

    return common.json_return('上传成功', images)


# 获取图片列表
def list():
    field = ['search', 'page', 'page_rows']
    param = common.get_request_param(field)

    page = int(param.get('page', 1))
    page_rows = int(param.get('page_rows', 10))

    db = common.get_db().table('image')
    if param.get('search', ''):
        db = db.where(
            common.get_db().query()
                .or_where('milvus_id', '=', param.get("search"))
                .or_where('md5', '=', param.get("search"))
                .or_where('id', '=', param.get("search"))
        )

    data = db.order_by('id', 'desc').paginate(page_rows, page)

    total = data.total
    data = data.to_dict()
    for value in data:
        value['milvus_id'] = str(value['milvus_id'])  # 数字太大前端获取数字会出现偏差，如437222402463105104，显示的是437222402463105100
    res = {
        'list': data,
        'total': total,
    }

    return common.json_return('获取成功', res)


# 删除图片
def delete():
    field = ['ids', ]
    param = common.get_request_param(field)
    validate.checkData(param, {
        'ids|删除项目': 'required|list'
    })

    if len(param['ids']) > 1000:
        raise Exception('单次处理不允许超过一千条')

    images = common.get_db().table('image').where_in('id', param['ids']).get().serialize()
    milvus_ids = [i['milvus_id'] for i in images]
    image_paths = [i['image_path'] for i in images]
    common.get_db().begin_transaction()
    # 删除图片向量
    if milvus_ids:
        expr = 'id in ' + json.dumps(milvus_ids)
        res = __get_milvus_collection().delete(expr)
        # 返回：(insert count: 0, delete count: 1, upsert count: 0, timestamp: 437223393524449286)
    # 删除数据库
    common.get_db().table('image').where_in('id', param['ids']).delete()
    # 删除文件
    for i in image_paths:
        os.remove(i)
    common.get_db().commit()
    return common.json_return('删除成功')
