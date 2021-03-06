var dashboard_index_ops = {
    init: function () {
        this.drawChart();
    },
    drawChart: function () {

        // 下面两个注释的是官网测试案例
        // Highcharts.chart('member_order', {
        //     chart: {
        //         type: 'spline'
        //     },
        //     title: {
        //         text: '两地月平均温度'
        //     },
        //     subtitle: {
        //         text: '数据来源: WorldClimate.com'
        //     },
        //     xAxis: {
        //         categories: ['一月', '二月', '三月', '四月', '五月', '六月',
        //             '七月', '八月', '九月', '十月', '十一月', '十二月']
        //     },
        //     yAxis: {
        //         title: {
        //             text: '温度'
        //         },
        //         labels: {
        //             formatter: function () {
        //                 return this.value + '°';
        //             }
        //         }
        //     },
        //     tooltip: {
        //         crosshairs: true,
        //         shared: true
        //     },
        //     plotOptions: {
        //         spline: {
        //             marker: {
        //                 radius: 4,
        //                 lineColor: '#666666',
        //                 lineWidth: 1
        //             }
        //         }
        //     },
        //     series: [{
        //         name: '东京',
        //         marker: {
        //             symbol: 'square'
        //         },
        //         data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, {
        //             y: 26.5,
        //             marker: {
        //                 symbol: 'url(https://www.highcharts.com/demo/gfx/sun.png)'
        //             }
        //         }, 23.3, 18.3, 13.9, 9.6]
        //     }, {
        //         name: '伦敦',
        //         marker: {
        //             symbol: 'diamond'
        //         },
        //         data: [{
        //             y: 3.9,
        //             marker: {
        //                 symbol: 'url(https://www.highcharts.com/demo/gfx/snow.png)'
        //             }
        //         }, 4.2, 5.7, 8.5, 11.9, 15.2, 17.0, 16.6, 14.2, 10.3, 6.6, 4.8]
        //     }]
        // });

        // 下面的图
        //     $("#finance").highcharts({
        //         chart: {
        //             type: 'spline'
        //         },
        //
        //         xAxis: {
        //             categories: ['一月', '二月', '三月', '四月', '五月', '六月',
        //                 '七月', '八月', '九月', '十月', '十一月', '十二月']
        //         },
        //         series: [{
        //             name: '东京',
        //             data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
        //         }]
        //     // });
        //
        // }

        // 调用charts公共js中美化方法
        charts_ops.setOption();

        // 发送ajax请求到后端获取数据 获取会员和订单总数
        $.ajax({
            url: common_ops.buildUrl("/chart/dashboard"),
            dataType:'json',
            success:function (res) {
                charts_ops.drawLine($("#member_order"),res.data)
            }
        });

         // 发送ajax请求到后端获取数据 获取财务信息
        $.ajax({
            url: common_ops.buildUrl("/chart/finance"),
            dataType:'json',
            success:function (res) {
                charts_ops.drawLine($("#finance"),res.data)
            }
        });

    }
};

$(document).ready(function () {
    dashboard_index_ops.init();
});

