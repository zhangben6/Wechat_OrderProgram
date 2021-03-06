//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address: null,
        yun_price: "1.00",
        pay_price: "0.00",
        total_price: "0.00", 
        params: null // 这个参数专门用来接收上级页面传递的参数信息,然后再发送网络请求使用
    },


    onShow: function () {
        var that = this;
        that.getOrderInfo(); 
    },


    onLoad: function (e) {
        var that = this;
        that.setData({
          params:JSON.parse(e.data)
        });
    },

    // 提交订单的操作
    createOrder: function (e) {
        wx.showLoading();
        var that = this;
        var data = {
          type: this.data.params.type,
          goods: JSON.stringify(this.data.params.goods)
        }
        wx.request({
          url: app.buildUrl('/order/create'),
          header: app.getRequestHeader(),
          method: 'POST',
          data: data,
          success: function (res) {
            wx.hideLoading();
            var resp = res.data;
            if (resp.code != 200) {
              app.alert({ 'content': resp.msg })
              return;
            }
            wx.navigateTo({
              url: "/pages/my/order_list"
            });
          }
        });
       
    },


    addressSet: function (e) {
        wx.navigateTo({
          url: "/pages/my/addressSet?id=" + e.currentTarget.dataset.id
        });
    },

    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList"
        });
    },

    // 订单信息的请求
    getOrderInfo:function(){
      var that = this;
      var data = {
        type:this.data.params.type,
        goods:JSON.stringify(this.data.params.goods)
      };

      wx.request({
        url:app.buildUrl('/order/info'),
        header:app.getRequestHeader(),
        method:'POST',
        data:data,
        success:function(res){
            var resp = res.data;
            if(resp.code!=200){
              app.alert({'content':resp.msg})
              return;
            }

              that.setData({
                  goods_list:resp.data.food_list,
                  default_address:resp.data.default_address,
                  yun_price:resp.data.yun_price,
                  pay_price:resp.data.pay_price,
                  total_price:resp.data.total_price,
            })
        }
      });

  }

  
});
