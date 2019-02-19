/**
 * Created by tarena on 19-2-19.
 */
;
var user_edit_ops = {
    init:function () {
        this.eventBind()
    },
    eventBind:function () {
        $('.user_edit_wrap .save').click(function () {

            //判断提交按钮上是否有class属性,就不能提交
            var btn_target = $(this);
            if(btn_target.hasClass('disabled')){
                common_ops.alert('正在处理,请不要重复提交!!');
                return;
            }
            //获取手机号码节点和手机号
            var mobile_target = $('.user_edit_wrap input[name=mobile]');
            var mobile = mobile_target.val();

            var nickname_target = $('.user_edit_wrap input[name=nickname]');
            var nickname = nickname_target.val();

            var email_target = $('.user_edit_wrap input[name=email]');
            var email = email_target.val();

            if(!mobile || mobile.lenth<2){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.tip('请输入符合规范的邮箱格式!',mobile_target);
                return false;
            }

            if(!nickname || nickname.lenth<2){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.tip('请输入符合规范的姓名!',nickname_target);
                return false;
            }

            if(!email || email.lenth<2){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.tip('请输入符合规范的邮箱格式!',email_target);
                return false;
            }
            var data = {
                mobile:mobile,
                nickname:nickname,
                email:email
            };
            // 给按钮增加一个class属性
            btn_target.addClass('disabled');
            $.ajax({
                url:common_ops.buildUrl('/user/edit'),
                type:'POST',
                data:data,
                dataType:'json',
                success:function (res) {
                    btn_target.removeClass('disabled');
                    var callback = null;
                    if(res.code == 200){
                        callback = function(){
                            // 刷新当前页面
                            window.location.href = window.location.href;
                        }
                    }else{
                        callback = function(){
                            // 刷新当前页面
                            window.location.href = window.location.href
                        };
                        common_ops.alert(res.msg,callback);
                        return false
                };
                    common_ops.alert(res.msg,callback);
                }
            })


        });
    }
};

$(document).ready(function () {
   user_edit_ops.init();
});