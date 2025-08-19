import React from "react";
import {Breadcrumb, Empty, Image, Spin, Upload, Divider} from "antd";
import BaseComponent from "@/pages/BaseComponent";
import {Link} from 'umi';
import {getPageTitleByPath} from "@/utils/utils";
import {InboxOutlined} from "@ant-design/icons";
import {getAccessToken} from "@/utils/authority";

export default class index extends BaseComponent {
  state = {
    response: {}
  }

  componentDidMount() {
    //
  }

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
          <a>{getPageTitleByPath('/predict')}</a>
        </Breadcrumb.Item>
      </Breadcrumb>
      <div
        style={{
          background: 'white', padding: 20, margin: "20px 0"
        }}
      >
        <Spin spinning={this.state.loading || false}>
          <Upload.Dragger
            name='file'
            action='/api/image/search'
            headers={{
              Authorization: getAccessToken(),
            }}
            data={{
              limit: 20,
            }}
            onChange={info => {
              this.setStateSimple('loading', true)
              if (info.file.status === 'done') {
                const reader = new FileReader();
                let that = this
                reader.addEventListener("load", function () {
                  that.setStateSimple('preditImage', reader.result)
                }, false);
                reader.readAsDataURL(info.file.originFileObj)
                this.setStateSimple('loading', false)
                this.setStateSimple('response', info.file.response)
              }
            }}
            showUploadList={false}
          >
            <div>
              {this.state.preditImage ?
                <Image
                  style={{
                    padding: 20,
                  }}
                  src={this.state.preditImage}
                  height={300}
                  width={300}
                  preview={false}
                />
                :
                <p className="ant-upload-drag-icon"><InboxOutlined/></p>
              }
            </div>
            <p className="ant-upload-text">支持点击选择文件，或拖动文件到当前区域内</p>
            <p className="ant-upload-hint">
              支持识别jpg,jpeg,png格式的文件，识别结果将出现在下面的方框中
            </p>
          </Upload.Dragger>
        </Spin>
        <Divider/>
        <div>
          <div
            style={{textAlign: 'center'}}
          >
            {this.state.response?.info?.map(value => {
              return <div style={{display: 'inline-block'}} key={value.image_path}>
                <Image
                  style={{
                    padding: 20,
                  }}
                  src={value.image_path}
                  height={300}
                  width={300}
                />
                <br/>
                <span>distance {value.distance.toFixed(2)}</span>
              </div>
            })}
          </div>

          {(!this.state.response.info || this.state.response.info.length === 0) && <Empty/>}
        </div>
      </div>
    </div>
  }

}
