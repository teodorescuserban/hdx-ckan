$('#country-drop').change(function(){
      var country = $('#country-drop option:selected').val();
      var country_name = $('#country-drop option:selected').attr('display_name');
      if($('#'+country).length == 0){
        var number_of_groups = $('.group_checked').length;
        //Add country
        $('#selected_groups').append('<span class="filtered pill">'+country_name+' <input id="field-group-'+(number_of_groups)+'" type="checkbox" name="groups__'+(number_of_groups)+'__id" value="'+country+'" checked="checked" class="group_checked"/></span>');
        //Add country for real
        if($('#selected_groups_hidden').length >0){
          $('#select_groups_hidden').append('<input id="'+country+'" type="checkbox" name="groups__'+(number_of_groups)+'__id" value="'+country+'" checked="checked"/>');
        }
      }
    });

    $('#selected_groups').click(function(){
      if(event.target.className == "filtered pill"){
        //Uncheck hidden
        var id = event.target.children.item().value;
        $('#'+id).remove();
        $(event.target).remove();
      }else if(event.target.className == "group_checked"){
        var id = event.target.value;
        $('#'+id).remove();
        $(event.target).parent().remove();
      }
    });

$( "#field-dataset_date, #date_range1, #date_range2").datepicker();
  
$('#field-organizations').change(function(){
      if($(this).val() == ''){
        $('#field-private option[value=False]').attr('selected', true);
        $('#field-private').attr('disabled', true);
      }else{
        $('#field-private').removeAttr('disabled');
      }
});

    $('#onepage_submit, #dataset_edit').click(function(e){	
      if(this.id == 'onepage_submit' && $('.group_checked').length == 0){
        $('#select_country').prepend('<div class="error-explanation alert alert-error" id="error-country"><p>Must select a country first.</p></div>');
        $('html, body').animate({
              scrollTop: $('#select_country').offset().top
            }, 2000);
      }else{
      $('#error-explanation, .error-block, .error-country').remove();
      $('.error').removeClass('error');

      //Add other specifics
      var other = $('#method_other').val();
      //$('input[value="Other"]').val("Other - "+other);
      //https://github.com/OCHA-DAP/hdx-ckan/issues/344
      $('input[value="Other"]').val(other);

      //Create date range
      if($('#date_range1').val()){
	      $('#field-dataset_date').val($('#date_range1').val() +'-'+$('#date_range2').val());
		}
		
      //Remove extra form elements
      $('#method_other, #date_range1, #date_range2').remove();
      

      /*
      //Deactivate button and add loading
      $('#onepage_submit').attr('disabled', 'disabled');
      $('#onepage_submit').html('<img src="/images/ajax-loader-b.gif"> Processing');

      e.preventDefault();
        $.ajax({
          type: 'POST',
          url: $('#dataset_part_1 form').attr('action'),
          data: $('#dataset_part_1 form').serialize()+'&save',
          success: function(data){
            if(data.validation_fail){
              var print_errors = "<ul>";
              for(var p in data['error_summary']){
                print_errors += '<li data-filed-label="'+p+'">'+p+': '+data['error_summary'][p]+'</li>';
              }
              print_errors += '</ul>';
              $('#dataset_part_1 form').prepend('<div class="error-explanation alert alert-error" id="error-explanation"><p>The form contains invalid entries:'+print_errors+'</p></div>');
              for(var e in data['errors']){
                var element = $('#dataset_part_1 #field-'+e);
                if(e=='name'){
                  $('#dataset_part_1 #field-title').parent().parent().addClass('error');
                }
                element.parent().append('<span class="error-block">'+data['errors'][e][0]+'</span>');
                
              }
              $('html, body').animate({
              scrollTop: $('#error-explanation').offset().top
            }, 2000);
            }else{
              //Point the form at correct endpoint
              $('#dataset_part_2 form').attr('action', data['action_url']);
            /*Activate form
            $('#dataset_part_2').parent().children(".overlay").remove();
            $('#dataset_part_2').parent().removeClass('inactive');
            $('html, body').animate({
              scrollTop: $('#dataset_part_2').offset().top
            }, 2000);
              submit_metadata();
            }
          }
        });*/
      $('form').submit();
  }
    });
