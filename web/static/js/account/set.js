/**
 * Created by tarena on 19-2-19.
 */
/**
 * Created by tarena on 19-2-19.
 */
;
var account_set_ops = {
    init:function () {
        this.eventBind()
    },
    eventBind:function () {
        $('.wrap_account_set .save').click(function () {

            //判断提交按钮上是否有class属性,就不能提交
            var btn_target = $(this);
            if(btn_target.hasClass('disabled')){
                common_ops.alert('正在处理,请不要重复提交!!');
                return;
            }
            var nickname_target = $('.wrap_account_set input[name=nickname]');
            var nickname = nickname_target.val();

            var mobile_target = $('.wrap_account_set input[name=mobile]');
            var mobile = mobile_target.val();

            var email_target = $('.wrap_account_set input[name=email]');
            var email = email_target.val();

            var login_name_target = $('.wrap_account_set input[name=login_name]');
            var login_name = login_name_target.val();

            var login_pwd_target = $('.wrap_account_set input[name=login_pwd]');
            var login_pwd = login_pwd_target.val();


            if(!nickname || nickname.lenth<1){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.tip('请输入符合规范的姓名!',nickname_target);
                return false;
            }



            if(!mobile || mobile.lenth<2){
                common_ops.tip('请输入符合规范的邮箱格式!',mobile_target);
                return false;
            }


            if(!mobile || mobile.lenth<1){
                common_ops.tip('请输入符合规范的姓名!',mobile_target);
                return false;
            }

            if(!email || email.lenth<2){
                common_ops.tip('请输入符合规范的邮箱格式!',email_target);
                return false;
            }

            if(!login_name || login_name.lenth<2){
                common_ops.tip('请输入规范的登录用户名!',login_name_target);
                return false;
            }

             if(!login_pwd || login_pwd.lenth<2){
                common_ops.tip('请输入规范的登录用户名!',login_pwd_target);
                return false;
            }

            var data = {
                nickname:nickname,
                mobile:mobile,
                email:email,
                login_name:login_name,
                login_pwd:login_pwd,
                id:$(".wrap_account_set input[name=id]").val()
            };
            // 给按钮增加一个class属性
            btn_target.addClass('disabled');
            $.ajax({
                url:common_ops.buildUrl('/account/set'),
                type:'POST',
                data:data,
                dataType:'json',
                success:function (res) {
                    btn_target.removeClass('disabled');
                    var callback = null;
                    if(res.code == 200){
                        callback = function(){
                            // 刷新当前页面
                            window.location.href = common_ops.buildUrl('/account/index');
                        }
                    }
                    common_ops.alert(res.msg,callback);
                }
            })


        });
    }
};

$(document).ready(function () {
   account_set_ops.init();
});