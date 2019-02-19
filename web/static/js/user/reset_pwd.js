/**
 * Created by tarena on 19-2-19.
 */
/**
 * Created by tarena on 19-2-19.
 */
;
var mod_pwd_ops = {
    init:function () {
        this.eventBind()
    },
    eventBind:function () {
        $('#save').click(function () {
            //判断提交按钮上是否有class属性,就不能提交
            var btn_target = $(this);
            if(btn_target.hasClass('disabled')){
                common_ops.alert('正在处理,请不要重复提交!!');
                return;
            }
            //获取老密码和新密码
            var old_password = $('#old_password').val();
            var new_password = $('#new_password').val();


            if(!old_password){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.alert('请输入原始密码!');
                return false;
            }

            if(!new_password || new_password<6){
                // commot_ops.js文件中的tip方法封装的提示函数,两个参数分别为提示字符串和元素节点
                common_ops.alert('请输入不少于6为的新密码!');
                return false;
            }

             // 给按钮增加一个class属性
            btn_target.addClass('disabled');

            var data = {
                old_password:old_password,
                new_password:new_password
            };
            $.ajax({
                url:common_ops.buildUrl('/user/reset-pwd'),
                type:'POST',
                data:data,
                dataType:'json',
                success:function (res) {
                    // 为提交按钮解锁
                    btn_target.removeClass('disabled');
                    var callback = null;
                    if(res.code == 200){
                        callback = function(){
                            // 刷新当前页面
                            window.location.href = window.location.href;
                        }
                    }
                    common_ops.alert(res.msg,callback);
                }
            })

        });
    }
};

$(document).ready(function () {
   mod_pwd_ops.init();
});