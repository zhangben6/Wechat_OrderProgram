/**
 * Created by tarena on 19-2-22.
 */
;

// 定义iframe中调用父类需要用到的window.error|success 方法
// 切记需要iframe来协助实现无刷新上传
var upload = {
    error: function (msg) {
        common_ops.alert(msg);
    },
    success: function (file_key) {
        if (!file_key) {
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'
                + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

        if ($(".upload_pic_wrap .pic-each").size() > 0) {
            $(".upload_pic_wrap .pic-each").html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        food_set_ops.delete_img();
    }
};

var food_set_ops = {
    init:function () {
        this.eventBind();
        this.initEditor()
    },
    eventBind:function () {

        // 样式 选择的绑定按钮处理函数
        $(".wrap_food_set select[name=cat_id]").select2({
           language:'zh-CN',
            width: '100%'
        });

        // 上传封面功能,监控函数时间
        $(".wrap_food_set .upload_pic_wrap input[name=pic]").change(function () {
            $(".wrap_food_set .upload_pic_wrap").submit();
        });

        //标签选择的按钮处理函数
         $(".wrap_food_set input[name=tags]").tagsInput({
             width: 'auto',
             height:40
        });
    },
    // 编辑器的初始化方法
    initEditor:function () {
        var that = this;
        // 括号里面第二个中括号字符串代表自定义的toolbar工具栏
        that.ue = UE.getEditor('editor',{
            toolbars: [
        [ 'undo', 'redo', '|',
            'bold', 'italic', 'underline', 'strikethrough', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall',  '|','rowspacingtop', 'rowspacingbottom', 'lineheight'],
        [ 'customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
            'directionalityltr', 'directionalityrtl', 'indent', '|',
            'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
            'link', 'unlink'],
        [ 'imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
            'insertimage', 'insertvideo', '|',
            'horizontal', 'spechars','|','inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols' ]

        ],
            // 不设置自动保存
            enableAutoSave:true,
            saveInterval:60000,  //60000秒后保存
            elementPathEnabled:false,
            zIndex:4,
             serverUrl:common_ops.buildUrl(  '/upload/ueditor' )
        });
    }
};

$(document).ready(function () {
   food_set_ops.init();
});