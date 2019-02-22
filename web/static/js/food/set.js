/**
 * Created by tarena on 19-2-22.
 */
;
var food_set_ops = {
    init:function () {
        this.eventBind();
        this.initEditor()
    },
    eventBind:function () {

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