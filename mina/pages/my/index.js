//获取应用实例
var app = getApp();
Page({
    data: {},
    onLoad() {

    },

    
    onShow() {
        this.getInfo();
    },

    //从后台得到会员数据
    getInfo:function(){
      var that = this;
      wx.request({
        url: app.buildUrl("/member/info"),
        header:app.getRequestHeader(),
        success:function(res){
           var resp = res.data;
           if(resp.code != 200){
             app.alert({"content":resp.msg})
             return;
           }
           that.setData({
             user_info:resp.data.info
           })
        }
      })
    }
});