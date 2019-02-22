/**
 * Created by tarena on 19-2-19.
 */

;
var food_set_ops = {
    init:function () {
        this.eventBind()
    },
    eventBind:function () {
        $('.wrap_cat_set .save').click(function () {

            //判断提交按钮上是否有class属性,就不能提交
            var btn_target = $(this);
            if(btn_target.hasClass('disabled')){
                common_ops.alert('正在处理,请不要重复提交!!');
                return;
            }
            var name_target = $('.wrap_cat_set input[name=name]');
            var name = name_target.val();

            var weight_target = $('.wrap_cat_set input[name=weight]');
            var weight = weight_target.val();


            if(!name || name.lenth<1){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.tip('请输入符合规范的分类名称!',name_target);
                return false;
            }

            if(!weight || parseInt(weight)<1){
                common_ops.tip('请输入符合规范的权重格式,并且至少大于1',weight_target);
                return false;
            }

            // 为提交按钮增加属性disabled
            btn_target.addClass('disabled');

            var data = {
                name:name,
                weight:weight,
                id:$(".wrap_cat_set input[name=id]").val()
            };

            $.ajax({
                url:common_ops.buildUrl('/food/cat-set'),
                type:'POST',
                data:data,
                dataType:'json',
                success:function (res) {
                    btn_target.removeClass('disabled');
                    var callback = null;
                    if(res.code == 200){
                        callback = function(){
                            // 刷新当前页面
                            window.location.href = common_ops.buildUrl('/food/cat');
                        }
                    }
                    common_ops.alert(res.msg,callback);
                }
            })


        });
    }
};

$(document).ready(function () {
   food_set_ops.init();
});