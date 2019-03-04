var app = getApp();
Page({
  data: {
    statusType: ["待付款", "待发货", "待收货", "待评价", "已完成", "已关闭"],
    status: ["-8", "-7", "-6", "-5", "1", "0"],
    currentType: 0,
    tabClass: ["", "", "", "", "", ""]
  },
  statusTap: function(e) {
    var curType = e.currentTarget.dataset.index;
    this.data.currentType = curType;
    this.setData({
      currentType: curType
    });
    this.onShow();
  },
  orderDetail: function(e) {
    wx.navigateTo({
      url: "/pages/my/order_info"
    })
  },
  onLoad: function(options) {
    // 生命周期函数--监听页面加载

  },
  onReady: function() {
    // 生命周期函数--监听页面初次渲染完
  },
  onShow: function() {
    var that = this;
    // that.setData({
    //   order_list: [{
    //     status: -8,
    //     status_desc: "待支付",
    //     date: "2018-07-01 22:30:23",
    //     order_number: "20180701223023001",
    //     note: "记得周六发货",
    //     total_price: "85.00",
    //     goods_list: [{
    //         pic_url: "/images/food.jpg"
    //       },
    //       {
    //         pic_url: "/images/food.jpg"
    //       }
    //     ]
    //   }]
    // });

    //请求后台数据
    this.getPayOrder();
  },

  onHide: function() {
    // 生命周期函数--监听页面隐藏

  },
  onUnload: function() {
    // 生命周期函数--监听页面卸载

  },
  onPullDownRefresh: function() {
    // 页面相关事件处理函数--监听用户下拉动作

  },
  onReachBottom: function() {
    // 页面上拉触底事件的处理函数

  },

  // 从后台取出数据,列表展示
  getPayOrder: function() {
    var that = this;
    // 发送网络请求
    wx.request({
      url: app.buildUrl('/my/order'),
      header: app.getRequestHeader(),
      data: {
        status: that.data.status[that.data.currentType]
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alter({
            'content': resp.msg
          })
          return;
        }
        that.setData({
          order_list: resp.data.pay_order_list
        });

      }
    });
  },

  // 马上付款的事件处理函数
  toPay: function(e) {
    var that = this;
    // 发送网络请求
    wx.request({
      url: app.buildUrl('/order/pay'),
      header: app.getRequestHeader(),
      method: 'POST',
      data: {
        order_sn: e.currentTarget.dataset.id
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alter({
            'content': resp.msg
          })
          return;
        }
        var pay_info = resp.data.pay_info;
        wx.requestPayment({
          timeStamp: pay_info.timeStamp,
          nonceStr: pay_info.nonceStr,
          package: pay_info.package,
          signType: 'MD5',
          paySign: pay_info.paySign,
          success(res) {},
          fail(res) {} 
        })
      }
    });
  }
});