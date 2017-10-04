window.onload = function()
{
	var new_message = document.getElementById("new_message");
	new_message.addEventListener('click', clicked_new_message, false);

	var inbox = document.getElementById("inbox");
        inbox.addEventListener('click', clicked_inbox, false);
	
	var outbox = document.getElementById("outbox");
        outbox.addEventListener('click', clicked_outbox, false);
		
	var logout = document.getElementById("logout");
	logout.addEventListener('click', clicked_logout, false);
	
	$("#dynamic_panel").on('click',"#message_list #single_message #subject",open_message);
	$("#dynamic_panel").on('click',"#message_list #single_message #delete", delete_message);
	$("#dynamic_panel").on('click',"#opened_message #delete", delete_message);
	$("#dynamic_panel").on('click',"#message_list #single_message #read", change_unread);
	
	count_unread();
}
	
function count_unread()
{
	$.ajax({
                        type: "GET",
                        url: "http://edi.iem.pw.edu.pl/makosak/message/count_unread",
                        dataType: "text",
                        success: function(response) {
                                var section = document.getElementById("inbox");
                                section.innerHTML = response;
                        }
                });

}
function delete_message()
{
	var id = $(this).attr("name");
	if(id >= 10)
	{
        	$.ajax({
               		type: "DELETE",
                	url: "http://edi.iem.pw.edu.pl/makosak/message/delete/" + id.toString(),
                	dataType: "text",
                	success: function(response) {
                        	var section = document.getElementById("dynamic_panel");
                        	section.innerHTML = response;
                	}
        	});
	}
	else
	{
		$.ajax({
                type: "GET",
                url: "http://edi.iem.pw.edu.pl/makosak/message/no_delete",
                dataType: "text",
                success: function(response) {
                        var section = document.getElementById("dynamic_panel");
                        section.innerHTML = response;
                }
        });
	}
	count_unread();
}

function change_unread()
{
	var id = $(this).attr("name");
        $.ajax({
                type: "PUT",
                url: "http://edi.iem.pw.edu.pl/makosak/message/change_unread/" + id.toString(),
                dataType: "text",
                success: function(response) {
                        var section = document.getElementById("dynamic_panel");
                        section.innerHTML = response;
                }
        });
	count_unread();

}

function open_message()
{
	var id = $(this).attr("name");
	$.ajax({
		type: "GET",
		url: "http://edi.iem.pw.edu.pl/makosak/message/display/" + id.toString(),
		dataType: "text",
		success: function(response) {
			var section = document.getElementById("dynamic_panel");
			section.innerHTML = response;
		}
	});
}
function clicked_new_message()
{
	$.ajax({
           	type: "GET",
              	url: "http://edi.iem.pw.edu.pl/makosak/message/new_message",
      		dataType: "text",
              	success: function (response) {
			var section = document.getElementById("dynamic_panel");
			section.innerHTML = response;
		}
	});
}
function clicked_inbox()
{
        $.ajax({
                type: "GET",
                url: "http://edi.iem.pw.edu.pl/makosak/message/inbox",
                dataType: "text",
                success: function (response) {
                        var section = document.getElementById("dynamic_panel");
                        section.innerHTML = response;
                }
        });
	count_unread();
}
function clicked_outbox()
{
	 $.ajax({
                type: "GET",
                url: "http://edi.iem.pw.edu.pl/makosak/message/outbox",
                dataType: "text",
                success: function (response) {
                        var section = document.getElementById("dynamic_panel");
                        section.innerHTML = response;
                }
        });
	count_unread();
}
function clicked_logout()
{
	top.location.href="http://edi.iem.pw.edu.pl/makosak/message/logout"
}

