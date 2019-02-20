//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    regFlag:true
  },


  goToIndex:function(){
    wx.switchTab({
      url: '/pages/food/index',
    });
  },


  onLoad:function(){
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    this.checkLogin();
  },


  onShow:function(){
  },


  onReady: function(){
    var that = this;
    setTimeout(function(){
      that.setData({
        remind: ''
      });
    }, 1000);
    wx.onAccelerometerChange(function(res) {
      var angle = -(res.x*30).toFixed(1);
      if(angle>14){ angle=14; }
      else if(angle<-14){ angle=-14; }
      if(that.data.angle !== angle){
        that.setData({
          angle: angle
        });
      }
    });
  },


  checkLogin: function () {
    var that = this;
    wx.login({
      success: function (res) {
        if (!res.code) {
          app.alert({ 'content': '登录失败,请再次点击' });
          return;
        }
        // 使用微信的request方法发送ajax请求
        wx.request({
          url: app.buildUrl('/member/check-reg'),
          header: app.getRequestHeader(),
          method: 'POST',
          data: {code:res.code},
          success: function (res) {
              if(res.data.code!=200){ 
                that.setData({
                  regFlag:false
                })
                return 
              }
          app.setCache('token', res.data.data.token)
              // 接收到以前的登录信息,直接去首页面
              //that.goToIndex();
          }
        });
      }
    })
  },


  login:function(e){
    var that = this;
    if(!e.detail.userInfo){
        app.alert({'content':'登录失败,请再次点击'});
        return;
    }
    //如果获取信息成功,返回数据到后台
    var data = e.detail.userInfo;
    //前端的登录操作
    wx.login({
      success:function(res){
          if(!res.code){
            app.alert({ 'content':'登录失败,请再次点击'});
            return;
          }
          data['code'] = res.code
        // 使用微信的request方法发送ajax请求
          wx.request({
          url: app.buildUrl('/member/login'),
          header: app.getRequestHeader(),
          method: 'POST',
          data: data,
          success: function (res) {
            if(res.data.code!=200){
              app.alert({'content':res.data.msg});
              return;
            }
            app.setCache('token',res.data.data.token)
            that.goToIndex();

          }
        });
      }
    })
    
  }

});