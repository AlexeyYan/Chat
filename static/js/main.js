moment.locale('ru')
var cookie_agree = getCookie('cookie_agree');
$(document).ready(function () {
    var msg = {};
    var key = "";
    var id = 0;
    var attach_list = [];
    var ws = new WebSocket("wss://my-chat-socket.herokuapp.com/");
    var dropZone = $('.upload-container');
    var alive = null
    
    if ("WebSocket" in window) {
        websocket = true;
    } else {
        websocket = false;
    }

    if (cookie_agree == undefined) {
        document.getElementById('cookie-agreement').className = 'cookie-agree';
    }
    else {
        var back = getCookie('background');
        if (back != undefined) {
            document.body.style.backgroundImage = back;
        }
        else {
            document.cookie = 'background=' + document.body.style.backgroundImage + ';path=/;max-age=31536e3;';
        }

    }

    $('#cookie-sumbit').on('click', function () {
        document.cookie = "cookie_agree=1;path=/;max-age=31536e3;";
        document.cookie = 'background=' + document.body.style.backgroundImage + ';path=/;max-age=31536e3;';
        document.getElementById('cookie-agreement').className = 'hidden';
    });

    ws.onopen = function () {
        console.log("Was connected!");
        document.getElementById("loginbox").className = "lshow";
        $('#register').on('click', function () {
            document.getElementById("loginbox").className = "hidden";
            document.getElementById("registerbox").className = "rshow";
        });
        
        $('.close-registerbox').on('click', function(){
            document.getElementById("registerbox").className = "hidden";
            document.getElementById("loginbox").className = "lshow";
        });
        $('#registerbutton').on('click', function () {
            if (document.forms["registerbox"]["rname"].value != '' && document.forms["registerbox"]["name"].value != '') {
                msg = JSON.stringify({ event: 'register', name: document.forms["registerbox"]["rname"].value, email: document.forms["registerbox"]["email"].value, passwd: document.forms["registerbox"]["rpasswd"].value, });
                console.log("Register");
                ws.send(msg);
            }
        });
        $('#loginbutton').on('click', function () {
            if (document.forms["loginbox"]["name"].value != '' && document.forms["loginbox"]["passwd"].value != '') {
                msg = JSON.stringify({ event: 'login', name: document.forms["loginbox"]["name"].value, passwd: document.forms["loginbox"]["passwd"].value, });
                console.log("Login");
                ws.send(msg);
            }
        });
    };

    ws.onmessage = function (evt) {
        var event = JSON.parse(evt.data);
        if (event.event == 'message') {
            if (event.author.id == id) {
                $('.messageBox').append('<div><div class="myMessage"><b>' + event.author.name + ':</b>  ' + event.text + '<br>' + attach(event.attachments) + '<p>' + moment(event.timestamp).utcOffset(+6.00).calendar() + '</p></div></div>');
            }
            else {
                $('.messageBox').append('<div><div class="otherMessage"><b>' + event.author.name + ':</b>  ' + event.text + '<br>' + attach(event.attachments) + '<p>' + moment(event.timestamp).utcOffset(+6.00).calendar() + '</p></div></div>');
            }
            $(".messageBox").animate({
                scrollTop: $(".messageBox").get(0).scrollHeight
            }, 100);
            console.log('Received message');
        }
        if (event.event == 'connect') {
            $('.messageBox').append('<div><div class="clear" style="text-align: center;">' + event.user + ' connected!</div></div>');
            $(".messageBox").animate({
                scrollTop: $(".messageBox").get(0).scrollHeight
            }, 100);
        }
        if(event.event == 'disconnect'){
            console.log(event);
            $('.messageBox').append('<div><div class="clear" style="text-align: center;">' + event.user + ' disconnected!</div></div>');
            $(".messageBox").animate({
                scrollTop: $(".messageBox").get(0).scrollHeight
            }, 100);
        }
        if (event.event == 'login'){
            if (event.status == 'true'){
                key = event.key;
                id = event.id;
                document.getElementById("loginbox").className = "hidden";
                alive=setInterval(function () { ws.send(JSON.stringify({ event: 'alive', key: key })); }, 30000);
            }
            if(event.status =='false'){
                document.getElementById("log_error").innerHTML="Ошибка авторизации! Проверьте данные для входа.";
            }
        }

        if (event.event == 'register') {
            if (event.status != "true") {
                document.getElementById("reg_error").innerHTML = event.error;
            }
            else {
                document.getElementById("registerbox").className = "hidden";
                window.location.reload();
            }
        }

        if (event.event == 'messagedump') {
            for (var message in event.messages) {
                var author = event.messages[message].author;
                var attachments = event.messages[message].attachments;
                if (author.id == id) {
                    $('.messageBox').append('<div><div class="myMessage"><b>' + author.name + ':</b>  ' + event.messages[message].text + '<br>' + attach(attachments) + '<p>' + moment(event.messages[message].timestamp).utcOffset(+6.00).calendar() + '</p></div></div>');
                }
                else {
                    $('.messageBox').append('<div><div class="otherMessage"><b>' + author.name + ':</b>  ' + event.messages[message].text + '<br>' + attach(attachments) + '<p>' + moment(event.messages[message].timestamp).utcOffset(+6.00).calendar() + '</p></div></div>');
                }
            }
            $(".messageBox").animate({
                scrollTop: $(".messageBox").get(0).scrollHeight
            }, 100);
        }

        if(event.event == 'attach_response'){
            attach_list=event.files;
            document.getElementById("photo_handler").className = "hidden";
            document.getElementById('upload-image').src='images/upload.png';
        }
    };

    ws.onclose=function(){
        console.log('Connection closed');
        clearInterval(alive);
    }
    //Прикрепление вложения
    dropZone.on('drag dragstart dragend dragover dragenter dragleave drop', function () {
        return false;
    });

    dropZone.on('dragover dragenter', function () {
        dropZone.addClass('dragover');
    });

    dropZone.on('dragleave', function (e) {
        dropZone.removeClass('dragover');
    });

    dropZone.on('drop', function (e) {
        dropZone.removeClass('dragover');
        let files = e.originalEvent.dataTransfer.files;
        document.getElementById('upload-image').src='images/loading.svg'
        sendFiles(files);        
    });

    $('#file-input').change(function () {
        let files = this.files;
        sendFiles(files);
    });

    $('#myMessage').on('keydown', function(event) {
        if($(this).text().length === 300 && event.keyCode != 8) {
            event.preventDefault();
        }
    });
    //Отправка сообщения
    document.onkeyup = function (e) {
        if (e.keyCode == 13 && !e.shiftKey) {
            if ($('#myMessage').text() != '' || attach_list.length!=0) {
                var messag = $('#myMessage').text().replace(/<\/?[^>]+(>|$)/g, "");
                if (messag != '') {
                    msg = JSON.stringify({ event: 'message', message: messag, key: key, attachments: attach_list, });
                    ws.send(msg);
                }
                $('#myMessage').text('');
                attach_list = [];
            }
        }
    };

    $('#sendbutton').on('click', function () {
        if ($('#myMessage').text() != '') {
            var messag = $('#myMessage').text.replace(/<\/?[^>]+(>|$)/g, "");
            if (messag != '' || attach_list.length!=0) {
                msg = JSON.stringify({ event: 'message', message: messag, key: key, attachments: attach_list, });
                ws.send(msg);
                $('#myMessage').text('');
                attach_list = [];
            }
        }
    });

    $(document.body).on('click','.attachment_photo', function(e) {
        document.getElementById('big_picture').className ="big_picture-show";
        document.getElementById('big_picture-img').src = e.currentTarget.attributes.src.value;

    });

    $('.close-big_picture').on('click', function(){
        document.getElementById('big_picture').className ="hidden";
    });

    $('.item-menu').on('click', function () {
        document.getElementById("photo_handler").className = "photoh_show";
    });
    $('.close-upload-container').on('click', function(){
        document.getElementById("photo_handler").className = "hidden";
    });

    ws.onclose = function () {
        console.log("Connection closed...");
        alert("Connection closed...")
    };

    function sendFiles(files) {
        let Data = new FormData();
        $(files).each(function (index, file) {
            console.log(file);
            Data.append('key',key);
            Data.append('files[]', file);
            console.log(Data);
            $.ajax({
                url: "/upload",
                type: "POST",
                data: Data,
                contentType: false,
                processData: false,
            });
        });
    };

    var filetypes={
        'image':[
            'image/png',
            'image/jpeg',
            'image/gif',
            'image/x-icon',
            'image/svg+xml',
            'image/tiff',
            'image/webp'
        ],
        'file':[
            'text/plain',
            'text/css',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/html',
            'application/pdf',
            'application/vnd.ms-powerpoint',
            'application/x-rar-compressed',
            'application/x-zip-compressed',
            'application/rtf',
            'application/zip',
            'application/x-7z-compressed'
        ]
    }

    //Обработка вложений 
    function attach(attachments) {
        if (attachments==null) return '';
        var attachm = '';
        for (var attachment in attachments) {
            if (filetypes['image'].includes(attachments[attachment].type)) {
                attachm += '<img class="attachment_photo" src="' + attachments[attachment].link + '"><br>';
            }
            if (filetypes['file'].includes(attachments[attachment].type)) {
                attachm += '<a href="' + attachments[attachment].link + '">' + attachments[attachment].name + '<img src="images/file_attachment.png"></a><br>';
            }
            
        }
        return attachm;
    }
});	  
function getCookie(name) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));

    return matches ? decodeURIComponent(matches[1]) : undefined;
}