import React from "react";
import {
  Button, Form, Input, Modal, Table, message, Divider, Popconfirm, Breadcrumb, Image, Avatar, Space, Upload
} from "antd";
import {request_get, request_post} from "@/utils/request_tool";
import BaseComponent from "@/pages/BaseComponent";
import {history, Link} from 'umi';
import {bytesToSize, getPageTitleByPath} from "@/utils/utils";
import {getAccessToken} from "@/utils/authority";

export default class image extends BaseComponent {
  state = {
    param: {
      page: 1, page_rows: 10,
    }, list: [], total: 0, visible: false, temp_data: {}, loading: false, refresh_loading: false, upload_item: {},
  }

  componentDidMount() {
    this.fetch()
  }

  fetch() {
    this.setState({loading: true}, () => {
      request_get('/api/image/list', this.state.param).then((res) => {
        this.setStateSimple('list', res.info.list)
        this.setStateSimple('total', res.info.total)
        this.setStateSimple('loading', false)
      })
    })
  }

  columns = [{
    title: 'ID', dataIndex: 'id',
  }, {
    title: '图片', render: record => {
      return <Image
        src={'/' + record.image_path}
        // height={300}
        width={100}
      />
    }
  }, {
    title: '大小', dataIndex: 'size', render: value => bytesToSize(value)
  }, {
    title: 'md5', dataIndex: 'md5',
  }, {
    title: 'milvus_id', dataIndex: 'milvus_id', render: value => value + ''
  }, {
    title: '创建时间', dataIndex: 'created_at',
  }, {
    title: '操作', render: record => {
      return <div>
        <Popconfirm
          title='您确定要删除吗？'
          onConfirm={() => {
            request_post('/api/image/delete', {ids: [record.id]}).then(response => {
              if (response.code === 200) {
                this.fetch()
              }
            })
          }}
        >
          <a style={{color: 'red'}}>删除</a>
        </Popconfirm>

      </div>
    }
  },]

  render() {
    return <div>
      <Breadcrumb
        style={{
          padding: 20, paddingTop: 0, paddingBottom: 0,
        }}
      >
        <Breadcrumb.Item>
          <Link to="/">{getPageTitleByPath()}</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          {getPageTitleByPath('/image/list')}
        </Breadcrumb.Item>
      </Breadcrumb>
      <div
        style={{
          background: 'white', padding: 20, margin: "20px 0", height: 70
        }}
      >
        <div style={{float: 'left'}}>
          <Upload
            name='files'
            multiple
            disabled={Object.keys(this.state.upload_item).length > 0}
            action='/api/image/upload'
            headers={{
              Authorization: getAccessToken()
            }}
            showUploadList={false}
            onChange={info => {
              // console.log(info.file)
              if (info.file.status === 'done') {
                delete this.state.upload_item[info.file.uid]
                this.setStateSimple('upload_item', this.state.upload_item, () => {
                  if (Object.keys(this.state.upload_item).length === 0) {
                    this.fetch()
                  }
                })
              } else {
                this.state.upload_item[info.file.uid] = info.file.uid
                this.setStateSimple('upload_item', this.state.upload_item)
              }
            }}
            // data={{
            //   label_id: this.state.param.label_id
            // }}
          >
            <Space
              size='middle'
            >
              <Button
                type='primary'
                loading={Object.keys(this.state.upload_item).length > 0}
              >
                上传
              </Button>

              <Button
                onClick={(event) => {
                  event.stopPropagation()
                  if (!this.state.selectedRowKeys || this.state.selectedRowKeys.length === 0) {
                    message.warning('删除选项不能为空')
                    return false
                  }
                  Modal.confirm({
                    title: '删除提示',
                    content: '您确定要删除选中项目吗？',
                    onOk: () => {
                      request_post('/api/image/delete', {ids: this.state.selectedRowKeys}).then(res => {
                        if (res.code === 200) {
                          message.success('删除成功')
                          this.fetch()
                        }
                      })
                    }
                  })
                }}

                // style={{float: "left"}}
                type='danger'
              >
                删除选中
              </Button>
            </Space>
          </Upload>
        </div>

        <Input.Search
          style={{
            width: 500, float: 'right',
          }}
          placeholder='请输入搜索关键字'
          onSearch={value => {
            this.setState({
              param: {
                ...this.state.param, search: value, page: 1,
              }
            }, () => {
              this.fetch()
            })
          }}
        />
      </div>
      <Table
        onChange={(pagination) => {
          this.setState({
            param: {
              ...this.state.param, page: pagination.current, page_rows: pagination.pageSize,
            }
          }, () => {
            this.fetch()
          })
        }}
        pagination={{
          showSizeChanger: true,
          current: this.state.param.page,
          total: this.state.total,
          pageSize: this.state.param.page_rows,
          showTotal: (total) => {
            return <div>总共 {total} 条数据</div>
          }
        }}
        loading={this.state.loading}
        rowKey='id'
        dataSource={this.state.list}
        columns={this.columns}
        rowSelection={{
          onChange: (selectedRowKeys, selectedRows) => {
            this.setStateSimple('selectedRowKeys', selectedRowKeys)
          }
        }}
      />
    </div>
  }

}
