/**
 * Created by RayJowa on 04/05/2016.



function prepareEventHandlers () {

}

window.onload = function () {
    prepareEventHandlers();

};

*/

function selectAgent(agent_id,agent_name){
    $("#id_agent").val(agent_id).change();
    //$("#id_agent option[value=agent_id]").attr('selected','selected');
    $("#id_agent_show").val(agent_name);

};

function openTab(evt, tabName) {
		var i, tabcontent, tablinks;

		tabcontent = document.getElementsByClassName("tabcontent");
		for (i = 0; i < tabcontent.length; i++) {
			tabcontent[i].style.display = "none";
		}

		tablinks = document.getElementsByClassName("tablinks");
		for (i = 0; i < tablinks.length; i++) {
			tablinks[i].className = tablinks[i].className.replace(" active", "");
		}

		document.getElementById(tabName).style.display = "block";
		evt.currentTarget.className += " active"
	};


function showRight(right_id){
	right_id.style.display = "block";
};

function hideRight(right_id){
	right_id.style.display = "none";
};

function resendSms(policy_id, sms_id) {
	console.log(policy_id, sms_id);
	$.ajax({
		url: '/system/ajax/resend_sms/',
		data: {
			'policy_id': policy_id,
			'sms_id': sms_id
		},
		dataType: 'json',
		success: function (data) {
			alert(data.message)
        }
	});
}





$(document).ready(function(){


    var payAuth = $("#pay_auth");
    var payMethod = document.getElementById("id_payment_method");
    var payAuthority = document.getElementById("id_paying_authority");
    var today = new Date();


	try {
		document.getElementById('deps').click();
	}catch(err){

	}

	$("#id_paying_authority, #id_paying_authority_label").hide();

    $("#checkAll").change(function () {
        alert("Fu!");
        $("input:checkbox").prop('checked', $(this).prop("checked"));
    });


    if (payAuth.html() == '(None)') {
        payAuth.hide();
    }

    $('#id_payment_method').change(function(){
        if ($(this).val()=="Stop order"){
            $("#id_paying_authority, #id_paying_authority_label").show();
        } else {
            $("#id_paying_authority, #id_paying_authority_label").hide();
        }
    });



    $('#id_agent_show').keypress(function(){

        q = $(this).val();
        $('#agent_drpdwn').html('&nbsp;').load( $('#id_url').val()+'?q=' + q );

        var pos = $(this).position();
        $('#agent_drpdwn').css('top', (pos.top)+35+ 'px').fadeIn();
        }).blur(function(){
        $('#agent_drpdwn').fadeOut();
		});


   		//add some elements with animate effect
		$(".box").hover(
			function () {
			$(this).find('span.badge').addClass("animated fadeInLeft");
			$(this).find('.ico').addClass("animated fadeIn");
			},
			function () {
			$(this).find('span.badge').removeClass("animated fadeInLeft");
			$(this).find('.ico').removeClass("animated fadeIn");
			}
		);

		//noinspection JSJQueryEfficiency


		$('#dependants_table').on('click', 'tr', function (e) {
			var dep_id = $(this).attr('data-id');
			$('#claim_dependant').val(dep_id);
			$('.sel').removeClass('sel');
			$(this).addClass('sel');

			calculate_claim();

			$('#claim_details').removeAttr('hidden');

        });

		function calculate_claim() {
			$.ajax({
				url:'/system/calculate_hours/',
				method:'POST',
				data: {
					admitted_date:$('#id_admitted_date').val(),
					admitted_time:$('#id_admitted_time').val(),
					discharged_date:$('#id_discharged_date').val(),
					discharged_time:$('#id_discharged_time').val(),
					dependant_id:$('#claim_dependant').val(),
					csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
				},
				success:function (data) {
					$('#id_days').val(data.days);
					$('#id_amount').val(data.claim_amount);
                }
			});

        };

		$('#id_admitted_time, #id_admitted_date, #id_discharged_date, #id_discharged_time').on('blur', function (e) {
			calculate_claim()
        });


       /*
        myInput.change(function() {
            if (myInput.val()) {
              // Everything fine
            inputOpentip.hide();
            }
            else {
              // Oh oh
                inputOpentip.setContent("Please fill out this field.");
                inputOpentip.show();
            }
          });*/



});

