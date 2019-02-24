//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: true, // loading
        swiperCurrent: 0,
        categories: [],
        
        //对应cat_id,表示菜品的选项
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,

        //搜索框的内容
        searchInput: '',

        //页数相关参数的设置
        p:1,
        processing:false  //true表示页面正在请求中
    },

    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });

        that.setData({
            banners: [
                {
                    "id": 1,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 2,
                    "pic_url": "/images/food.jpg"
                },
                {
                    "id": 3,
                    "pic_url": "/images/food.jpg"
                }
            ],
            categories: [
                // {id: 0, name: "全部"},
                // {id: 1, name: "川菜"},
                // {id: 2, name: "东北菜"},
            ],
            activeCategoryId: 0,
			      goods: [
			                // {
			                //     "id": 1,
			                //     "name": "小鸡炖蘑菇-1",
			                //     "min_price": "15.00",
			                //     "price": "15.00",
			                //     "pic_url": "/images/food.jpg"
			                // },
			                // {
			                //     "id": 2,
			                //     "name": "小鸡炖蘑菇-1",
			                //     "min_price": "15.00",
			                //     "price": "15.00",
			                //     "pic_url": "/images/food.jpg"
			                // },
			                // {
			                //     "id": 3,
			                //     "name": "小鸡炖蘑菇-1",
			                //     "min_price": "15.00",
			                //     "price": "15.00",
			                //     "pic_url": "/images/food.jpg"
			                // },
			                // {
			                //     "id": 4,
			                //     "name": "小鸡炖蘑菇-1",
			                //     "min_price": "15.00",
			                //     "price": "15.00",
			                //     "pic_url": "/images/food.jpg"
			                // }

			    ],
        });

        //加载页面就要获取banner的值和cat分类
        this.getBannerAndCat();
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },

	  listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	  },

	  toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	  },

    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },

    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    
    // 首页分类信息标签绑定的事件函数
    catClick:function(e){
        this.setData({
          activeCategoryId:e.currentTarget.id,
          p:1,
          goods:[],
          loadingMoreHidden:true
        });

        this.getFoodList();
    },

    // onload中自定义的方法(获取轮播图和菜品分类信息)
    getBannerAndCat:function(){
      //定义一个网络请求,通过api接口获得json数据
        var that = this;
        wx.request({
            url:app.buildUrl('/food/index'),
            header:app.getRequestHeader(),
            success:function(res){
                var resp = res.data;
                if(resp.code != 200){
                  app.alert({"content":resp.msg});
                  return;
                }
                // 如果正常接收到数据
                that.setData({
                  // 重新改变Banner的值
                    banners:resp.data.banner_list,
                    categories:resp.data.cat_list
                });

                // 不请求的话,没数据,多尴尬
                that.getFoodList();
            }
        });
    },

    // 首页搜索的事件函数 继而获取菜品列表(向后台传递搜索的字段数据)
    getFoodList:function(){
      //定义一个网络请求,通过api接口获得json数据
      var that = this;

      //判断是否发送请求的条件
      if (that.data.processing){
        return;
      }
      
      if(!that.data.loadingHidden){
          return;
      }

      that.setData({
        processing:true
      })

      // 发送请求的
      wx.request({
        url: app.buildUrl('/food/search'),
        header: app.getRequestHeader(),
        data:{
          cat_id: that.data.activeCategoryId,
          mix_kw: that.data.searchInput,
          p: that.data.p
        },
        success: function (res) {
          var resp = res.data;
          if (resp.code != 200) {
            app.alert({ "content": resp.msg });
            return;
          }
          var goods = resp.data.list;
          that.setData({
            goods:that.data.goods.concat(goods),
            p:that.data.p + 1,
            processing:false
          });
         
          if(resp.data.has_more==0){
              that.setData({
                loadingMoreHidden:false
              });
          }

        }
      });
    },

    // 页面底部的触发函数,分页效果
    onReachBottom:function(){
        var that = this;
        setTimeout(function(){
            that.getFoodList();
        },500);

    }

});
