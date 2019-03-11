;
// 后台首页统一封装的画图js
var charts_ops = {
  drawLine:function (target,data) {
       target.highcharts({
            chart: {
                type: 'spline'
            },

            xAxis: {
                categories: data.categories
            },
            series: data.series
        });
  }
};