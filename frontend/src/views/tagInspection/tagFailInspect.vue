<template>
<div style="text-align:left;margin:10px 0">
  <a-tabs v-model="activeKey" type="editable-card" @edit="onEdit" hide-add>
    <a-tab-pane v-for="pane in panes" :key="pane.key" :tab="pane.title" :closable="pane.closable">
      <div v-if="pane.key === '0'">
        <!-- <a-select default-value="id" style="width: 100px; margin:0px 10px 15px 0px" @change="handleChange">
          <a-select-option value="id">
            游记编号
          </a-select-option>
          <a-select-option value="content">
            游记内容
          </a-select-option>
          <a-select-option value="position">
            游记地点
          </a-select-option>
          <a-select-option value="owner">
            用户编号
          </a-select-option>
        </a-select>
        <a-input-search placeholder="请输入搜索文本" style="width: 300px; margin:0 5px 0 2px"  @search="onSearch" />
        <a-button style="margin:0 5px 0 50px" type="primary" @click="add">查看</a-button> -->
        <a-button style="margin:0px 10px 15px 0px" type="primary" @click="add">查看</a-button>
        <a-spin :spinning="spinning">
          <a-table :row-selection="rowSelection" :columns="columns" :data-source="pane.data" :pagination="false">
            <a slot="id" slot-scope="text, record" @click="addSingle(record)">{{ text }} </a>
          </a-table>
          <br>
          <a-pagination show-quick-jumper :page-size="1" :total="pageNum" @change="onPageChange" />
        </a-spin>
      </div>
      <div v-else style="margin:10px 0 10px 15px;">
        <a-descriptions title="标签信息" bordered style="word-break: break-all;word-wrap: break-word;">
            <a-descriptions-item label="编号">
              {{data[pane.key-1].id}}
            </a-descriptions-item>
            <a-descriptions-item label="名称">
              {{data[pane.key-1].title}}
            </a-descriptions-item>
            <a-descriptions-item label="创建时间">
              {{data[pane.key-1].createTime}}
            </a-descriptions-item>
            <a-descriptions-item label="创建者编号">
              {{data[pane.key-1].creatorId}}
            </a-descriptions-item>
            <a-descriptions-item label="创建者名称">
              {{data[pane.key-1].creatorName}}
            </a-descriptions-item>
            <a-descriptions-item label="审核不通过原因" :span="3">
              {{data[pane.key-1].forbidden_reason}}
            </a-descriptions-item>
          </a-descriptions>
      </div>

    </a-tab-pane>
  </a-tabs>
  <a-modal
      title="提示"
      :visible="visible"
      :confirm-loading="confirmLoading"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <p>{{ ModalText }}</p>
    </a-modal>
  </div>
</template>
<script>
const columns = [
  {
    title: '标签编号',
    dataIndex: 'id',
    scopedSlots: { customRender: 'id' },
  },
  {
    title: '标签名称',
    dataIndex: 'title',
  },
  {
    title: '创建者编号',
    dataIndex: 'creatorId',
  },
  {
    title: '创建者名称',
    dataIndex: 'creatorName',
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
  },
  {
    title: '不通过原因',
    dataIndex: 'forbidden_reason',
  },
];

export default {
  name:"tagFailInspect",
  data() {
    const panes = [
      { title: '审核不通过', data:[],  key: '0' ,closable: false },
    ];
    return {
      spinning:true,
      data:[],
      searchType: "id",
      columns,
      activeKey: panes[0].key,
      panes,
      selectedRows:[],
      selectedRowKeys:[],
      page: 1,
      pageNum: 1,
      visible: false,
      confirmLoading: false,
      ModalText: '您的登录信息已过期，请重新登录'
    };
  },
  computed:{
    rowSelection() {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: (selectedRowKeys, selectedRows) => {
          console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows);
          this.selectedRows = selectedRows;
          this.selectedRowKeys = selectedRowKeys;
        },
        getCheckboxProps: record => ({
          props: {
            title: record.id,
          },
        }),
      };
    },
  },
  mounted(){
    this.getTags({"page": "1", "forbidden": 1});
  },
  methods: {
    getTags(p) {
      this.spinning = true;
      this.$axios({
        method: "get",
        url: "api/admin/tag/getTagList/",
        params: p,
        headers: {
          Authorization: localStorage.getItem('Authorization')
        },
        data: {},
      }).then((res) => {
        this.data = res.data.results;
        this.pageNum = res.data.pages;
        let key = 1;
        this.data.forEach((item)=>{
          item.key = key + '';
          key = key + 1;
          item.title = item.content;
          item.creatorId = item.user == null ? "-" : item.user.id;
          item.creatorName = item.user == null ? "管理员" : item.user.name;
          item.createTime = item.date;
        })
        this.panes[0].data = this.data;
        this.spinning = false;
      }).catch((error) => {
        if (error.response.status == 403) {
          this.visible = true;
        }
      });
    },
    handleOk() {
      this.ModalText = '该对话框将在2秒后关闭';
      this.confirmLoading = true;
      setTimeout(() => {
        this.visible = false;
        this.confirmLoading = false;
        this.$router.push('/login');
      }, 2000);
    },
    handleCancel() {
      this.visible = false;
    },
    handleChange(value) {
      this.searchType = value;
    },
    onSearch(value){
      let params = {"page": "1", "forbidden": 1};
      params[this.searchType] = value;
      this.getTags(params);
    },
    onPageChange(page) {
      for (let i = 1; i < this.panes.length; i++) {
        this.remove(this.panes[i].key);
      }
      this.panes.splice(1, this.panes.length-1);
      this.selectedRows = [];
      this.selectedRowKeys = [];
      this.getTags({"page": page, "forbidden": 1});
    },
    fail(){
      console.log("fail")
    },
    pass(){
      console.log("pass")
    },
    callback(key) {
      console.log(key);
    },
    onEdit(targetKey, action) {
      this[action](targetKey);
      console.log("targetKey:"+targetKey);
      console.log("action:"+action);
      console.log(this.panes);
    },
    addSingle(record){
      const panes = this.panes;
        let flag = 0;
        let item = record;
        for(let j = 0; j<panes.length;j++){
          if(panes[j].key == item.key){
            console.log("item.key:"+item.key);
            flag = 1;
            break;
          }
        }
        if(flag == 0){
          panes.push({ title: item.id, data:item.data, key: item.key });

        }
         this.activeKey = item.key;
         this.panes = panes;
    },
    add() {
      const panes = this.panes;
      let i = 0;
      this.selectedRows.forEach((item)=>{
        let flag = 0;
        for(let j = 0; j<panes.length;j++){
          if(panes[j].key == item.key){
            console.log("item.key:"+item.key);
            flag = 1;
            break;
          }
        }
        console.log("flag:"+flag);
        if(flag == 0){
          panes.push({ title: item.id, data:item.data, key: item.key });
          i=item.key;
          console.log(i);
          this.activeKey = i;
        }
      })
      this.panes = panes;
    },
    remove(targetKey) {
      let activeKey = this.activeKey;
      let lastIndex;
      this.panes.forEach((pane, i) => {
        if (pane.key === targetKey) {
          lastIndex = i - 1;
        }
      });
      const panes = this.panes.filter(pane => pane.key !== targetKey);
      if (panes.length && activeKey === targetKey) {
        if (lastIndex >= 0) {
          activeKey = panes[lastIndex].key;
        } else {
          activeKey = panes[0].key;
        }
      }
      this.panes = panes;
      this.activeKey = activeKey;
    },
  },
};
</script>