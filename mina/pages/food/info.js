//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../../wxParse/wxParse.js');
// 加载写好的utilts.js文件中的方法
var utils = require('../../utils/util.js')
Page({
  data: {
    autoplay: true,
    interval: 3000,
    duration: 1000,
    swiperCurrent: 0,
    hideShopPopup: true,
    buyNumber: 1,
    buyNumMin: 1,
    buyNumMax: 1,
    canSubmit: false, //  选中时候是否允许加入购物车
    shopCarInfo: {},
    shopType: "addShopCar", //购物类型，加入购物车或立即购买，默认为加入购物车,
    id: 0,
    shopCarNum: 4,
    commentCount: 2
  },
  onLoad: function(e) {
    var that = this;
    // 进入某个页面就要获取id的值
    that.setData({
      id: e.id
    });

    that.setData({
      // "info": {
      //     "id": 1,
      //     "name": "小鸡炖蘑菇",
      //     "summary": '<p>多色可选的马甲</p><p><img src="http://www.timeface.cn/uploads/times/2015/07/071031_f5Viwp.jpg"/></p><p><br/>相当好吃了</p>',
      //     "total_count": 2,
      //     "comment_count": 2,
      //     "stock": 2,
      //     "price": "80.00",
      //     "main_image": "/images/food.jpg",
      //     "pics": [ '/images/food.jpg','/images/food.jpg' ]
      // },
      // buyNumMax:2,
      commentList: [{
          "score": "好评",
          "date": "2017-10-11 10:20:00",
          "content": "非常好吃，一直在他们加购买",
          "user": {
            "avatar_url": "/images/more/logo.png",
            "nick": "angellee 🐰 🐒"
          }
        },
        {
          "score": "好评",
          "date": "2017-10-11 10:20:00",
          "content": "非常好吃，一直在他们加购买",
          "user": {
            "avatar_url": "/images/more/logo.png",
            "nick": "angellee 🐰 🐒"
          }
        }
      ]
    });

    // WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);

  },

  onShow: function() {
    // 请求页面的详情数据
    this.getInfo();
  },

  //通往购物车页面
  goShopCar: function() {
    wx.reLaunch({
      url: "/pages/cart/index"
    });
  },


  toAddShopCar: function() {
    this.setData({
      shopType: "addShopCar"
    });
    this.bindGuiGeTap();
  },

  tobuy: function() {
    this.setData({
      shopType: "tobuy"
    });
    this.bindGuiGeTap();
  },

  // 添加到购物车
  addShopCar: function() {
      var that = this;
      var data = {
        'id':that.data.info.id,
        'number':that.data.buyNumber,
      };
      // 发送网络请求
      wx.request({
        url:app.buildUrl('/cart/set'),
        header:app.getRequestHeader(),
        method:'POST',
        data:data,
        success:function(res){
            var resp = res.data;
            app.alert({'content':resp.msg});

            that.setData({
              hideShopPopup:true
            });
        }
      });
  },

  // 立即购买   传递参数的操作
  buyNow: function() {
    var data = {
      goods:[{
        "id": this.data.info.id,
        "price": this.data.info.price,
        "number": this.data.buyNumber,
      }]
    };

    this.setData({
      hideShopPopup: true
    });
    
    wx.navigateTo({
      url: "/pages/order/index?data=" + JSON.stringify(data)
    });
  },


  /**
   * 规格选择弹出框
   */
  bindGuiGeTap: function() {
    this.setData({
      hideShopPopup: false
    })
  },
  /**
   * 规格选择弹出框隐藏
   */
  closePopupTap: function() {
    this.setData({
      hideShopPopup: true
    })
  },


  numJianTap: function() {
    if (this.data.buyNumber <= this.data.buyNumMin) {
      return;
    }
    var currentNum = this.data.buyNumber;
    currentNum--;
    this.setData({
      buyNumber: currentNum
    });
  },
  numJiaTap: function() {
    if (this.data.buyNumber >= this.data.buyNumMax) {
      return;
    }
    var currentNum = this.data.buyNumber;
    currentNum++;
    this.setData({
      buyNumber: currentNum
    });
  },
  //事件处理函数
  swiperchange: function(e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },

  //得到视频详情数据
  getInfo: function() {
    var that = this;
    wx.request({
      url: app.buildUrl('/food/info'),
      header: app.getRequestHeader(),
      data: {
        id: that.data.id
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({
            "content": resp.msg
          });
          return;
        }

        //请求到后台的数据后渲染到前台页面
        that.setData({
          info: resp.data.info,
          buyNumMax: resp.data.info.stock,
          shopCarNum:resp.data.cart_number
        });

        //此方法渲染页面中的描述summary
        WxParse.wxParse('article', 'html', that.data.info.summary, that, 5);

      }
    });
  },

  //页面的分享功能实现
  onShareAppMessage: function() {
    var that = this;
    return {
      title: that.data.info.name,
      path: '/page/food/info?id=' + that.data.info.id,
      success: function(res) {
        //转发成功

        wx.request({
          url: app.buildUrl('/member/share'),
          header: app.getRequestHeader(),
          method:'POST',
          data: {
            // 把当前页面的url地址发给后台
            url: utils.getCurrentPageUrlWithArgs()
          },
          success:function(res){

          }

        });
      },

      fail: function(res) {
        //转发失败
        return

      }
    }
  }

});